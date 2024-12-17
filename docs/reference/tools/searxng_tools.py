"""SearXNG search integration."""
import os
import json
import requests
from typing import Optional, Dict, Any
from functools import lru_cache

def searxng_search(
    query: str,
    format: str = "json",
    page: int = 1,
    categories: Optional[str] = None,
    time_range: Optional[str] = None,
    language: Optional[str] = None
) -> str:
    """
    Search using local SearXNG instance.
    
    Args:
        query: Search query string
        format: Response format (json, csv, rss)
        page: Page number
        categories: Comma-separated category list
        time_range: Time filter (day, month, year)
        language: Language code
    
    Returns:
        str: Search results or error message
    """
    try:
        url = "http://localhost:4000/search"
        
        params = {
            "q": query,
            "format": format,
            "pageno": page
        }
        
        if categories:
            params["categories"] = categories
        if time_range:
            params["time_range"] = time_range
        if language:
            params["language"] = language

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        if format == "json":
            return json.dumps(response.json(), indent=2)
        return response.text
        
    except requests.exceptions.RequestException as e:
        return f"Error calling SearXNG: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

# Direct testing
if __name__ == "__main__":
    print("\nTesting SearXNG Search:")
    try:
        result = searxng_search("test query")
        print(f"Success: {result}")
    except Exception as e:
        print(f"Test failed: {str(e)}") 