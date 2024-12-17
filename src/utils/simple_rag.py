"""Simple RAG implementation using LangChain."""

import logging
import shutil
import json
import re
import html
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain.docstore.document import Document
from config import get_model_config, get_rag_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentSanitizer:
    """Utilities for sanitizing document content and metadata."""
    
    @staticmethod
    def sanitize_content(content: str) -> str:
        """Sanitize document content.
        
        - Remove potential XSS/script content
        - Normalize whitespace
        - Remove control characters
        - HTML escape special characters
        """
        # Remove script tags and their content
        content = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', content)
        
        # Remove other potentially dangerous HTML tags
        content = re.sub(r'<(style|iframe|object|embed|form)\b[^<]*(?:(?!<\/\1>)<[^<]*)*<\/\1>', '', content)
        
        # Remove control characters except newlines and tabs
        content = ''.join(char for char in content if char >= ' ' or char in '\n\t')
        
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        # HTML escape special characters
        content = html.escape(content)
        
        return content
    
    @staticmethod
    def sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize document metadata.
        
        - Remove potentially dangerous keys
        - Sanitize string values
        - Ensure proper types
        """
        safe_metadata = {}
        
        # List of allowed metadata keys
        allowed_keys = {'source', 'title', 'author', 'date', 'type', 'tags'}
        
        for key, value in metadata.items():
            # Skip potentially dangerous keys
            if key not in allowed_keys:
                continue
                
            # Sanitize string values
            if isinstance(value, str):
                value = DocumentSanitizer.sanitize_content(value)
            elif isinstance(value, (int, float, bool)):
                # Allow basic types as is
                pass
            else:
                # Convert other types to strings and sanitize
                value = DocumentSanitizer.sanitize_content(str(value))
            
            safe_metadata[key] = value
            
        return safe_metadata
    
    @staticmethod
    def sanitize_query(query: str) -> str:
        """Sanitize search query.
        
        - Remove special characters
        - Limit length
        - Basic injection prevention
        """
        # Remove special characters except basic punctuation
        query = re.sub(r'[^\w\s.,!?-]', '', query)
        
        # Limit length
        query = query[:1000]
        
        return query.strip()

class RAGService:
    """Service for handling RAG operations."""
    
    def __init__(self):
        self.model_config = get_model_config()
        self.rag_config = get_rag_config()
        self._embeddings = None
        self._llm = None
        self.sanitizer = DocumentSanitizer()
    
    @property
    def embeddings(self):
        """Get embeddings model, initializing if needed."""
        if self._embeddings is None:
            self._embeddings = OllamaEmbeddings(
                model=self.model_config["embedding_model"],
                base_url=self.model_config["base_url"]
            )
        return self._embeddings
    
    @property
    def llm(self):
        """Get LLM model, initializing if needed."""
        if self._llm is None:
            self._llm = ChatOllama(
                model=self.model_config["default_llm"],
                temperature=self.model_config["temperature"],
                base_url=self.model_config["base_url"]
            )
        return self._llm

    def save_vector_store(self, vector_store: FAISS, save_path: Optional[str] = None):
        """Safely save vector store with separate metadata."""
        save_path = Path(save_path or self.rag_config["vector_store_path"])
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index (already uses a secure binary format)
        vector_store.save_local(str(save_path), "index")
        
        # Extract and sanitize metadata before saving
        documents = vector_store.docstore._dict
        metadata = {
            str(k): {
                'page_content': self.sanitizer.sanitize_content(v.page_content),
                'metadata': self.sanitizer.sanitize_metadata(v.metadata)
            } for k, v in documents.items()
        }
        
        with open(save_path / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def load_vector_store(self, load_path: Optional[str] = None, allow_faiss_pickle: bool = False) -> FAISS:
        """Safely load vector store with metadata validation."""
        load_path = Path(load_path or self.rag_config["vector_store_path"])
        
        # Validate paths exist
        if not (load_path / "index.faiss").exists():
            raise ValueError("Vector store index not found")
        if not (load_path / "metadata.json").exists():
            raise ValueError("Vector store metadata not found")
        
        # Load metadata from JSON (secure)
        with open(load_path / "metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        # Validate metadata structure
        if not isinstance(metadata, dict):
            raise ValueError("Invalid metadata format")
        
        # Reconstruct documents with sanitization
        documents = {}
        for k, v in metadata.items():
            if not isinstance(v, dict) or 'page_content' not in v or 'metadata' not in v:
                raise ValueError(f"Invalid document format for key {k}")
            documents[k] = Document(
                page_content=self.sanitizer.sanitize_content(v['page_content']),
                metadata=self.sanitizer.sanitize_metadata(v['metadata'])
            )
        
        if not allow_faiss_pickle:
            raise ValueError(
                "FAISS requires pickle deserialization. Set allow_faiss_pickle=True "
                "only if you trust the source of this vector store. "
                "The index file could potentially contain malicious code if tampered with."
            )
        
        # Load FAISS index with explicit pickle permission
        vector_store = FAISS.load_local(
            str(load_path), 
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        vector_store.docstore._dict = documents
        
        return vector_store

    def process_documents(self, folder_path: str, patterns: Optional[List[str]] = None):
        """Process documents from a folder."""
        patterns = patterns or self.rag_config["supported_file_types"]
        
        # Clean up old vector store
        vector_store_path = Path(self.rag_config["vector_store_path"])
        if vector_store_path.exists():
            logger.info("Removing old vector store...")
            shutil.rmtree(vector_store_path)
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.rag_config["chunk_size"],
            chunk_overlap=self.rag_config["chunk_overlap"]
        )
        
        # Find all matching files
        folder_path = Path(folder_path)
        all_files = []
        for pattern in patterns:
            all_files.extend(folder_path.glob(pattern))
        
        logger.info(f"Found {len(all_files)} files")
        
        # Process each file with sanitization
        all_chunks = []
        for file_path in all_files:
            try:
                logger.info(f"Processing {file_path.name}")
                loader = TextLoader(str(file_path), encoding='utf-8')
                documents = loader.load()
                
                # Sanitize content and metadata before chunking
                sanitized_docs = []
                for doc in documents:
                    sanitized_docs.append(Document(
                        page_content=self.sanitizer.sanitize_content(doc.page_content),
                        metadata=self.sanitizer.sanitize_metadata(doc.metadata)
                    ))
                
                chunks = text_splitter.split_documents(sanitized_docs)
                all_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"Error processing {file_path.name}: {str(e)}")
        
        logger.info(f"Created {len(all_chunks)} chunks")
        
        # Create vector store
        if all_chunks:
            vector_store = FAISS.from_documents(all_chunks, self.embeddings)
            self.save_vector_store(vector_store)
            logger.info("Vector store saved")
            return vector_store
        return None

    def search_documents(self, query: str, num_results: int = 5):
        """Search for documents and generate an AI response."""
        try:
            # Sanitize the search query
            query = self.sanitizer.sanitize_query(query)
            
            # Load vector store
            vector_store = self.load_vector_store(allow_faiss_pickle=True)
            
            # Get relevant documents
            results = vector_store.similarity_search_with_score(query, k=num_results)
            
            # Format documents for LLM with sanitized content
            context = "\n\n".join(
                f"Document {i+1} (from {doc.metadata.get('source', 'Unknown')}):\n{doc.page_content}"
                for i, (doc, _) in enumerate(results)
            )
            
            # Generate response
            prompt = f"""Based on the following documents, please answer this question: {query}

