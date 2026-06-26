from typing import List, Dict, Any
from datetime import datetime
from providers.base_provider import WebProvider

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None


class DuckDuckGoProvider(WebProvider):
    """
    DuckDuckGo search provider implementing the WebProvider interface.
    """
    def search(self, query: str) -> List[Dict[str, Any]]:
        if DDGS is None:
            raise RuntimeError("DuckDuckGo search library is not installed.")

        try:
            ddgs = DDGS()
            # Retrieve search results
            raw_results = list(ddgs.text(query, max_results=5))
        except Exception as e:
            raise RuntimeError(f"DuckDuckGo search failed: {str(e)}")

        results = []
        for r in raw_results:
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "DuckDuckGo"
            })
        return results
