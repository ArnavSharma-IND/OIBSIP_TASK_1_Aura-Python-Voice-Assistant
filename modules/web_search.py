"""
Web Search and Browser Navigation Module for ArnavSharma_Task1.
Handles automated web searching via default system browser across major search engines.
"""

import urllib.parse
import webbrowser
from typing import Optional, Tuple

from utils.logger import get_logger

logger = get_logger("WebSearch")


class WebSearchService:
    """Manages browser opening and query submission for web searches."""

    ENGINE_URLS = {
        "google": "https://www.google.com/search?q={}",
        "bing": "https://www.bing.com/search?q={}",
        "duckduckgo": "https://duckduckgo.com/?q={}",
        "youtube": "https://www.youtube.com/results?search_query={}",
        "wikipedia": "https://en.wikipedia.org/wiki/Special:Search?search={}",
        "github": "https://github.com/search?q={}",
    }

    def __init__(self, default_engine: str = "google"):
        self.default_engine = default_engine.lower()
        if self.default_engine not in self.ENGINE_URLS:
            self.default_engine = "google"

    def search(self, query: str, engine: Optional[str] = None) -> Tuple[bool, str]:
        """
        Opens the user's default browser with the requested search query.

        Args:
            query: The search term or question.
            engine: Optional search engine key.

        Returns:
            Tuple of (success: bool, spoken_response: str)
        """
        clean_query = query.strip()
        if not clean_query:
            return False, "Please specify what you would like me to search for."

        # Detect if user specifically asked for YouTube or GitHub
        selected_engine = (engine or self.default_engine).lower()
        q_lower = clean_query.lower()
        if "on youtube" in q_lower or "in youtube" in q_lower:
            selected_engine = "youtube"
            clean_query = clean_query.replace("on youtube", "").replace("in youtube", "").strip()
        elif "on github" in q_lower or "in github" in q_lower:
            selected_engine = "github"
            clean_query = clean_query.replace("on github", "").replace("in github", "").strip()

        base_url = self.ENGINE_URLS.get(selected_engine, self.ENGINE_URLS["google"])
        encoded = urllib.parse.quote_plus(clean_query)
        target_url = base_url.format(encoded)

        logger.info(f"Opening browser for search query: '{clean_query}' via {selected_engine} -> {target_url}")

        try:
            webbrowser.open(target_url, new=2)
            # Matches user prompt: "Searching the web for Python machine learning tutorials."
            spoken = f"Searching the web for {clean_query}."
            return True, spoken
        except Exception as err:
            logger.error(f"Failed to open browser for search: {err}")
            return False, f"Could not open the browser: {str(err)}"

    def open_url(self, url: str) -> Tuple[bool, str]:
        """Opens an arbitrary URL in the default browser."""
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"
        try:
            webbrowser.open(url, new=2)
            return True, f"Opening {url}."
        except Exception as err:
            logger.error(f"Failed to open URL '{url}': {err}")
            return False, f"Could not open {url}."

