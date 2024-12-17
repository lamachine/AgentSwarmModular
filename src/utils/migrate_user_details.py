"""Migrate user details from JSON file to database."""

import asyncio
import os
import json
import logging
from tools.user_state import get_user_state

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def migrate_user_details():
    """Migrate user details from JSON to database."""
    logger = logging.getLogger(__name__)
    logger.debug("Starting migration process")
    
    user_state = get_user_state()
    json_path = "agent_directory/user_details.json"
    
    try:
        # Check if file exists
        if not os.path.exists(json_path):
            logger.error(f"File not found: {json_path}")
            return
            
        logger.debug(f"Reading file: {json_path}")
        with open(json_path, 'r') as f:
            data = json.load(f)
        logger.debug(f"File contents: {json.dumps(data, indent=2)}")
        
        # Initialize database
        logger.debug("Initializing database connection")
        await user_state.ensure_initialized()
        logger.debug("Database initialized")
        
        # Import the data
        logger.debug("Importing data to database")
        success = await user_state.import_from_json("default", json_path)
        
        if success:
            logger.info("✓ Successfully migrated user details to database")
            # Verify the data
            state = await user_state.load_state("default")
            logger.debug(f"Loaded state: {json.dumps(state, indent=2)}")
            
            print("\nVerified user state:")
            print(f"Name: {state.get('name', 'Not set')}")
            print(f"Expertise: {state.get('expertise_level', 'Not set')}")
            print(f"Goals: {state.get('goals', 'Not set')}")
            print("\nPreferences:")
            for k, v in state.get('preferences', {}).items():
                print(f"  {k}: {v}")
            
            # Delete the JSON file
            try:
                os.remove(json_path)
                logger.info(f"✓ Deleted {json_path}")
            except Exception as e:
                logger.error(f"Failed to delete {json_path}: {str(e)}")
        else:
            logger.error("Failed to migrate user details")
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON file: {str(e)}")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}", exc_info=True)
    finally:
        # Close database connection
        if hasattr(user_state.db, 'pool'):
            await user_state.db.pool.close()

if __name__ == "__main__":
    asyncio.run(migrate_user_details()) 