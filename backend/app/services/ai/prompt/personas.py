from typing import Dict, List, Optional
from app.core.prompt_config import PERSONAS_CONFIG, DEFAULT_PERSONA

class Persona:
    """
    Represents an assistant persona with traits and specific behavioral rules.
    """
    def __init__(self, name: str, characteristics: List[str], extra_instructions: str = ""):
        self.name = name
        self.characteristics = characteristics
        self.extra_instructions = extra_instructions

    def to_prompt_section(self) -> str:
        characteristics_str = "\n".join(f"- {c}" for c in self.characteristics)
        
        # Standardize persona foundation to avoid drift (Requirement 3)
        base_persona = (
            "You are BITAtlas, the official AI-powered campus assistant for Birla Institute of Technology, Mesra. "
            "You must consistently maintain this identity throughout the conversation. Under no circumstances should you deviate "
            "from this persona, act as a general-purpose LLM, or adopt another identity."
        )
        
        section = f"{base_persona}\n\nActive Persona Mode: {self.name}\nTraits:\n{characteristics_str}"
        if self.extra_instructions:
            section += f"\n\nSpecial Persona Guidelines:\n{self.extra_instructions}"
        return section

class PersonaManager:
    """
    Manages multiple personas for BITAtlas.
    Supports registration and lookup of custom personas.
    """
    def __init__(self):
        self.personas: Dict[str, Persona] = {}
        self._register_default_personas()

    def _register_default_personas(self):
        # Register the default assistant personas from configuration file
        for name, config in PERSONAS_CONFIG.items():
            self.register_persona(
                name=name,
                characteristics=config["characteristics"],
                extra_instructions=config.get("extra_instructions", ""),
                display_name=config.get("display_name")
            )

    def register_persona(self, name: str, characteristics: List[str], extra_instructions: str = "", display_name: Optional[str] = None):
        """
        Registers a new persona.
        """
        self.personas[name] = Persona(
            name=display_name or name,
            characteristics=characteristics,
            extra_instructions=extra_instructions
        )

    def get_persona_section(self, name: str = DEFAULT_PERSONA) -> str:
        """
        Retrieves the formatted prompt section for a given persona name.
        Defaults to the main BITAtlas Assistant if the persona name is invalid.
        """
        persona = self.personas.get(name) or self.personas.get(DEFAULT_PERSONA)
        if persona:
            return persona.to_prompt_section()
        return ""
