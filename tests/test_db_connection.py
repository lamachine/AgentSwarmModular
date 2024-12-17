"""Test PostgreSQL connection."""

import asyncio
import asyncpg
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_connection():
    # Load environment variables
    load_dotenv()
    
    # Get connection details
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = int(os.getenv('POSTGRES_PORT', '5432'))
    database = os.getenv('POSTGRES_DB', 'ai_memory')
    user = os.getenv('POSTGRES_USER', 'root')
    password = os.getenv('POSTGRES_PASSWORD', 'password')
    
    logger.info(f"Connecting to PostgreSQL at {host}:{port}")
    
    try:
        # Try to connect
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        logger.info("Successfully connected to database!")
        
        # Test a simple query
        version = await conn.fetchval('SELECT version();')
        logger.info(f"PostgreSQL version: {version}")
        
        await conn.close()
        logger.info("Connection closed")
        
    except Exception as e:
        logger.error(f"Failed to connect: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_connection()) 