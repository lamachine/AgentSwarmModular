"""
Manages persistent user state across different LLM providers
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
import logging
import re
from services.db_service import DatabaseService
import time

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class UserState:
    """Manages user state with database storage"""
    
    # Core fields that should always be present
    CORE_FIELDS = {
        'name': 'Unknown User',
        'expertise_level': 'beginner',
        'goals': 'Not specified',
        'preferences': {},
        'context': {}
    }
    
    # System fields
    SYSTEM_FIELDS = {
        'os_version': None,
        'workspace_path': None,
        'shell_path': None
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = DatabaseService()
        self._initialized = False
        self._cache = {}
        self._cache_ttl = 60  # Cache TTL in seconds
        self._cache_timestamps = {}
        
    async def ensure_initialized(self):
        """Ensure database is initialized"""
        if not self._initialized:
            success = await self.db.initialize()
            if success:
                self._initialized = True
                return True
            return False
        return True
        
    async def cleanup(self):
        """Clean up resources"""
        if self._initialized:
            await self.db.cleanup()
            self._initialized = False
            self._cache = {}
            self._cache_timestamps = {}
            
    def _merge_state(self, current: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """Merge new state with current state, preserving structure."""
        merged = current.copy()
        
        # Update core fields
        for field in self.CORE_FIELDS:
            if field in new:
                if field in ['preferences', 'context']:
                    # Deep merge for dictionaries
                    if not isinstance(merged.get(field), dict):
                        merged[field] = {}
                    if isinstance(new[field], dict):
                        merged[field].update(new[field])
                else:
                    merged[field] = new[field]
            elif field not in merged:
                merged[field] = self.CORE_FIELDS[field]
        
        # Update system fields
        for field in self.SYSTEM_FIELDS:
            if field in new:
                merged[field] = new[field]
        
        # Update additional info
        if 'additional_info' not in merged:
            merged['additional_info'] = {}
        
        # Store non-core, non-system fields in additional_info
        for key, value in new.items():
            if (key not in self.CORE_FIELDS and 
                key not in self.SYSTEM_FIELDS and 
                key not in {'id', 'session_id', 'timestamp', 'additional_info'}):
                merged['additional_info'][key] = value
        
        return merged
        
    def _is_cache_valid(self, session_id: str) -> bool:
        """Check if cache entry is still valid."""
        if session_id not in self._cache_timestamps:
            return False
        return (time.time() - self._cache_timestamps[session_id]) < self._cache_ttl
        
    def _update_cache(self, session_id: str, state: Dict[str, Any]):
        """Update cache with new state."""
        self._cache[session_id] = state
        self._cache_timestamps[session_id] = time.time()
        
    def _invalidate_cache(self, session_id: str):
        """Invalidate cache for session."""
        self._cache.pop(session_id, None)
        self._cache_timestamps.pop(session_id, None)
        
    async def load_state(self, session_id: str) -> Dict[str, Any]:
        """Load user state from database with defaults."""
        try:
            if not await self.ensure_initialized():
                self.logger.error("Failed to initialize database")
                return self.CORE_FIELDS.copy()
            
            # Check cache first
            if session_id in self._cache and self._is_cache_valid(session_id):
                return self._cache[session_id]
            
            # Load from database
            state = await self.db.get_user_info(session_id)
            if not state:
                # Return defaults if no state exists
                return self.CORE_FIELDS.copy()
            
            # Ensure core fields exist with defaults
            merged_state = self._merge_state(self.CORE_FIELDS.copy(), state)
            
            # Update cache
            self._update_cache(session_id, merged_state)
            
            return merged_state
            
        except Exception as e:
            self.logger.error(f"Failed to load state: {str(e)}")
            return self.CORE_FIELDS.copy()
            
    async def save_state(self, session_id: str, state: Dict[str, Any]) -> bool:
        """Save user state to database."""
        try:
            self.logger.debug(f"Saving state for session {session_id}")
            if not await self.ensure_initialized():
                self.logger.error("Failed to initialize database")
                return False
            
            # Validate state
            if not isinstance(state, dict):
                raise ValueError("State must be a dictionary")
            
            # Check for required fields
            if any(key not in self.CORE_FIELDS and 
                  key not in self.SYSTEM_FIELDS and 
                  key not in {'id', 'session_id', 'timestamp', 'additional_info'} 
                  for key in state.keys()):
                raise ValueError("State contains invalid fields")
            
            self.logger.debug("Loading current state")
            # Merge with existing state
            current_state = await self.load_state(session_id)
            self.logger.debug("Merging states")
            merged_state = self._merge_state(current_state, state)
            
            # Update cache
            self.logger.debug("Updating cache")
            self._update_cache(session_id, merged_state)
            
            # Ensure JSONB fields are properly serialized
            self.logger.debug("Preparing JSONB fields")
            preferences = merged_state.get('preferences', {})
            context = merged_state.get('context', {})
            additional_info = merged_state.get('additional_info', {})
            
            if isinstance(preferences, str):
                preferences = json.loads(preferences)
            if isinstance(context, str):
                context = json.loads(context)
            if isinstance(additional_info, str):
                additional_info = json.loads(additional_info)
            
            # Save to database
            self.logger.debug("Storing in database")
            result = await self.db.store_user_info(
                session_id=session_id,
                name=merged_state.get('name'),
                expertise_level=merged_state.get('expertise_level'),
                goals=merged_state.get('goals'),
                preferences=preferences,
                context=context,
                os_version=merged_state.get('os_version'),
                workspace_path=merged_state.get('workspace_path'),
                shell_path=merged_state.get('shell_path'),
                additional_info=additional_info
            )
            
            self.logger.debug(f"Save completed with result: {result}")
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Failed to save state: {str(e)}")
            # Invalidate cache on error
            self._invalidate_cache(session_id)
            raise  # Re-raise the exception instead of returning False
            
    async def update_field(self, session_id: str, field: str, value: Any) -> str:
        """Update a specific field in the user state."""
        try:
            await self.ensure_initialized()
            current_state = await self.load_state(session_id)
            
            # Handle nested fields (e.g., preferences.theme)
            if '.' in field:
                parent, child = field.split('.', 1)
                if parent in current_state:
                    if not isinstance(current_state[parent], dict):
                        current_state[parent] = {}
                    current_state[parent][child] = value
                else:
                    return f"Invalid field: {field}"
            else:
                # Handle core fields
                if field in self.CORE_FIELDS:
                    current_state[field] = value
                # Handle system fields
                elif field in self.SYSTEM_FIELDS:
                    current_state[field] = value
                else:
                    # Store in additional_info
                    if 'additional_info' not in current_state:
                        current_state['additional_info'] = {}
                    current_state['additional_info'][field] = value
                
            success = await self.save_state(session_id, current_state)
            if success:
                return f"Updated {field}"
            else:
                return f"Failed to update {field}"
                
        except Exception as e:
            self.logger.error(f"Failed to update field: {str(e)}")
            return f"Error updating {field}: {str(e)}"
            
    async def update_from_prompt(self, session_id: str, prompt_text: str) -> bool:
        """Update state from prompt text."""
        try:
            await self.ensure_initialized()
            
            # Extract system information
            system_info = {}
            
            # OS version
            os_match = re.search(r"user's OS version is ([^.]+)", prompt_text)
            if os_match:
                system_info['os_version'] = os_match.group(1)
            
            # Workspace path
            workspace_match = re.search(r"absolute path of the user's workspace is ([^.]+)", prompt_text)
            if workspace_match:
                system_info['workspace_path'] = workspace_match.group(1)
            
            # Shell path
            shell_match = re.search(r"user's shell is ([^.]+)", prompt_text)
            if shell_match:
                system_info['shell_path'] = shell_match.group(1)
            
            # Extract personal information
            personal_info = {}
            
            # Name
            name_match = re.search(r"my name is ([^.]+)", prompt_text, re.IGNORECASE)
            if name_match:
                personal_info['name'] = name_match.group(1).strip()
            
            # Expertise level
            expertise_match = re.search(r"expertise level is ([^.]+)", prompt_text, re.IGNORECASE)
            if expertise_match:
                personal_info['expertise_level'] = expertise_match.group(1).strip()
            
            # Goals
            goals_match = re.search(r"goals? (?:is|are) ([^.]+)", prompt_text, re.IGNORECASE)
            if goals_match:
                personal_info['goals'] = goals_match.group(1).strip()
            
            # Combine and save
            state = {**system_info, **personal_info}
            return await self.save_state(session_id, state)
            
        except Exception as e:
            self.logger.error(f"Failed to update from prompt: {str(e)}")
            return False

    async def import_from_json(self, session_id: str, json_path: str) -> bool:
        """Import user details from a JSON file."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Convert preferences string to dictionary if needed
            if isinstance(data.get('preferences'), str):
                prefs_text = data['preferences']
                prefs_dict = {}
                for pref in prefs_text.split('  '):
                    if pref.strip():
                        if pref[0].isdigit():
                            key = f"preference_{pref[0]}"
                            value = pref[1:].strip()
                        else:
                            key = f"preference_{len(prefs_dict) + 1}"
                            value = pref.strip()
                        prefs_dict[key] = value
                data['preferences'] = prefs_dict
            
            return await self.save_state(session_id, data)
            
        except Exception as e:
            self.logger.error(f"Failed to import from JSON: {str(e)}")
            return False

# Singleton instance
_user_state = None

def get_user_state() -> UserState:
    """Get the singleton UserState instance."""
    global _user_state
    if _user_state is None:
        _user_state = UserState()
    return _user_state

# Backward compatibility function
def update_user_state(field: str, value: str) -> str:
    """Update a field in the user state (backward compatibility)"""
    state = get_user_state()
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Create a new loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(state.update_field("default", field, value))