"""Tests for simple_rag.py"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json
from langchain.docstore.document import Document
from langchain_ollama import OllamaEmbeddings
from simple_rag import RAGService

class TestSimpleRAG(unittest.TestCase):
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.vector_store_path = Path(self.temp_dir) / "vector_store"
        self.rag_service = RAGService()
        
        # Create a test document
        self.test_content = "This is a test document."
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text(self.test_content)

    def tearDown(self):
        """Clean up temporary files."""
        shutil.rmtree(self.temp_dir)

    def test_process_and_load_documents(self):
        """Test full process of document processing, saving, and loading."""
        # Process test document
        vector_store = self.rag_service.process_documents(self.temp_dir, ["*.txt"])
        self.assertIsNotNone(vector_store, "Vector store should be created")
        
        # Verify metadata.json exists and has correct format
        metadata_path = Path(self.rag_service.rag_config["vector_store_path"]) / "metadata.json"
        self.assertTrue(metadata_path.exists(), "metadata.json should exist")
        
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        self.assertIsInstance(metadata, dict, "Metadata should be a dictionary")
        
        # Check content is preserved
        found_content = False
        for doc_data in metadata.values():
            if self.test_content in doc_data['page_content']:
                found_content = True
                break
        self.assertTrue(found_content, "Test content should be in metadata")
        
        # Test loading without pickle permission
        with self.assertRaises(ValueError) as context:
            self.rag_service.load_vector_store(allow_faiss_pickle=False)
        self.assertIn("FAISS requires pickle deserialization", str(context.exception))
        
        # Test loading with pickle permission
        loaded_store = self.rag_service.load_vector_store(allow_faiss_pickle=True)
        self.assertIsNotNone(loaded_store, "Vector store should load successfully")
        
        # Verify document content is preserved after loading
        found_content = False
        for doc in loaded_store.docstore._dict.values():
            if self.test_content in doc.page_content:
                found_content = True
                break
        self.assertTrue(found_content, "Test content should be preserved after loading")

    def test_invalid_metadata(self):
        """Test handling of invalid metadata."""
        # Create invalid metadata file
        self.vector_store_path.mkdir(parents=True)
        invalid_metadata = {"invalid": "format"}
        with open(self.vector_store_path / "metadata.json", "w") as f:
            json.dump(invalid_metadata, f)
        
        # Create dummy index file
        (self.vector_store_path / "index.faiss").touch()
        
        # Test loading invalid metadata
        with self.assertRaises(ValueError):
            self.rag_service.load_vector_store(str(self.vector_store_path), allow_faiss_pickle=True)

    def test_sanitization(self):
        """Test document sanitization functionality."""
        # Create a test document with potentially dangerous content
        dangerous_content = """
        <script>alert('xss')</script>
        <iframe src="evil.com"></iframe>
        Normal text with some \x00control\x01 characters
        <style>body { background: red; }</style>
        Multiple    spaces   and\ttabs
        """
        
        # Create test document
        test_file = Path(self.temp_dir) / "dangerous.txt"
        test_file.write_text(dangerous_content)
        
        # Process document
        vector_store = self.rag_service.process_documents(self.temp_dir, ["*.txt"])
        self.assertIsNotNone(vector_store, "Vector store should be created")
        
        # Load and verify sanitization
        loaded_store = self.rag_service.load_vector_store(allow_faiss_pickle=True)
        
        # Find the sanitized dangerous content
        dangerous_doc_found = False
        for doc in loaded_store.docstore._dict.values():
            content = doc.page_content
            if 'Normal text' in content:
                dangerous_doc_found = True
                
                # Content checks
                self.assertNotIn('<script>', content)
                self.assertNotIn('<iframe>', content)
                self.assertNotIn('<style>', content)
                self.assertNotIn('\x00', content)
                self.assertNotIn('\x01', content)
                self.assertIn('Normal text', content)
                break
        
        self.assertTrue(dangerous_doc_found, "Sanitized dangerous document should be found")
        
        # Test query sanitization
        dangerous_query = "<script>alert('xss')</script> test query with \x00 control chars"
        sanitized = self.rag_service.sanitizer.sanitize_query(dangerous_query)
        self.assertNotIn('<script>', sanitized)
        self.assertNotIn('\x00', sanitized)
        self.assertIn('test query', sanitized)

if __name__ == '__main__':
    unittest.main() 