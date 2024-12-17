"""Verify user state in database."""

import asyncio
import logging
from tools.user_state import get_user_state
import platform
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def verify_state():
    print("Starting verification...")  # Debug print
    logger.debug("Starting user state verification")
    
    # Get user state instance
    state = get_user_state()
    logger.debug("Got user state instance")
    
    # Initialize database
    await state.ensure_initialized()
    logger.debug("Database initialized")
    
    # First load current state to preserve core fields
    current_state = await state.load_state("default")
    print(f"Loaded state: {current_state}")  # Debug print
    
    # Add system fields while preserving core fields
    system_info = {
        'os_version': f"{platform.system()} {platform.release()}",
        'workspace_path': os.path.abspath(os.getcwd()),
        'shell_path': os.environ.get('SHELL') or os.environ.get('COMSPEC')
    }
    
    # Merge with current state
    merged_state = {**current_state, **system_info}
    print(f"Merged state: {merged_state}")  # Debug print
    
    # Save merged state
    await state.save_state("default", merged_state)
    
    # Load and display current state
    current_state = await state.load_state("default")
    logger.debug(f"Loaded state: {current_state}")
    
    print("\nCurrent User State in Database:")
    print("=" * 30 + "\n")
    
    print("Core Fields:")
    print(f"Name: {current_state.get('name')}")
    print(f"Expertise Level: {current_state.get('expertise_level')}")
    print(f"Goals: {current_state.get('goals')}\n")
    
    print("Preferences:")
    for key, value in current_state.get('preferences', {}).items():
        print(f"  {key}: {value}")
    
    print("\nContext:")
    context = current_state.get('context', {})
    if context:
        for key, value in context.items():
            print(f"  {key}: {value}")
    else:
        print("  No context set")
    
    print("\nSystem Fields:")
    print(f"OS Version: {current_state.get('os_version')}")
    print(f"Workspace: {current_state.get('workspace_path')}")
    print(f"Shell: {current_state.get('shell_path')}")
    
    print("\nAdditional Info:")
    print(current_state.get('additional_info', {}))

if __name__ == "__main__":
    asyncio.run(verify_state()) 