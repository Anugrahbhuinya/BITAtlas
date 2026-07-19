import re
from typing import Dict, List, Any

class SystemPromptBlock:
    def __init__(self, content: str = ""):
        self.content = content
    def render(self) -> str:
        return f"=== SYSTEM ===\n{self.content}" if self.content.strip() else ""

class PersonaBlock:
    def __init__(self, content: str = ""):
        self.content = content
    def render(self) -> str:
        return f"=== PERSONA ===\n{self.content}" if self.content.strip() else ""

class SafetyBlock:
    def __init__(self, content: str = ""):
        self.content = content
    def render(self) -> str:
        return f"=== SAFETY ===\n{self.content}" if self.content.strip() else ""

class ContextBlock:
    def __init__(self):
        self.sub_sections = {
            "CURRENT DATE": "",
            "STUDENT PROFILE": "",
            "VERIFIED NAVIGATION CONTEXT": "",
            "CURRENT CONTEXT": "",
            "RETRIEVED KNOWLEDGE": "",
            "FEW SHOT EXAMPLES": "",
            "CONVERSATION SUMMARY": ""
        }
        self.sub_sections_order = [
            "CURRENT DATE",
            "STUDENT PROFILE",
            "VERIFIED NAVIGATION CONTEXT",
            "CURRENT CONTEXT",
            "RETRIEVED KNOWLEDGE",
            "FEW SHOT EXAMPLES",
            "CONVERSATION SUMMARY"
        ]

    def render(self) -> str:
        parts = []
        for name in self.sub_sections_order:
            val = self.sub_sections.get(name, "").strip()
            if val:
                parts.append(f"=== {name} ===\n{val}")
        return "\n\n".join(parts)

class ToolBlock:
    def __init__(self, content: str = ""):
        self.content = content
    def render(self) -> str:
        return f"=== TOOL ===\n{self.content}" if self.content.strip() else ""

class FormattingBlock:
    def __init__(self, content: str = ""):
        self.content = content
    def render(self) -> str:
        return f"=== OUTPUT FORMAT ===\n{self.content}" if self.content.strip() else ""

class UserQueryBlock:
    def __init__(self, content: str = ""):
        self.content = content
    def render(self) -> str:
        return f"=== USER QUESTION ===\n{self.content}" if self.content.strip() else ""

