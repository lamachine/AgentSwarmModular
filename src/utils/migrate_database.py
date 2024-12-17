"""Migrate user data from old schema to new schema."""

import asyncio
import logging
from services.db_service import DatabaseService

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def migrate_database():
    """Migrate user data to new schema."""
    try:
        db = DatabaseService()
        await db.initialize()
        
        # Drop existing table
        async with db.pool.acquire() as conn:
            logger.info("Dropping existing user_info table...")
            await conn.execute('DROP TABLE IF EXISTS user_info;')
            
            logger.info("Creating new user_info table...")
            await conn.execute('''
                CREATE TABLE user_info (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL DEFAULT 'Unknown User',
                    expertise_level TEXT NOT NULL DEFAULT 'beginner',
                    goals TEXT NOT NULL DEFAULT 'Not specified',
                    preferences JSONB DEFAULT '{}',
                    context JSONB DEFAULT '{}',
                    os_version TEXT,
                    workspace_path TEXT,
                    shell_path TEXT,
                    additional_info JSONB,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            
            logger.info("✓ Successfully created new user_info table")
            
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise
    finally:
        if hasattr(db, 'pool'):
            await db.pool.close()

if __name__ == "__main__":
    asyncio.run(migrate_database()) 