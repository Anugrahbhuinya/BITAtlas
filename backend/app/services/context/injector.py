"""
Context Injector.

Maps an assembled and optimized ContextPackage to the legacy PromptContext model.
This acts as a translation layer, keeping the rest of the prompt builder and LLM services
independent of context pipeline internals.
"""
from __future__ import annotations

import logging
from typing import Optional

from app.schemas.prompt_schema import NavigationContext, PromptContext
from app.services.context.models import ContextPackage

logger = logging.getLogger("context.injector")


class ContextInjector:
    """
    Translates ContextPackage to PromptContext schema.
    
    Ensures backwards compatibility with PromptOrchestrator by populating
    exactly the fields it expects.
    """

    def inject(self, package: ContextPackage, query: str) -> PromptContext:
        """
        Builds a PromptContext from the ContextPackage.

        Args:
            package: Assembled ContextPackage.
            query:   Original user query.

        Returns:
            Populated PromptContext.
        """
        # Extract basic sections as strings
        history_text = package.get_text("conversation")
        rag_text = package.get_text("rag")
        academic_text = package.get_text("workspace")

        # RAG chunk list
        from app.security.sanitizers.ai_guard import sanitize_retrieved_context
        rag_section = package.get_section("rag")
        retrieved_chunks = [sanitize_retrieved_context(item.content) for item in rag_section.items] if rag_section else []

        # System dates
        system_section = package.get_section("system")
        today_val = ""
        if system_section and system_section.items:
            sys_meta = system_section.items[0].metadata
            today_val = sys_meta.get("date", "")
            time_val = sys_meta.get("time", "")
            if today_val and time_val:
                today_val = f"{today_val} {time_val}"

        # Student details
        student_name = "Student"
        department = ""
        semester = ""
        cgpa = ""
        attendance = ""
        
        profile_section = package.get_section("profile")
        if profile_section and profile_section.items:
            prof_meta = profile_section.items[0].metadata
            student_name = prof_meta.get("name", "Student")
            department = prof_meta.get("department", "")
            semester = prof_meta.get("semester", "")
            cgpa = prof_meta.get("cgpa", "")
            attendance = prof_meta.get("attendance", "")

        # Navigation Context model
        navigation_context: Optional[NavigationContext] = None
        if package.navigation_data:
            try:
                navigation_context = NavigationContext(**package.navigation_data)
            except Exception as e:
                logger.error("Failed to parse navigation_data into NavigationContext: %s", e)

        # Assemble PromptContext
        prompt_context = PromptContext(
            question=query,
            context=sanitize_retrieved_context(rag_text),
            history=history_text,
            academic_context=academic_text,
            student_name=student_name,
            department=department,
            semester=semester,
            cgpa=cgpa,
            attendance=attendance,
            today=today_val,
            retrieved_chunks=retrieved_chunks,
            navigation_context=navigation_context,
        )

        logger.info(
            "PromptContext successfully injected. Query length: %d, History length: %d, "
            "RAG chunks: %d, Nav data present: %s",
            len(query),
            len(history_text),
            len(retrieved_chunks),
            navigation_context is not None,
        )
        return prompt_context
