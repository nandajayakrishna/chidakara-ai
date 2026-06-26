import os
from providers.base_provider import WebProvider
from providers.duckduckgo_provider import DuckDuckGoProvider

def get_web_provider() -> WebProvider:
    """
    Dynamically select and return the active WebProvider instance.
    Checks the WEB_PROVIDER environment variable, defaulting to 'duckduckgo'.
    """
    provider_name = os.environ.get("WEB_PROVIDER", "duckduckgo").lower()
    
    if provider_name == "duckduckgo":
        return DuckDuckGoProvider()
    else:
        # Gracefully fallback to DuckDuckGo, but could support serpapi, brave, etc. in future
        return DuckDuckGoProvider()
