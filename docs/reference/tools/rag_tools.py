"""RAG tools for the main agent."""

from typing import List, Optional
from pathlib import Path
from simple_rag import RAGService, search_documents

class RAGTool:
    """Tool for handling document ingestion and querying."""
    
    def __init__(self):
        self.rag_service = RAGService()
    
    def ingest_documents(self, folder_path: str, patterns: Optional[List[str]] = None) -> bool:
        """Ingest documents from a folder.
        
        Args:
            folder_path: Path to folder containing documents
            patterns: Optional list of file patterns to match
            
        Returns:
            bool: True if ingestion was successful
        """
        try:
            folder_path = Path(folder_path)
            if not folder_path.exists():
                raise ValueError(f"Folder not found: {folder_path}")
                
            vector_store = self.rag_service.process_documents(str(folder_path), patterns)
            return vector_store is not None
            
        except Exception as e:
            print(f"Error ingesting documents: {str(e)}")
            return False
    
    def query_documents(self, query: str, num_results: int = 5) -> Optional[str]:
        """Query the document store.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            Optional[str]: Response from the AI, or None if error
        """
        try:
            return self.rag_service.search_documents(query, num_results)
        except Exception as e:
            print(f"Error querying documents: {str(e)}")
            return None

# For backward compatibility
def search_local_documents(query: str, num_results: int = 5) -> Optional[str]:
    """Search through local documents using RAG.
    
    Args:
        query: The search query
        num_results: Number of results to return
        
    Returns:
        Optional[str]: Response from the AI, or None if error
    """
    return search_documents(query, num_results)