from rag.llm import model


def critic_review(
    question,
    context,
    answer
):

    prompt = f"""
You are a Critic Agent.

Question:
{question}

Context:
{context}

Generated Answer:
{answer}

Determine:

1. Is answer supported by context?
2. Any hallucinations?
3. Confidence score 0-100

Return concise review.
"""

    response = model.generate_content(
        prompt
    )

    return response.text