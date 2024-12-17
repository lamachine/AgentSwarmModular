"""
LLM Provider Management Tools

This module provides functions to manage different LLM providers including:
- Listing available providers
- Getting current provider info
- Switching between providers

Usage:
    llm_manager("list")  # List all available providers
    llm_manager("info")  # Get current provider info
    llm_manager("switch", provider="ollama")  # Switch to Ollama
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv, set_key
from functools import lru_cache
from .llm_config import LLM_PROVIDERS, validate_provider_config

@lru_cache(maxsize=1)
def get_env_path() -> str:
    """Get path to .env file."""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

def llm_manager(action: str, provider: Optional[str] = None) -> str:
    """
    Manage LLM providers and models.
    
    Args:
        action: Action to perform ('list', 'info', or 'switch')
        provider: Provider name for 'switch' action
        
    Returns:
        str: Result of the action
        
    Raises:
        ValueError: If action or provider is invalid
    """
    try:
        if action == "list":
            providers_info = []
            for name, config in LLM_PROVIDERS.items():
                providers_info.append(f"- {name}: {config['model_name']}")
            return "Available LLM Providers:\n" + "\n".join(providers_info)
            
        elif action == "info":
            current = os.getenv("LLM_PROVIDER", "openai")
            validate_provider_config(current)
            config = LLM_PROVIDERS[current]
            return f"Current Provider: {current}\nModel: {config['model_name']}"
            
        elif action == "switch":
            if not provider:
                raise ValueError("Provider name required for switch action")
            
            validate_provider_config(provider)
            set_key(get_env_path(), "LLM_PROVIDER", provider)
            return f"Switched to provider: {provider}\nPlease restart the application for changes to take effect"
            
        else:
            raise ValueError(f"Unknown action: {action}")
            
    except Exception as e:
        return f"Error in llm_manager: {str(e)}"

# Direct testing
if __name__ == "__main__":
    print("\nTesting LLM Manager:")
    try:
        print("\n1. Testing list action:")
        print(llm_manager("list"))
        
        print("\n2. Testing info action:")
        print(llm_manager("info"))
        
        print("\n3. Testing switch action:")
        print(llm_manager("switch", provider="ollama"))
        
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc()) 