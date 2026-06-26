from typing import List, Dict, Any

class WebProvider:
    """
    Abstract Base Class defining the interface for all Web Search Providers.
    """
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Executes a web search query.
        Returns a list of dicts:
        [
            {
                "title": str,
                "url": str,
                "snippet": str,
                "timestamp": str,
                "source": str
            }
        ]
        """
        raise NotImplementedError("Each search provider must implement the search method.")