class PromptBuilder:
    """
    Enforces a strict, standard layout ordering for the prompt sections.
    Implements a modular block system to construct prompts dynamically.
    Empty sections are ignored automatically.
    """
    def __init__(self):
        # Instantiate block sections
        self.system_block = SystemPromptBlock()
        self.persona_block = PersonaBlock()
        self.safety_block = SafetyBlock()
        self.context_block = ContextBlock()
        self.tool_block = ToolBlock()
        self.formatting_block = FormattingBlock()
        self.user_query_block = UserQueryBlock()

        # Registry for extensibility
        self.blocks: Dict[str, Any] = {
            "system": self.system_block,
            "persona": self.persona_block,
            "safety": self.safety_block,
            "context": self.context_block,
            "tool": self.tool_block,
            "formatting": self.formatting_block,
            "user_query": self.user_query_block,
        }
        
        self.block_order: List[str] = [
            "system",
            "persona",
            "safety",
            "context",
            "tool",
            "formatting",
            "user_query"
        ]

        # For backward compatibility
        self.sections_content: Dict[str, str] = {}
        self.sections_order: List[str] = [
            "SYSTEM",
            "PERSONA",
            "SAFETY",
            "CURRENT DATE",
            "STUDENT PROFILE",
            "VERIFIED NAVIGATION CONTEXT",
            "CURRENT CONTEXT",
            "RETRIEVED KNOWLEDGE",
            "FEW SHOT EXAMPLES",
            "TOOL",
            "OUTPUT FORMAT",
            "USER QUESTION",
            "CONVERSATION SUMMARY"
        ]

    def register_block(self, key: str, block: Any, after_block: str | None = None) -> 'PromptBuilder':
        """
        Dynamically registers a new custom block section for future extensibility.
        """
        key_lower = key.lower()
        self.blocks[key_lower] = block
        if key_lower not in self.block_order:
            if after_block and after_block.lower() in self.block_order:
                idx = self.block_order.index(after_block.lower())
                self.block_order.insert(idx + 1, key_lower)
            else:
                self.block_order.append(key_lower)
        
        # Keep backward compatibility order updated if name matches uppercase
        name_upper = key.upper()
        if name_upper not in self.sections_order:
            self.sections_order.append(name_upper)
            
        return self

    def set_verified_navigation_context(self, content: str) -> 'PromptBuilder':
        self.context_block.sub_sections["VERIFIED NAVIGATION CONTEXT"] = content
        self.sections_content["VERIFIED NAVIGATION CONTEXT"] = content
        return self

    def set_system(self, content: str) -> 'PromptBuilder':
        self.system_block.content = content
        self.sections_content["SYSTEM"] = content
        return self

    def set_persona(self, content: str) -> 'PromptBuilder':
        self.persona_block.content = content
        self.sections_content["PERSONA"] = content
        return self

    def set_safety(self, content: str) -> 'PromptBuilder':
        self.safety_block.content = content
        self.sections_content["SAFETY"] = content
        return self

    def set_current_date(self, content: str) -> 'PromptBuilder':
        self.context_block.sub_sections["CURRENT DATE"] = content
        self.sections_content["CURRENT DATE"] = content
        return self

    def set_student_profile(self, content: str) -> 'PromptBuilder':
        self.context_block.sub_sections["STUDENT PROFILE"] = content
        self.sections_content["STUDENT PROFILE"] = content
        return self

    def set_conversation_summary(self, content: str) -> 'PromptBuilder':
        self.context_block.sub_sections["CONVERSATION SUMMARY"] = content
        self.sections_content["CONVERSATION SUMMARY"] = content
        return self

    def set_current_context(self, content: str) -> 'PromptBuilder':
        self.context_block.sub_sections["CURRENT CONTEXT"] = content
        self.sections_content["CURRENT CONTEXT"] = content
        return self

    def set_retrieved_knowledge(self, content: str) -> 'PromptBuilder':
        self.context_block.sub_sections["RETRIEVED KNOWLEDGE"] = content
        self.sections_content["RETRIEVED KNOWLEDGE"] = content
        return self

    def set_few_shot_examples(self, content: str) -> 'PromptBuilder':
        self.context_block.sub_sections["FEW SHOT EXAMPLES"] = content
        self.sections_content["FEW SHOT EXAMPLES"] = content
        return self

    def set_tool(self, content: str) -> 'PromptBuilder':
        self.tool_block.content = content
        self.sections_content["TOOL"] = content
        return self

    def set_output_format(self, content: str) -> 'PromptBuilder':
        self.formatting_block.content = content
        self.sections_content["OUTPUT FORMAT"] = content
        return self

    def set_user_question(self, content: str) -> 'PromptBuilder':
        self.user_query_block.content = content
        self.sections_content["USER QUESTION"] = content
        return self

    def set_section(self, section_name: str, content: str) -> 'PromptBuilder':
        """
        Dynamically sets a section content by string name.
        """
        name_upper = section_name.upper()
        self.sections_content[name_upper] = content
        
        # Route the value to the appropriate block internally
        if name_upper == "SYSTEM":
            self.system_block.content = content
        elif name_upper == "PERSONA":
            self.persona_block.content = content
        elif name_upper == "SAFETY":
            self.safety_block.content = content
        elif name_upper == "TOOL":
            self.tool_block.content = content
        elif name_upper == "OUTPUT FORMAT":
            self.formatting_block.content = content
        elif name_upper == "USER QUESTION":
            self.user_query_block.content = content
        elif name_upper in self.context_block.sub_sections:
            self.context_block.sub_sections[name_upper] = content
        return self

    def get_sections(self) -> Dict[str, str]:
        """
        Returns a dictionary of all set sections.
        """
        # Ensure dict is synchronized with active block contents
        sections = {}
        if self.system_block.content:
            sections["SYSTEM"] = self.system_block.content
        if self.persona_block.content:
            sections["PERSONA"] = self.persona_block.content
        if self.safety_block.content:
            sections["SAFETY"] = self.safety_block.content
        for k, v in self.context_block.sub_sections.items():
            if v:
                sections[k] = v
        if self.tool_block.content:
            sections["TOOL"] = self.tool_block.content
        if self.formatting_block.content:
            sections["OUTPUT FORMAT"] = self.formatting_block.content
        if self.user_query_block.content:
            sections["USER QUESTION"] = self.user_query_block.content
            
        # Dynamically include any custom registered blocks
        for key, block in self.blocks.items():
            if key not in ["system", "persona", "safety", "context", "tool", "formatting", "user_query"]:
                val = getattr(block, "content", "")
                if val:
                    sections[key.upper()] = val
                    
        self.sections_content = sections
        return self.sections_content

    def optimize(self) -> None:
        # 1. Deduplicate System Instructions
        if self.system_block.content:
            content = self.system_block.content
            # Remove ROLE block (redundant with Persona)
            content = re.sub(r"(?i)\bROLE:\s*\n.*?(?=\n\n|\n[A-Z\s]{4,}:)", "", content, flags=re.DOTALL)
            # Remove FORMATTING INSTRUCTIONS (redundant with OUTPUT FORMAT)
            content = re.sub(r"(?i)\bFORMATTING INSTRUCTIONS:\s*\n.*$", "", content, flags=re.DOTALL)
            self.system_block.content = content.strip()
            
        # 2. Deduplicate rules/constraints across SYSTEM and SAFETY
        if self.system_block.content and self.safety_block.content:
            system_rules_lower = self.system_block.content.lower()
            safety_lines = self.safety_block.content.splitlines()
            cleaned_safety_lines = []
            
            for line in safety_lines:
                cleaned = line.strip()
                # Check for numbered/bullet rules
                rule_match = re.match(r"^(\d+[\.\)]|[a-zA-Z][\.\)]|-|\*)\s+(.*)$", cleaned)
                if rule_match:
                    rule_text = rule_match.group(2).strip()
                    rule_lower = rule_text.lower()
                    
                    # Check if this rule is semantically already in system_block
                    is_dup = False
                    if "could not find" in rule_lower or "information is not" in rule_lower or "unavailable" in rule_lower:
                        if "could not find" in system_rules_lower or "unavailable" in system_rules_lower:
                            is_dup = True
                    elif "fabricate" in rule_lower or "invent" in rule_lower or "speculate" in rule_lower:
                        if "fabricate" in system_rules_lower or "invent" in system_rules_lower or "speculate" in system_rules_lower:
                            is_dup = True
                            
                    if is_dup:
                        continue
                cleaned_safety_lines.append(line)
            self.safety_block.content = "\n".join(cleaned_safety_lines).strip()
            
        # 3. Deduplicate RETRIEVED KNOWLEDGE context
        retrieved = self.context_block.sub_sections.get("RETRIEVED KNOWLEDGE", "")
        if retrieved:
            optimized_retrieved = deduplicate_context(retrieved)
            self.context_block.sub_sections["RETRIEVED KNOWLEDGE"] = optimized_retrieved
            self.sections_content["RETRIEVED KNOWLEDGE"] = optimized_retrieved
            
        # Synchronize backward compatibility content dict
        if self.system_block.content:
            self.sections_content["SYSTEM"] = self.system_block.content
        if self.safety_block.content:
            self.sections_content["SAFETY"] = self.safety_block.content

    def build(self) -> str:
        """
        Assembles all populated prompt sections separated by clear visual markers.
        """
        self.optimize()
        assembled_parts = []
        for key in self.block_order:
            block = self.blocks.get(key)
            if block:
                rendered = block.render().strip()
                if rendered:
                    assembled_parts.append(rendered)
        
        return "\n\n".join(assembled_parts)


