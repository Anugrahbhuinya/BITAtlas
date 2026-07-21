def build_prompt(
    question: str,
    context: str
):

    return f"""
You are BITAtlas.

Answer using only the provided context.

Context:
{context}

Question:
{question}
"""