import logging
from datetime import datetime
from typing import Dict, Any

from app.schemas.prompt_schema import PromptContext, PromptMetadata, PromptSchema, PromptValidationResult
from app.services.ai.prompt.templates import TemplateLoader
from app.services.ai.prompt.personas import PersonaManager
from app.services.ai.prompt.variables import VariableEngine
from app.services.ai.prompt.examples import FewShotEngine
from app.services.ai.prompt.hallucination import HallucinationGuard
from app.services.ai.prompt.formatter import ResponseFormatter
from app.services.ai.prompt.validator import PromptValidator
from app.services.ai.prompt.compression import PromptCompressor
from app.services.ai.prompt.builder import PromptBuilder
from app.services.ai.prompt.selector import PromptSelector

logger = logging.getLogger("prompt_orchestrator")

class PromptOrchestrator:
    """
    Coordinates and executes the multi-stage prompt assembly pipeline.
    Uses the Builder pattern to construct prompts section-by-section.
    """
    def __init__(self, templates_base_dirs=None):
        self.selector = PromptSelector()
        self.template_loader = TemplateLoader(base_dirs=templates_base_dirs)
        self.persona_manager = PersonaManager()
        self.variable_engine = VariableEngine()
        self.few_shot_engine = FewShotEngine()
        self.hallucination_guard = HallucinationGuard()
        self.response_formatter = ResponseFormatter()
        self.validator = PromptValidator()
        self.compressor = PromptCompressor()

    def assemble_prompt(self, context: PromptContext, metadata: PromptMetadata) -> PromptSchema:
        """
        Executes the 14-stage prompt orchestration pipeline:
        1. Receive User Query & 2. Intent (via context/metadata)
        3. Load Persona
        4. Select Prompt Template
        5. Inject Variables
        6. Inject Student Context
        7. Inject Conversation Summary
        8. Inject Retrieved RAG Context
        9. Inject Few-shot Examples
        10. Inject Hallucination Rules
        11. Inject Output Formatting Rules
        12. Validate Prompt
        13. Compress Prompt
        14. Return Final Prompt Schema
        """
        logger.info(f"Orchestrating prompt assembly. Intent='{metadata.intent}', Version='{metadata.version}'")

        # --- Stage 3: Load Persona ---
        persona_name, template_name, few_shot_limit = self.selector.select_config(metadata.intent)
        # Override persona if specified in metadata config
        if metadata.persona and metadata.persona != "bit_mesra_assistant":
            persona_name = metadata.persona
        persona_content = self.persona_manager.get_persona_section(persona_name)

        # --- Stage 4: Select Prompt Template ---
        template_text = self.template_loader.load_template(template_name, metadata.version)

        # --- Stage 5: Prepare and Inject Variables ---
        context_vars = {
            "student_name": context.student_name,
            "department": context.department,
            "semester": context.semester,
            "cgpa": context.cgpa,
            "attendance": context.attendance,
            "today": context.today or datetime.now().strftime("%Y-%m-%d"),
            "conversation_summary": context.conversation_summary or context.history or "",
            "retrieved_context": context.context or "",
            "user_question": context.question
        }
        # Merge custom variables if provided
        if context.additional_variables:
            context_vars.update(context.additional_variables)

        # Inject variables into template text
        system_instructions = self.variable_engine.inject_variables(template_text, context_vars)

        # --- Stage 6: Inject Student Context / Profile ---
        student_profile_lines = []
        if context.student_name:
            student_profile_lines.append(f"Name: {context.student_name}")
        if context.department:
            student_profile_lines.append(f"Department: {context.department}")
        if context.semester:
            student_profile_lines.append(f"Semester: {context.semester}")
        if context.cgpa:
            student_profile_lines.append(f"CGPA: {context.cgpa}")
        if context.attendance:
            student_profile_lines.append(f"Attendance Details:\n{context.attendance}")
        student_profile = "\n".join(student_profile_lines)

        # --- Stage 7: Inject Conversation Summary ---
        conversation_summary = context.history or ""

        # --- Stage 8: Inject Retrieved RAG Context ---
        retrieved_knowledge = context.context or ""
        if not retrieved_knowledge and context.retrieved_chunks:
            retrieved_knowledge = "\n\n".join(context.retrieved_chunks)

        # --- Stage 9: Inject Few-shot Examples ---
        few_shot = self.few_shot_engine.get_examples(metadata.intent, limit=few_shot_limit)

        # --- Stage 10: Inject Hallucination Rules ---
        hallucination_rules = ""
        if metadata.hallucination_guard_enabled:
            hallucination_rules = self.hallucination_guard.get_guard_instructions()

        # Combine system instructions and hallucination rules in the system section
        if hallucination_rules:
            system_instructions = system_instructions + "\n\n" + hallucination_rules

        # --- Stage 11: Inject Output Formatting Rules ---
        output_format = self.response_formatter.get_formatting_instructions(metadata.intent)

        # Structured navigation injection (ISSUE 6)
        verified_nav_str = ""
        if context.navigation_context:
            nav = context.navigation_context
            directions_str = "\n".join(f"- {d}" for d in nav.directions)
            landmarks_str = ", ".join(nav.landmarks) if nav.landmarks else "None"
            facilities_str = ", ".join(nav.nearby_facilities) if nav.nearby_facilities else "None"
            
            verified_nav_str = f"""Source: {nav.source or 'None'}
Destination: {nav.destination}
Distance: {nav.walking_distance} meters
Estimated Time: {nav.estimated_time} minutes
Directions:
{directions_str}
Landmarks: {landmarks_str}
Nearby Facilities: {facilities_str}"""

        # Assemble prompt sections using reusable PromptBuilder
        builder = PromptBuilder()
        builder.set_system(system_instructions)
        builder.set_persona(persona_content)
        builder.set_current_date(context_vars["today"])
        builder.set_student_profile(student_profile)
        if verified_nav_str:
            builder.set_verified_navigation_context(verified_nav_str)
        builder.set_conversation_summary(conversation_summary)
        builder.set_current_context(context.academic_context or "")
        builder.set_retrieved_knowledge(retrieved_knowledge)
        builder.set_few_shot_examples(few_shot)
        builder.set_output_format(output_format)
        builder.set_user_question(context.question)

        # --- Stage 12: Validate Raw Assembled Prompt ---
        raw_prompt = builder.build()
        original_length = len(raw_prompt)

        final_prompt = raw_prompt
        final_length = original_length
        compression_ratio = 1.0

        # --- Stage 13: Compress Prompt (if enabled) ---
        if metadata.compression_enabled:
            raw_sections = builder.get_sections()
            compressed_sections = self.compressor.compress_sections(raw_sections)
            
            # Reassemble using the compressed parts
            compressed_builder = PromptBuilder()
            for name, content in compressed_sections.items():
                compressed_builder.set_section(name, content)
            
            final_prompt = compressed_builder.build()
            final_length = len(final_prompt)
            if original_length > 0:
                compression_ratio = final_length / original_length

        # Run validator on the final prompt
        validation_result = self.validator.validate_prompt(
            final_prompt=final_prompt,
            sections=builder.get_sections(),
            template=template_text,
            question=context.question
        )

        # Print detailed pipeline execution logging as requested
        vars_injected = sum(1 for k, v in context_vars.items() if v)
        has_history = "Included" if conversation_summary else "Excluded"
        has_student = "Included" if student_profile else "Unavailable"
        chunks_count = len(context.retrieved_chunks) if context.retrieved_chunks else (1 if context.context else 0)
        few_shot_count = few_shot_limit if few_shot else 0
        hallucination_status = "Applied" if metadata.hallucination_guard_enabled else "Disabled"
        formatter_status = "Applied" if output_format else "Disabled"
        validator_status = "Passed" if validation_result.is_valid else f"Failed ({len(validation_result.errors)} errors)"
        compression_status = "Completed" if metadata.compression_enabled else "Disabled"
        estimated_tokens = final_length // 4

        print("\n================================================")
        print("PROMPT PIPELINE")
        print("===============")
        print("\nPrompt Pipeline Enabled\n")
        print(f"Intent:\n{metadata.intent}\n")
        print(f"Template:\n{template_name}\n")
        print(f"Persona:\n{persona_name}\n")
        print(f"Variables Injected:\n{vars_injected}\n")
        print(f"Conversation Summary:\n{has_history}\n")
        print(f"Student Context:\n{has_student}\n")
        print(f"Retrieved Context:\n{chunks_count} chunks\n")
        print(f"Few-shot Examples:\n{few_shot_count}\n")
        print(f"Hallucination Guard:\n{hallucination_status}\n")
        print(f"Response Formatter:\n{formatter_status}\n")
        print(f"Prompt Validator:\n{validator_status}\n")
        print(f"Prompt Compression:\n{compression_status}\n")
        print(f"Final Prompt Tokens:\n{estimated_tokens}\n")
        print("Calling Gemini...\n")

        if metadata.intent == "navigation":
            print("==================================================")
            print("NAVIGATION PROMPT")
            print("==================================================")
            print(final_prompt)
            print("==================================================\n")
        else:
            print("================================================")
            print("FINAL PROMPT")
            print("============")
            print(final_prompt)
            print("================================================\n")

        # --- Stage 14: Return Assembled PromptSchema ---
        return PromptSchema(
            final_prompt=final_prompt,
            context=context,
            metadata=metadata,
            validation=validation_result,
            original_length=original_length,
            final_length=final_length,
            compression_ratio=compression_ratio
        )
