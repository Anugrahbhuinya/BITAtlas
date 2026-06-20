def build_prompt(
    question: str,
    context: str
):

    return f"""
You are BIT Mesra AI Assistant.

Answer using only the provided context.

Context:
{context}

Question:
{question}
"""