Documents:
{context}

If you find any pricing or structured data in the documents, please format it clearly in your response.
Please provide a clear and concise answer based only on the information in these documents.
If you see a document that matches the query exactly (like a pricing document when asked about prices),
focus on that document rather than summarizing all documents.
If the documents don't contain enough information to answer the question, please say so.

Answer:"""
            
            response = self.llm.invoke(prompt)
            
            # Print AI response
            print("\nAI Response:")
            print("-" * 80)
            print(response)
            print("-" * 80)
            
            # Print source documents
            print("\nSource Documents:")
            for doc, score in results:
                print(f"\nRelevance Score: {1 - score:.2f}")
                print(f"Source: {doc.metadata.get('source', 'Unknown')}")
                print(f"Content: {doc.page_content[:300]}...")
                print("-" * 80)
                
        except Exception as e:
            logger.error(f"Error searching: {str(e)}", exc_info=True)

# For backward compatibility
def save_vector_store(vector_store: FAISS, save_path: str):
    """Backward compatibility wrapper."""
    rag = RAGService()
    return rag.save_vector_store(vector_store, save_path)

def load_vector_store(load_path: str, embeddings, allow_faiss_pickle: bool = False) -> FAISS:
    """Backward compatibility wrapper."""
    rag = RAGService()
    return rag.load_vector_store(load_path, allow_faiss_pickle)

def process_documents(folder_path: str, patterns: List[str] = None):
    """Backward compatibility wrapper."""
    rag = RAGService()
    return rag.process_documents(folder_path, patterns)

def search_documents(query: str, num_results: int = 5):
    """Backward compatibility wrapper."""
    rag = RAGService()
    return rag.search_documents(query, num_results)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python simple_rag.py <folder_path>")
        sys.exit(1)
        
    folder_path = sys.argv[1]
    rag = RAGService()
    
    # Process documents
    vector_store = rag.process_documents(folder_path)
    
    if vector_store:
        # Test search
        while True:
            query = input("\nEnter search query (or 'q' to quit): ")
            if query.lower() == 'q':
                break
            rag.search_documents(query) 