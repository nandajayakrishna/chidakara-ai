import time
from rag.llm_client import model

def review(context_or_question, answer=None):
    """
    Executes the answer review critique.
    Supports ExecutionContext and backward compatible positional parameters.
    """
    is_context = hasattr(context_or_question, 'question')
    if is_context:
        ctx = context_or_question
        question = ctx.question
        ans = ctx.draft_answer if ctx.draft_answer else ctx.final_answer
    else:
        ctx = None
        question = context_or_question
        ans = answer

    reflection = getattr(ctx, 'reflection', {}) if is_context else {}
    confidence_score = getattr(ctx, 'confidence_score', 0.0) if is_context else 0.0
    confidence_reason = getattr(ctx, 'confidence_reason', "") if is_context else ""

    hallucination_detected = reflection.get("hallucination_detected", False)
    answered = reflection.get("answered", True)  # Default to True if not present

    # Determine if we should perform normal polishing or corrective regeneration
    should_regenerate = is_context and (hallucination_detected or not answered)

    if should_regenerate:
        retrieved_documents = getattr(ctx, 'retrieved_documents', []) or []
        retrieved_documents_str = "\n\n".join([f"- Chunk {i+1}:\n{doc}" for i, doc in enumerate(retrieved_documents)]) if retrieved_documents else "(No retrieved document chunks available)"
        graph_results_str = getattr(ctx, 'graph_results', "") or "(No knowledge graph results available)"
        web_summary_str = getattr(ctx, 'web_summary', "") or "(No external web results available)"
        reflection_summary = f"Answered: {reflection.get('answered')}, Hallucination Detected: {reflection.get('hallucination_detected')}, Missing Information: {reflection.get('missing_information')}, Reason: {reflection.get('reason')}"

        prompt = f"""You are a Critic Agent.

The previous draft answer has issues (e.g., it is incorrect, incomplete, or contains hallucinations).
You must regenerate the answer using ONLY the supported evidence in the Retrieved Documents, Graph Results, and Web Summary.
If the information to answer the question is missing, you must return exactly:
"I could not find that information in the knowledge base."

Do not invent or assume any facts.

Question:
{question}

Original Draft Answer:
{ans}

======== REFLECTION ========
Reflection Summary: {reflection_summary}
Confidence Score: {confidence_score}
Confidence Reason: {confidence_reason}

Retrieved Documents:
{retrieved_documents_str}

Graph Results:
{graph_results_str}

Web Summary:
{web_summary_str}

Tasks:
- Regenerate the answer using only supported evidence.
- Remove any hallucinations.
- If evidence is missing, return exactly: "I could not find that information in the knowledge base."

New Answer:
"""
    else:
        reflection_summary = f"Answered: {reflection.get('answered')}, Hallucination Detected: {reflection.get('hallucination_detected')}, Missing Information: {reflection.get('missing_information')}, Reason: {reflection.get('reason')}" if reflection else "(No reflection analysis executed)"

        prompt = f"""You are a Critic Agent.

Review the answer below, using the Reflection Summary, Confidence Score, and Confidence Reason for verification.
Do not invent any new information or fabricate facts.

Question:
{question}

Answer:
{ans}

======== REFLECTION ========
Reflection Summary: {reflection_summary}
Confidence Score: {confidence_score}
Confidence Reason: {confidence_reason}

Tasks:
- Improve clarity.
- Remove redundancies.
- Keep the answer concise.
- Ensure the answer is supported by the facts.
- Do not invent information.
- If the answer is already correct, return it unchanged.

Final Answer:
"""

    start_t = time.time()
    response = model.generate_content(prompt)
    reviewed = response.text.strip()
    duration_ms = (time.time() - start_t) * 1000.0

    if is_context:
        ctx.final_answer = reviewed
        ctx.debug_metadata["critic"] = {
            "review_duration_ms": duration_ms,
            "regenerated": should_regenerate
        }

    return reviewed