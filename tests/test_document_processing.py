"""Test script for document processing capabilities."""

import asyncio
import logging
from pathlib import Path
from services.db_service import DatabaseService
from services.document_tools import DocumentTools

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_file_processing(folder_path: str, patterns: list[str]):
    """Test processing files from a folder.
    
    Args:
        folder_path: Path to test documents folder
        patterns: List of file patterns to process
    """
    try:
        # Initialize services
        db = DatabaseService()
        await db.initialize()
        doc_tools = DocumentTools(db)
        
        # Process directory
        folder_path = Path(folder_path).resolve()
        logger.debug(f"Absolute folder path: {folder_path}")
        logger.debug(f"Path exists: {folder_path.exists()}")
        logger.debug(f"Is directory: {folder_path.is_dir()}")
        
        # List files before processing
        logger.debug("Files in directory:")
        for pattern in patterns:
            files = list(folder_path.glob(pattern))
            logger.debug(f"Pattern {pattern}: {len(files)} files found")
            for file in files:
                logger.debug(f"- {file}")
        
        logger.info(f"Processing files in: {folder_path}")
        logger.info(f"Using patterns: {patterns}")
        
        # Force refresh to ensure we're processing the new documents
        stats = await doc_tools.process_directory(str(folder_path), patterns, force_refresh=True)
        
        logger.info("\nProcessing Results:")
        logger.info(f"Documents processed: {stats['num_documents']}")
        logger.info(f"Total chunks created: {stats['num_chunks']}")
        if stats['skipped_files'] > 0:
            logger.warning(f"Skipped files: {stats['skipped_files']}")
            
        # Test search functionality
        if stats['num_documents'] > 0:
            logger.info("\nTesting search functionality...")
            # Try a few different search queries
            test_queries = [
                "function",  # For code files
                "import",    # For Python files
                "include",   # For C/Arduino files
                "the",      # Common word to find text content
            ]
            
            for query in test_queries:
                logger.info(f"\nSearching for: '{query}'")
                results = await doc_tools.search_documents(query, num_results=2)
                
                if results:
                    logger.info(f"Found {len(results)} results:")
                    for i, result in enumerate(results, 1):
                        doc = result['document']
                        logger.info(f"\nResult {i} (score: {result['score']:.3f}):")
                        logger.info(f"Title: {doc.title}")
                        logger.info(f"Source: {doc.metadata.get('path', 'Unknown')}")
                        content_preview = doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
                        logger.info(f"Content Preview: {content_preview}")
                else:
                    logger.info("No results found")
                    
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        raise
    finally:
        if hasattr(db, 'pool'):
            await db.pool.close()

def main():
    """Main entry point."""
    # Test folder path - update this to your test documents location
    test_folder = input("Enter the path to your test documents folder: ")
    test_folder = Path(test_folder).resolve()
    
    if not test_folder.exists():
        logger.error(f"Folder not found: {test_folder}")
        return
        
    # File patterns to test
    patterns = [
        "*.txt",    # Text files
        "*.py",     # Python files
        "*.ino",    # Arduino files
        "*.c",      # C files
        "*.cpp",    # C++ files
        "*.h",      # Header files
        "*.pdf",    # PDF files
        "*.doc*",   # Word documents
        "*.ppt*",   # PowerPoint files
        "*.xls*",   # Excel files
    ]
    
    # Run tests
    asyncio.run(test_file_processing(str(test_folder), patterns))

if __name__ == "__main__":
    main() 