"""Perplexity API integration."""
import os
import json
import requests
from functools import lru_cache
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@lru_cache(maxsize=1)
def get_api_key() -> str:
    """Get Perplexity API key from environment variables."""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY environment variable not set")
    return api_key

def perplexity_chat(
    prompt: str,
    model: str = "llama-3.1-sonar-small-128k-online",
    temperature: float = 0.2,
    max_tokens: Optional[int] = None
) -> str:
    """
    Send a chat request to Perplexity API.
    
    Args:
        prompt: The user's question or prompt
        model: The model to use (default: llama-3.1-sonar-small-128k-online)
        temperature: Controls randomness (0-1, default: 0.2)
        max_tokens: Maximum tokens in response (optional)
    
    Returns:
        str: Response from API or error message
    """
    try:
        url = "https://api.perplexity.ai/chat/completions"
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "Be precise and concise."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "top_p": 0.9,
            "search_domain_filter": ["perplexity.ai"],
            "return_images": False,
            "return_related_questions": False,
            "search_recency_filter": "month",
            "top_k": 0,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 1
        }
        
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        headers = {
            "Authorization": f"Bearer {get_api_key()}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if 'choices' not in data or not data['choices']:
            return "Error: Unexpected API response format"
        
        return data['choices'][0]['message']['content']
        
    except requests.exceptions.RequestException as e:
        return f"Error calling Perplexity API: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

# Direct testing
if __name__ == "__main__":
    print("\nTesting Perplexity API:")
    try:
        result = perplexity_chat("What is Python?")
        print(f"Success: {result}")
    except Exception as e:
        print(f"Test failed: {str(e)}")