import json
import time
import traceback
from typing import Dict, Any, List
from rag.llm_client import model

def run_reflection(context_or_question) -> Dict[str, Any]:
    """
    Executes the Reflection Agent.
    Evaluates whether the draft answer satisfies the user's question, detects hallucinations, 
    and checks if important information is missing.
    Supports ExecutionContext and backward compatible string questions.
    """
    is_context = hasattr(context_or_question, 'question')
    
    if is_context:
        ctx = context_or_question
        question = ctx.question
        draft_answer = ctx.draft_answer or ctx.final_answer
        retrieved_documents = ctx.retrieved_documents or []
        graph_results = getattr(ctx, 'graph_results', "")
        web_summary = getattr(ctx, 'web_summary', "")
    else:
        # Fallback values for backward compatibility
        ctx = None
        question = context_or_question
        draft_answer = ""
        retrieved_documents = []
        graph_results = ""
        web_summary = ""

    retrieved_documents_str = "\n\n".join([f"- Chunk {i+1}:\n{doc}" for i, doc in enumerate(retrieved_documents)]) if retrieved_documents else "(No retrieved document chunks available)"
    graph_results_str = graph_results if graph_results else "(No knowledge graph results available)"
    web_summary_str = web_summary if web_summary else "(No external web results available)"

    prompt = f"""You are a Reflection Agent.

Your task is to verify if the draft answer satisfies the user's question, identifies any missing information, checks for support in the retrieved evidence, and detects any hallucinations.

Read the following:
Question:
{question}

Retrieved Documents:
{retrieved_documents_str}

Graph Results:
{graph_results_str}

Web Summary:
{web_summary_str}

Draft Answer:
{draft_answer}

Analyze:
1. Was the user's question answered? (Set "answered" to true if the question is resolved, or false if it is not answered or if the draft says it cannot find the information.)
2. Is important information missing? (Provide a list of missing details if any, else an empty list.)
3. Is the draft answer supported by the retrieved documents, graph results, or web summary?
4. Did the draft answer hallucinate any facts not mentioned in the evidence? (Set "hallucination_detected" to true if there are facts in the draft answer not supported by any of the retrieved evidence, otherwise false.)
5. Provide a confidence score (between 0.00 and 1.00) based strictly on how well the answer is supported and whether it answers the query.
6. Provide a short reason explaining the evaluation.

Return ONLY a JSON object with this exact structure:
{{
  "answered": true/false,
  "missing_information": ["missing detail 1", ...],
  "hallucination_detected": true/false,
  "confidence": 0.95,
  "reason": "..."
}}

Do not return any conversational text. Return only the JSON object.
"""
    start_time = time.time()
    reflection_result = {
        "answered": False,
        "missing_information": [],
        "hallucination_detected": True,
        "confidence": 0.0,
        "reason": "Execution failed or did not run."
    }

    try:
        response = model.generate_content(prompt)
        resp_text = response.text.strip()
        
        # Clean JSON markdown blocks if present
        if "```" in resp_text:
            resp_text = resp_text.split("```")[1]
            if resp_text.startswith("json"):
                resp_text = resp_text[4:].strip()
                
        # Find bounds of JSON array/object to be safe
        start = resp_text.find('{')
        end = resp_text.rfind('}')
        if start != -1 and end != -1 and end > start:
            resp_text = resp_text[start:end+1]
            
        parsed = json.loads(resp_text)
        # Validate required fields
        reflection_result = {
            "answered": bool(parsed.get("answered", False)),
            "missing_information": list(parsed.get("missing_information", [])),
            "hallucination_detected": bool(parsed.get("hallucination_detected", False)),
            "confidence": float(parsed.get("confidence", 0.0)),
            "reason": str(parsed.get("reason", ""))
        }
    except Exception as e:
        import sys
        sys.stderr.write(f"REFLECTION AGENT PARSING ERROR: {str(e)}\n{traceback.format_exc()}\n")
        reflection_result = {
            "answered": False,
            "missing_information": ["Failed to parse reflection result"],
            "hallucination_detected": True,
            "confidence": 0.0,
            "reason": f"Parsing exception: {str(e)}"
        }

    duration_ms = (time.time() - start_time) * 1000.0

    if is_context:
        ctx.reflection = reflection_result
        
        # Run Confidence Engine dynamically
        from reasoning.confidence import calculate_confidence
        score, reason = calculate_confidence(ctx)
        ctx.confidence_score = score
        ctx.confidence_reason = reason
        
        # Log debug metrics for the visual trace debugger
        ctx.debug_metadata["reflection"] = {
            "reflection_time_ms": duration_ms,
            "confidence_score": score,
            "confidence_reason": reason,
            "reflection_result": reflection_result
        }

    return reflection_result
