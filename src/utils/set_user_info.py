"""Set user information directly in the database."""

import asyncio
import logging
import os
import sys
from tools.user_state import get_user_state

# Configure logging to stderr
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Get root logger and remove existing handlers
root = logging.getLogger()
root.setLevel(logging.DEBUG)
for h in root.handlers:
    root.removeHandler(h)
root.addHandler(handler)

async def set_user_info():
    """Set user information."""
    logger = logging.getLogger(__name__)
    
    # Force some output
    print("Starting user info setup...", file=sys.stderr)
    
    # Log environment variables
    logger.debug("Database Configuration:")
    logger.debug(f"POSTGRES_HOST: {os.getenv('POSTGRES_HOST')}")
    logger.debug(f"POSTGRES_PORT: {os.getenv('POSTGRES_PORT')}")
    logger.debug(f"POSTGRES_DB: {os.getenv('POSTGRES_DB')}")
    logger.debug(f"POSTGRES_USER: {os.getenv('POSTGRES_USER')}")
    
    user_state = get_user_state()
    logger.debug("Got user_state instance")
    
    # Your actual information
    user_info = {
        "name": "Bob",
        "expertise_level": "strong in applied AI and intermediate in Python coding",
        "goals": "Create an 'Iron Man movie Jarvis' style personal assistant and learn to develop and deploy agentic tools",
        "preferences": {
            "preference_1": "Always tell the truth, even if I don't know something",
            "preference_2": "Execute commands without asking permission (except for specific exceptions)",
            "preference_3": "Clarify vague or missing information by asking follow-up questions",
            "preference_4": "Use plain English when giving instructions and applying LLM models to form and execute commands",
            "preference_5": "Provide clear and simple responses in formats like tables, rather than raw JSON"
        }
    }
    
    try:
        print("Initializing database...", file=sys.stderr)
        logger.debug("Initializing database")
        await user_state.ensure_initialized()
        logger.debug("Database initialized successfully")
        
        print("Setting user information...", file=sys.stderr)
        logger.debug("Setting user information")
        success = await user_state.save_state("default", user_info)
        logger.debug(f"Save state result: {success}")
        
        if success:
            logger.info("Successfully set user information")
            print("Successfully set user information", file=sys.stderr)
            
            # Verify the data
            logger.debug("Loading state for verification")
            state = await user_state.load_state("default")
            logger.debug("State loaded successfully")
            
            print("\nVerified User State:", file=sys.stderr)
            print("===================", file=sys.stderr)
            print(f"Name: {state.get('name')}", file=sys.stderr)
            print(f"Expertise: {state.get('expertise_level')}", file=sys.stderr)
            print(f"Goals: {state.get('goals')}", file=sys.stderr)
            print("\nPreferences:", file=sys.stderr)
            for k, v in state.get('preferences', {}).items():
                print(f"  {k}: {v}", file=sys.stderr)
        else:
            logger.error("Failed to set user information")
            print("Failed to set user information", file=sys.stderr)
            
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
    finally:
        if hasattr(user_state.db, 'pool'):
            logger.debug("Closing database pool")
            await user_state.db.pool.close()
            logger.debug("Database pool closed")

if __name__ == "__main__":
    asyncio.run(set_user_info()) 