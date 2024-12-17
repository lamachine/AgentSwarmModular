"""Command line interface for document processing."""

import logging
import asyncio
import argparse
from typing import List
from pathlib import Path

from services.db_service import DatabaseService
from services.document_tools import DocumentTools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentCLI:
    """CLI for document processing."""
    
    def __init__(self):
        """Initialize CLI."""
        self.db = DatabaseService()
        self.doc_tools = None
        
    async def initialize(self):
        """Initialize services."""
        logger.info("Initializing services...")
        await self.db.initialize()
        self.doc_tools = DocumentTools(self.db)
        
    async def ingest_documents(self, folder_path: str, patterns: List[str]):
        """Ingest documents from a folder.
        
        Args:
            folder_path: Path to document folder
            patterns: List of file patterns to match
        """
        folder_path = Path(folder_path).resolve()
        
        if not folder_path.exists():
            logger.error(f"Folder not found: {folder_path}")
            return
            
        logger.info(f"Ingesting documents from: {folder_path}")
        logger.info(f"File patterns: {patterns}")
        
        try:
            stats = await self.doc_tools.process_directory(str(folder_path), patterns)
            logger.info(f"Successfully processed {stats['num_documents']} documents")
            logger.info(f"Created {stats['num_chunks']} chunks")
            
        except Exception as e:
            logger.error(f"Error during ingestion: {str(e)}")
            raise
            
    async def search_documents(self, query: str, num_results: int = 5):
        """Search for documents.
        
        Args:
            query: Search query
            num_results: Number of results to return
        """
        try:
            results = await self.doc_tools.search_documents(query, num_results)
            
            if not results:
                logger.info("No results found")
                return
                
            logger.info(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                logger.info(f"\nResult {i} (score: {result['score']:.3f}):")
                logger.info(f"Source: {result['metadata'].get('source', 'Unknown')}")
                logger.info(f"Content: {result['content'][:200]}...")
                
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            raise

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Document processing CLI")
    
    parser.add_argument(
        "--action",
        choices=["ingest", "search"],
        required=True,
        help="Action to perform"
    )
    
    parser.add_argument(
        "--folder",
        help="Folder path for ingestion"
    )
    
    parser.add_argument(
        "--patterns",
        help="File patterns to match (comma-separated)",
        default="*.txt"
    )
    
    parser.add_argument(
        "--query",
        help="Search query"
    )
    
    parser.add_argument(
        "--num-results",
        type=int,
        default=5,
        help="Number of search results to return"
    )
    
    return parser.parse_args()

async def main():
    """Main entry point."""
    args = parse_args()
    
    cli = DocumentCLI()
    await cli.initialize()
    
    if args.action == "ingest":
        if not args.folder:
            logger.error("--folder is required for ingest action")
            return
            
        patterns = [p.strip() for p in args.patterns.split(",")]
        await cli.ingest_documents(args.folder, patterns)
        
    elif args.action == "search":
        if not args.query:
            logger.error("--query is required for search action")
            return
            
        await cli.search_documents(args.query, args.num_results)

if __name__ == "__main__":
    asyncio.run(main()) 