"""Configuration settings for the AI system."""

from typing import Dict, Any

# Model configurations
MODEL_CONFIG = {
    "default_llm": "claude-3-5-sonnet-20241022",  # Default LLM for general tasks
    "embedding_model": "nomic-embed-text:latest",  # Model for embeddings
    #"base_url": "http://localhost:11434",  # Ollama base URL
    #"temperature": 0,  # Default temperature for LLM responses
}

# RAG configurations
RAG_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 100,
    "vector_store_path": "data/vector_store",
    "supported_file_types": ["*.txt", "*.md", "*.py"],  # Add more as needed
}

def get_model_config() -> Dict[str, Any]:
    """Get the current model configuration."""
    return MODEL_CONFIG.copy()

def get_rag_config() -> Dict[str, Any]:
    """Get the current RAG configuration."""
    return RAG_CONFIG.copy() 