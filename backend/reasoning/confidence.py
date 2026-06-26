from typing import Tuple

def calculate_confidence(ctx) -> Tuple[float, str]:
    """
    Computes a deterministic 0.00–1.00 confidence score and brief explanation text
    based on the state accumulated in ExecutionContext.
    """
    workflow = ctx.workflow_state.get("workflow", [])
    
    # 1. Pure Tool query check
    # A tool query is one that executes 'tool' but does not include 'knowledge' or 'research'.
    is_pure_tool = "tool" in workflow and not ("knowledge" in workflow or "research" in workflow)
    if is_pure_tool:
        return 1.00, "Tool execution is deterministic and fully accurate."

    # Check fallback response
    ans_text = (ctx.final_answer or ctx.draft_answer or "").lower()
    has_fallback = "i could not find that information" in ans_text or "not find that information in the knowledge base" in ans_text

    # Extract reflection results
    reflection = ctx.reflection or {}
    reflection_answered = reflection.get("answered", False)
    reflection_hallucination = reflection.get("hallucination_detected", False)
    reflection_confidence = reflection.get("confidence", 0.0)

    # 2. Heuristic calculations
    # RAG chunks & similarity
    scores = ctx.debug_metadata.get("research", {}).get("similarity_scores", [])
    avg_similarity = 0.0
    if scores:
        # Distance to similarity mapping. L2 distances in ChromaDB default embedding space
        # typically range between 1.0 (good match) and 1.8 (poor match).
        # We use a generous mapping: similarity = max(0.0, min(1.0, 2.0 - (s * 0.8)))
        similarities = [max(0.0, min(1.0, 2.0 - (s * 0.8))) for s in scores]
        avg_similarity = sum(similarities) / len(similarities)
        
    chunks_count = len(ctx.retrieved_documents)
    # Ratio relative to optimal count (e.g. 3 chunks)
    chunks_score = min(1.0, chunks_count / 3.0)
    
    # Combine chunk score and similarity
    rag_score = (avg_similarity * 0.7) + (chunks_score * 0.3)

    # Graph check
    is_graph_query = "graph" in workflow
    graph_score = 1.0
    if is_graph_query:
        # Ensure graph agent ran and created nodes
        if hasattr(ctx, "graph_nodes") and ctx.graph_nodes:
            graph_score = 1.0
        else:
            graph_score = 0.2

    # Web check
    is_web_query = "web" in workflow
    web_score = 1.0
    if is_web_query:
        if getattr(ctx, "web_summary", None) and len(ctx.web_summary.strip()) > 0:
            web_score = 1.0
        else:
            web_score = 0.2

    # Modality aggregation
    modality_scores = [rag_score]
    if is_graph_query:
        modality_scores.append(graph_score)
    if is_web_query:
        modality_scores.append(web_score)
        
    heuristic_score = sum(modality_scores) / len(modality_scores)

    # 3. Reflection outcome integration
    if reflection_answered and not reflection_hallucination:
        # Successfully answered without hallucinations
        # Blend: 20% heuristic score, 80% Reflection self-assessed confidence
        score = (heuristic_score * 0.2) + (reflection_confidence * 0.8)
    else:
        # Flagged issues
        score = min(0.35, reflection_confidence)

    # Apply hard penalties for lack of answers or hallucinations
    if has_fallback:
        score = min(0.35, score)
    if not reflection_answered:
        score = min(0.35, score)
    if reflection_hallucination:
        score = min(0.20, score)

    # Final clamping and rounding
    score = round(max(0.00, min(1.00, score)), 2)

    # 4. Generate deterministic, human-readable reasoning reasons
    reasons = []
    if has_fallback:
        reasons.append("Answer is the fallback response indicating lack of evidence in the knowledge base.")
    else:
        if reflection_answered:
            reasons.append("The question was successfully answered.")
        else:
            reasons.append("The question was not fully answered by the draft answer.")

        if reflection_hallucination:
            reasons.append("Potential hallucinations were detected in the draft answer.")
        else:
            reasons.append("No hallucinations were detected.")

        if is_graph_query:
            if hasattr(ctx, "graph_nodes") and ctx.graph_nodes:
                reasons.append(f"Answer supported by knowledge graph evidence ({len(ctx.graph_nodes)} nodes, {len(ctx.graph_edges)} edges).")
            else:
                reasons.append("Expected knowledge graph evidence, but none was found.")

        if is_web_query:
            if getattr(ctx, "web_summary", None):
                reasons.append("Answer supported by external search web evidence.")
            else:
                reasons.append("Expected external web search evidence, but none was found.")

        if avg_similarity > 0.7:
            reasons.append("High similarity retrieved text chunks support the answer.")
        elif avg_similarity > 0.4:
            reasons.append("Moderate similarity retrieved text chunks support the answer.")
        elif avg_similarity > 0.0:
            reasons.append("Low similarity retrieved text chunks found.")

    reason = " ".join(reasons)
    return score, reason
