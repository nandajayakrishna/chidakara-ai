from rag.llm_client import model


def generate_answer(context, question, conversation_history=None, web_summary=None, context_obj=None, graph_results=None):

    history_str = ""
    if conversation_history:
        history_lines = []
        for q, a in conversation_history:
            history_lines.append(f"User: {q}\nAssistant: {a}")
        history_str = "\n".join(history_lines)
    else:
        history_str = "(No previous history)"

    prompt = f"""
You are Chidakara Knowledge Assistant.

Instructions:
1. Answer the Current Question using the facts present in the Knowledge Base (KB), Graph Results, and/or Web Results.
2. Use KB whenever available. Use Graph Results for entity connections and relationships. Use WEB only for external/current facts.
3. If multiple sources exist, merge them naturally.
4. Use the Conversation History ONLY for conversational continuity (e.g. resolving pronouns like "it", "he", "she", or referencing previously discussed topics).
5. Do NOT invent facts or use assumptions. Never hallucinate.
6. If the answer is missing, reply exactly:

"I could not find that information in the knowledge base."

7. Prefer factual extraction over explanation.

========
CONVERSATION HISTORY
========
{history_str}

========
KNOWLEDGE BASE
========
{context}

========
GRAPH RESULTS
========
{graph_results or "(No knowledge graph results available)"}

========
WEB RESULTS
========
{web_summary or "(No external web results available)"}

========
CURRENT QUESTION
========
{question}

Answer:
"""

    if context_obj is not None:
        context_len = len(context) if context else 0
        web_len = len(web_summary) if web_summary else 0
        # Character-based estimation: 4 characters per token
        prompt_tokens_est = len(prompt) // 4
        context_obj.debug_metadata["knowledge"] = {
            "context_length": context_len,
            "web_length": web_len,
            "prompt_tokens": prompt_tokens_est
        }

    response = model.generate_content(prompt)

    return response.text