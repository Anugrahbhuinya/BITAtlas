class HallucinationGuard:
    """
    Injects strict negative constraints and behavior rules to prevent the LLM
    from hallucinating data that is not present in the retrieved context.
    """
    def __init__(self):
        pass

    def get_guard_instructions(self) -> str:
        """
        Returns a structured instruction string containing strict hallucination controls.
        """
        return """HALLUCINATION GUARD (CRITICAL RULE CONTROLS):
1. Rely ONLY on the provided Student Profile, Conversation History, and Retrieved Knowledge Base Context.
2. DO NOT assume or extrapolate facts not explicitly mentioned in the context.
3. NEVER fabricate dates, semester deadlines, exam schedules, or fee structures.
4. NEVER fabricate room numbers, building names, campus routes, distances, or walking times.
5. NEVER fabricate attendance percentages, lecture counts, or academic status.
6. If the information is not explicitly provided in the context, you MUST respond exactly:
   "I could not find that information in the BIT Mesra knowledge base."
7. If the retrieved context contains ambiguous, conflicting, or partial information, state your uncertainty clearly and guide the student to the official administrative office or department.
8. Do not speculate under any circumstances.
"""
