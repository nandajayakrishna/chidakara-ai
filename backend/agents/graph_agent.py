import time
import traceback
from typing import List, Dict, Any
from graph.memory_graph_store import MemoryGraphStore
from graph.graph_builder import build_graph_from_documents
from graph.graph_search import search_graph_with_llm

def run_graph(context_or_question) -> str:
    """
    Executes the Graph Agent.
    Builds a Knowledge Graph from retrieved context documents, traverses it to answer the question,
    and updates ExecutionContext with nodes, edges, results, and status.
    Supports ExecutionContext and backward compatible string questions.
    """
    is_context = hasattr(context_or_question, 'question')
    
    if is_context:
        ctx = context_or_question
        documents = ctx.retrieved_documents
        question = ctx.question
    else:
        # Backward compatibility fallback
        documents = []
        question = context_or_question

    # If in context mode but retrieved documents are empty, attempt to populate them dynamically
    if is_context and not documents:
        from agents.researcher_agent import gather
        try:
            docs, _ = gather(ctx)
            documents = docs
        except Exception:
            documents = []
    elif not is_context:
        from agents.researcher_agent import gather
        try:
            docs, _ = gather(question)
            documents = docs
        except Exception:
            documents = []

    store = MemoryGraphStore()
    
    try:
        # 1. Build local graph from retrieved text
        build_graph_from_documents(store, documents)
        
        # 2. Run graph search query using semantic traversal
        start_search = time.time()
        results = search_graph_with_llm(store, question)
        search_latency_ms = (time.time() - start_search) * 1000.0
        
        serialized = store.serialize()
        nodes = serialized["nodes"]
        edges = serialized["edges"]
        
        entity_types = list(set([n.get("label", "Entity") for n in nodes]))
        
        if is_context:
            ctx.graph_nodes = nodes
            ctx.graph_edges = edges
            ctx.graph_results = results
            ctx.graph_status = "success"
            
            # Record rich trace metrics for the visual debugger
            ctx.debug_metadata["graph"] = {
                "nodes_created": len(nodes),
                "edges_created": len(edges),
                "entity_types": entity_types,
                "relationship_count": len(edges),
                "graph_search_latency": search_latency_ms
            }
            
        return results
        
    except Exception as e:
        import sys
        sys.stderr.write(f"GRAPH AGENT ERROR: {str(e)}\n{traceback.format_exc()}\n")
        
        if is_context:
            ctx.graph_status = "failed"
            ctx.graph_nodes = []
            ctx.graph_edges = []
            ctx.graph_results = f"Error building graph: {str(e)}"
            ctx.debug_metadata["graph"] = {
                "nodes_created": 0,
                "edges_created": 0,
                "entity_types": [],
                "relationship_count": 0,
                "graph_search_latency": 0.0,
                "error": str(e)
            }
            
        return f"Error: {str(e)}"
