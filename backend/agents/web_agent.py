import traceback
from providers import get_web_provider
from rag.llm_client import model

def run_web(context_or_question):
    """
    Executes the web search agent.
    Queries the active web search provider, summarizes findings, and updates the context.
    Supports ExecutionContext and backward compatible string questions.
    """
    is_context = hasattr(context_or_question, 'question')
    query = context_or_question.question if is_context else context_or_question

    provider = get_web_provider()
    
    try:
        import time
        start_t = time.time()
        results = provider.search(query)
        latency_ms = (time.time() - start_t) * 1000.0
        sources = [{"title": r["title"], "url": r["url"]} for r in results]
        
        # Build search results string for the summarizer
        results_lines = []
        for i, r in enumerate(results, 1):
            results_lines.append(f"[{i}] {r['title']} ({r['url']})\nSnippet: {r['snippet']}\n")
        results_str = "\n".join(results_lines) if results_lines else "No results found."

        # Summarize findings using LLM
        prompt = f"""You are a Web Intelligence Agent.

Analyze the search results below and summarize the findings to answer the query.
Be concise, accurate, and base your summary strictly on the search results provided.

Query:
{query}

Search Results:
{results_str}

Summary:
"""
        response = model.generate_content(prompt)
        summary = response.text.strip()

        if is_context:
            context_or_question.web_results = results
            context_or_question.web_sources = sources
            context_or_question.web_summary = summary
            context_or_question.web_status = "success"
            context_or_question.debug_metadata["web"] = {
                "provider": provider.__class__.__name__,
                "urls": [r["url"] for r in results],
                "latency_ms": latency_ms
            }
        
        return summary

    except Exception as e:
        # Fallback: If the Web Agent fails, continue the workflow. Do not crash. Record ctx.web_status as failed.
        import sys
        sys.stderr.write(f"WEB AGENT ERROR: {str(e)}\n{traceback.format_exc()}\n")
        
        if is_context:
            context_or_question.web_status = "failed"
            context_or_question.web_results = []
            context_or_question.web_sources = []
            context_or_question.web_summary = f"Error performing web search: {str(e)}"
        
        return f"Error: {str(e)}"
