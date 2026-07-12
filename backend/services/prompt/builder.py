from typing import Dict, List

class PromptBuilder:
    """
    Enforces a strict, standard layout ordering for the prompt sections.
    Implements a classic Builder pattern to construct prompts dynamically.
    Empty sections are ignored automatically.
    """
    def __init__(self):
        self.sections_order: List[str] = [
            "SYSTEM",
            "PERSONA",
            "CURRENT DATE",
            "STUDENT PROFILE",
            "VERIFIED NAVIGATION CONTEXT",
            "CURRENT CONTEXT",
            "RETRIEVED KNOWLEDGE",
            "FEW SHOT EXAMPLES",
            "OUTPUT FORMAT",
            "USER QUESTION",
            "CONVERSATION SUMMARY"
        ]
        self.sections_content: Dict[str, str] = {}

    def set_verified_navigation_context(self, content: str) -> 'PromptBuilder':
        self.sections_content["VERIFIED NAVIGATION CONTEXT"] = content
        return self

    def set_system(self, content: str) -> 'PromptBuilder':
        self.sections_content["SYSTEM"] = content
        return self

    def set_persona(self, content: str) -> 'PromptBuilder':
        self.sections_content["PERSONA"] = content
        return self

    def set_current_date(self, content: str) -> 'PromptBuilder':
        self.sections_content["CURRENT DATE"] = content
        return self

    def set_student_profile(self, content: str) -> 'PromptBuilder':
        self.sections_content["STUDENT PROFILE"] = content
        return self

    def set_conversation_summary(self, content: str) -> 'PromptBuilder':
        self.sections_content["CONVERSATION SUMMARY"] = content
        return self

    def set_current_context(self, content: str) -> 'PromptBuilder':
        self.sections_content["CURRENT CONTEXT"] = content
        return self

    def set_retrieved_knowledge(self, content: str) -> 'PromptBuilder':
        self.sections_content["RETRIEVED KNOWLEDGE"] = content
        return self

    def set_few_shot_examples(self, content: str) -> 'PromptBuilder':
        self.sections_content["FEW SHOT EXAMPLES"] = content
        return self

    def set_output_format(self, content: str) -> 'PromptBuilder':
        self.sections_content["OUTPUT FORMAT"] = content
        return self

    def set_user_question(self, content: str) -> 'PromptBuilder':
        self.sections_content["USER QUESTION"] = content
        return self

    def set_section(self, section_name: str, content: str) -> 'PromptBuilder':
        """
        Dynamically sets a section content by string name.
        """
        name_upper = section_name.upper()
        if name_upper in self.sections_order:
            self.sections_content[name_upper] = content
        return self

    def get_sections(self) -> Dict[str, str]:
        """
        Returns a dictionary of all set sections.
        """
        return self.sections_content

    def build(self) -> str:
        """
        Assembles all populated prompt sections separated by clear visual markers.
        """
        assembled_parts = []
        for name in self.sections_order:
            content = self.sections_content.get(name, "").strip()
            if content:
                # Include a clear visual boundary for each section
                assembled_parts.append(f"=== {name} ===\n{content}")
        
        return "\n\n".join(assembled_parts)
