import re
from typing import Dict, List, Set
from app.core.config import MAX_PROMPT_SIZE
from app.services.ai.prompt.builder import deduplicate_context

class PromptCompressor:
    """
    Compresses prompt text by removing duplicate lines, redundant RAG documents,
    overlapping memory entries, and excessive whitespace.
    """
    def __init__(self):
        pass

    def compress_sections(self, sections: Dict[str, str]) -> Dict[str, str]:
        """
        Compresses each section individually before prompt assembly.
        """
        compressed = {}
        for section_name, content in sections.items():
            if not content:
                compressed[section_name] = ""
                continue

            # Standard cleanup
            cleaned = self.clean_whitespace(content)

            # Target specific sections for compression
            if section_name == "RETRIEVED KNOWLEDGE":
                cleaned = self.deduplicate_rag_chunks(cleaned)
            elif section_name == "CONVERSATION SUMMARY" or section_name == "CURRENT CONTEXT":
                cleaned = self.deduplicate_lines(cleaned)
            elif section_name in ["SYSTEM", "SAFETY"]:
                cleaned = self.deduplicate_system_rules(cleaned)

            compressed[section_name] = cleaned

        # Enforce budget limits
        compressed = self.enforce_budget(compressed, MAX_PROMPT_SIZE)

        return compressed

    def enforce_budget(self, sections: Dict[str, str], max_size: int) -> Dict[str, str]:
        """
        Prunes RETRIEVED KNOWLEDGE and CONVERSATION SUMMARY / CURRENT CONTEXT if the total
        size of all sections exceeds max_size.
        """
        def total_len(secs):
            return sum(len(content) for content in secs.values())
            
        if total_len(sections) <= max_size:
            return sections
            
        # Copy to avoid modifying input dictionary
        pruned = dict(sections)
        
        # 1. Prune RETRIEVED KNOWLEDGE first
        retrieved_key = "RETRIEVED KNOWLEDGE"
        if retrieved_key in pruned and pruned[retrieved_key]:
            chunks = [c.strip() for c in pruned[retrieved_key].split("\n\n") if c.strip()]
            while len(chunks) > 1 and total_len(pruned) > max_size:
                chunks.pop()  # Remove the last/least relevant chunk
                pruned[retrieved_key] = "\n\n".join(chunks)
                
        # 2. Prune CHAT HISTORY / CONVERSATION SUMMARY / CURRENT CONTEXT if still over budget
        history_keys = ["CONVERSATION SUMMARY", "CURRENT CONTEXT", "CHAT HISTORY"]
        for hk in history_keys:
            if hk in pruned and pruned[hk] and total_len(pruned) > max_size:
                lines = pruned[hk].splitlines()
                # Remove lines from the top (oldest messages) until we fit or run out of lines
                while len(lines) > 2 and total_len(pruned) > max_size:
                    lines.pop(0)
                    pruned[hk] = "\n".join(lines)
                    
        return pruned

    def clean_whitespace(self, text: str) -> str:
        """
        Cleans up excessive newlines and trims trailing spaces.
        """
        if not text:
            return ""
        # Trim whitespace from each line
        lines = [line.strip() for line in text.splitlines()]
        text = "\n".join(lines)
        # Replace 3 or more consecutive newlines with exactly two newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def deduplicate_rag_chunks(self, text: str) -> str:
        """
        Identifies and removes duplicate or overlapping knowledge base documents.
        """
        return deduplicate_context(text)

    def deduplicate_lines(self, text: str) -> str:
        """
        Removes identical lines of text (e.g. duplicate conversation messages).
        """
        if not text:
            return ""

        lines = text.splitlines()
        seen: Set[str] = set()
        unique_lines: List[str] = []

        for line in lines:
            cleaned = line.strip()
            if not cleaned:
                unique_lines.append("")
                continue

            if cleaned not in seen:
                seen.add(cleaned)
                unique_lines.append(line)

        return "\n".join(unique_lines)

    def deduplicate_system_rules(self, text: str) -> str:
        """
        Filters and removes duplicate rule statements from system templates.
        Allows headers and non-numbered instructions to pass through intact.
        """
        if not text:
            return ""

        lines = text.splitlines()
        seen_rules: Set[str] = set()
        unique_lines: List[str] = []

        for line in lines:
            cleaned = line.strip()
            # Match list structures: "1. Rule text", "a. Rule text", "- Rule text", "* Rule text"
            match = re.match(r"^(\d+[\.\)]|[a-zA-Z][\.\)]|-|\*)\s+(.*)$", cleaned)
            if match:
                rule_body = match.group(2).strip().lower()
                if rule_body not in seen_rules:
                    seen_rules.add(rule_body)
                    unique_lines.append(line)
            else:
                # Keep non-rule formatting (headings, structural separators)
                unique_lines.append(line)

        return "\n".join(unique_lines)
