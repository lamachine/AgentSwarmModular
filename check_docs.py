from services.db_service import DatabaseService
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_docs():
    try:
        db = DatabaseService()
        await db.initialize()
        
        # Get all document IDs first
        async with db.pool.acquire() as conn:
            records = await conn.fetch("SELECT doc_id, title FROM document_records")
        
        print(f'Found {len(records)} documents:')
        for record in records:
            print(f'- {record["title"]} ({record["doc_id"]})')
            
    except Exception as e:
        logger.error(f"Error checking documents: {str(e)}")
        raise

if __name__ == '__main__':
    asyncio.run(check_docs()) 