def deduplicate_context(text: str) -> str:
    if not text:
        return ""
        
    paragraphs = text.split("\n\n")
    seen_paragraphs = set()
    unique_paragraphs = []
    
    for para in paragraphs:
        para_clean = " ".join(para.lower().split())
        if not para_clean:
            continue
            
        # Avoid duplicate paragraphs
        if para_clean in seen_paragraphs:
            continue
            
        # Check if this paragraph is a substring of an already seen paragraph
        # or if any seen paragraph is a substring of this paragraph (replace with the longer one)
        is_sub = False
        for seen in list(seen_paragraphs):
            if para_clean in seen:
                is_sub = True
                break
            elif seen in para_clean:
                # The new paragraph is longer and contains the old one.
                # Remove the old one from unique_paragraphs and seen_paragraphs.
                seen_paragraphs.remove(seen)
                # find and remove from unique_paragraphs
                for i, p in enumerate(unique_paragraphs):
                    if " ".join(p.lower().split()) == seen:
                        unique_paragraphs.pop(i)
                        break
                break
                
        if is_sub:
            continue
            
        # Deduplicate sentences within the paragraph
        sentences = re.split(r'(?<=[.!?])\s+', para)
        seen_sentences = set()
        unique_sentences = []
        for sent in sentences:
            sent_clean = " ".join(sent.lower().split())
            if not sent_clean:
                continue
            if sent_clean not in seen_sentences:
                # Check for substring overlap
                is_sent_sub = False
                for seen_s in list(seen_sentences):
                    if sent_clean in seen_s:
                        is_sent_sub = True
                        break
                    elif seen_s in sent_clean:
                        seen_sentences.remove(seen_s)
                        for idx, s in enumerate(unique_sentences):
                            if " ".join(s.lower().split()) == seen_s:
                                unique_sentences.pop(idx)
                                break
                        break
                if not is_sent_sub:
                    seen_sentences.add(sent_clean)
                    unique_sentences.append(sent)
                    
        cleaned_para = " ".join(unique_sentences).strip()
        if cleaned_para:
            seen_paragraphs.add(para_clean)
            unique_paragraphs.append(cleaned_para)
            
    return "\n\n".join(unique_paragraphs)

