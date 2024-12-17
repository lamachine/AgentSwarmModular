"""
Configuration for LLM (Language Model) providers.

This module contains the configuration for different LLM providers including:
- OpenAI
- Ollama (local)
- Anthropic
- Google
- Microsoft
- GitHub

Each provider configuration includes:
- base_url: API endpoint
- model_name: Default model to use
- api_key_env: Environment variable name for API key
"""

from typing import Dict, Any

LLM_PROVIDERS: Dict[str, Dict[str, Any]] = {
    "openai": {
        "base_url": None,  # Uses OpenAI's default
        "model_name": "gpt-4o-mini",
        "api_key_env": "OPENAI_API_KEY"
    },
    "ollama": {
        "base_url": "http://localhost:11434",
        "model_name": "llama3:latest",
        "api_key_env": None  # Ollama doesn't use API keys
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1",
        "model_name": "claude-3-5-sonnet-20241022",
        "api_key_env": "ANTHROPIC_API_KEY"
    },
    "google": {
        "base_url": "https://generativelanguage.googleapis.com/v1",
        "model_name": "gemini-pro",
        "api_key_env": "GOOGLE_API_KEY"
    },
    "microsoft": {
        "base_url": "https://api.cognitive.microsoft.com/v1.0",
        "model_name": "gpt-4",
        "api_key_env": "MS_COPILOT_API_KEY"
    },
    "github": {
        "base_url": "https://api.github.com/copilot",
        "model_name": "copilot-chat",
        "api_key_env": "GITHUB_COPILOT_API_KEY"
    }
}

def validate_provider_config(provider: str) -> None:
    """
    Validate provider configuration exists and has required fields.
    
    Args:
        provider: Name of the provider to validate
        
    Raises:
        ValueError: If provider config is invalid
    """
    if provider not in LLM_PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}")
    
    config = LLM_PROVIDERS[provider]
    required_fields = ["model_name"]
    missing = [f for f in required_fields if f not in config]
    if missing:
        raise ValueError(f"Provider {provider} missing required fields: {missing}") 