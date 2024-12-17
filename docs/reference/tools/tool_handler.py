import json
from functools import lru_cache
from .file_tools import read_file, write_file, list_files, open_container_cli
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List, Dict, Any, Optional
from openai.types.beta.threads import Run
from .perplexity_api_tools import perplexity_chat
from .google_api_tools import (
    # Core functions
    get_credentials, get_services,
    
    # Gmail Draft functions
    gmail_drafts_get,
    gmail_drafts_list,
    gmail_drafts_send,
    gmail_drafts_update,
    gmail_drafts_create,
    gmail_drafts_delete,
    
    # Gmail History functions
    gmail_history_list,
    
    # Gmail Labels functions
    gmail_labels_create,
    gmail_labels_delete,
    gmail_labels_get,
    gmail_labels_list,
    gmail_labels_modify,
    
    # Gmail Messages functions
    gmail_messages_create,
    gmail_messages_delete,
    gmail_messages_import,
    gmail_messages_list,
    gmail_messages_send,
    gmail_messages_trash,
    gmail_messages_untrash,
    gmail_messages_batch_delete,
    gmail_messages_get,
    gmail_messages_attachments_get,
    
    # Gmail Settings functions
    gmail_settings_get_autoforwarding,
    gmail_settings_update_autoforwarding,
    gmail_settings_update_vacation,
    gmail_settings_get_vacation,
    
    # Gmail Settings Filters functions
    gmail_settings_filters_create,
    gmail_settings_filters_delete,
    gmail_settings_filters_get,
    gmail_settings_filters_list,
    
    # Gmail Threads functions
    gmail_threads_delete,
    gmail_threads_get,
    gmail_threads_list,
    gmail_threads_trash,
    gmail_threads_untrash,
    
    # Tasks functions
    tasks_tasklists_delete,
    tasks_tasklists_get,
    tasks_tasklists_insert,
    tasks_tasklists_list,
    tasks_tasklists_patch,
    tasks_tasklists_update,
    tasks_clear,
    tasks_delete,
    tasks_get,
    tasks_insert,
    tasks_list,
    tasks_move,
    tasks_patch,
    tasks_update,
    
    # Calendar functions
    calendar_colors_get,
    calendar_events_delete,
    calendar_events_get,
    calendar_events_instances,
    calendar_events_list,
    calendar_events_create,
    calendar_events_move,
    calendar_events_patch,
    calendar_events_quick_add,
    calendar_events_update,
    calendar_freebusy_query
)
from .llm_tools import llm_manager
from .user_state import get_user_state
from .searxng_tools import searxng_search
from .rag_tools import search_local_documents, RAGTool
from .time_tools import get_current_datetime

# Global user state instance
_user_state = get_user_state()

# Initialize RAG tool
_rag_tool = RAGTool()

async def update_user_state_async(field: str, value: str) -> str:
    """Update a field in the user state."""
    return await _user_state.update_field("default", field, value)

def update_user_state(field: str, value: str) -> str:
    """Synchronous wrapper for updating user state."""
    import asyncio
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Create a new loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(update_user_state_async(field, value))

def ingest_documents(folder_path: str, patterns: Optional[List[str]] = None) -> bool:
    """Tool function to ingest documents into RAG system."""
    return _rag_tool.ingest_documents(folder_path, patterns)

def search_local_documents(query: str, num_results: int = 5) -> Optional[str]:
    """Tool function to search local documents."""
    return _rag_tool.query_documents(query, num_results)

@lru_cache(maxsize=1)
def get_function_map():
    return {
        # Time functions
        "get_current_datetime": get_current_datetime,
        
        # Core file functions
        "read_file": read_file,
        "write_file": write_file,
        "list_files": list_files,
        
        # Container CLI function
        "open_container_cli": open_container_cli,

        "perplexity_chat": perplexity_chat,

        
        # Gmail Draft functions
        "gmail_drafts_get": gmail_drafts_get,
        "gmail_drafts_list": gmail_drafts_list,
        "gmail_drafts_send": gmail_drafts_send,
        "gmail_drafts_update": gmail_drafts_update,
        "gmail_drafts_create": gmail_drafts_create,
        "gmail_drafts_delete": gmail_drafts_delete,
        
        # Gmail History functions
        "gmail_history_list": gmail_history_list,
        
        # Gmail Labels functions
        "gmail_labels_create": gmail_labels_create,
        "gmail_labels_delete": gmail_labels_delete,
        "gmail_labels_get": gmail_labels_get,
        "gmail_labels_list": gmail_labels_list,
        "gmail_labels_modify": gmail_labels_modify,
        
        # Gmail Messages functions
        "gmail_messages_create": gmail_messages_create,
        "gmail_messages_delete": gmail_messages_delete,
        "gmail_messages_import": gmail_messages_import,
        "gmail_messages_list": gmail_messages_list,
        "gmail_messages_send": gmail_messages_send,
        "gmail_messages_trash": gmail_messages_trash,
        "gmail_messages_untrash": gmail_messages_untrash,
        "gmail_messages_batch_delete": gmail_messages_batch_delete,
        "gmail_messages_get": gmail_messages_get,
        "gmail_messages_attachments_get": gmail_messages_attachments_get,
        
        # Gmail Settings functions
        "gmail_settings_get_autoforwarding": gmail_settings_get_autoforwarding,
        "gmail_settings_update_autoforwarding": gmail_settings_update_autoforwarding,
        "gmail_settings_update_vacation": gmail_settings_update_vacation,
        "gmail_settings_get_vacation": gmail_settings_get_vacation,
        
        # Gmail Settings Filters functions
        "gmail_settings_filters_create": gmail_settings_filters_create,
        "gmail_settings_filters_delete": gmail_settings_filters_delete,
        "gmail_settings_filters_get": gmail_settings_filters_get,
        "gmail_settings_filters_list": gmail_settings_filters_list,
        
        # Gmail Threads functions
        "gmail_threads_delete": gmail_threads_delete,
        "gmail_threads_get": gmail_threads_get,
        "gmail_threads_list": gmail_threads_list,
        "gmail_threads_trash": gmail_threads_trash,
        "gmail_threads_untrash": gmail_threads_untrash,
        
        # Tasks functions
        "tasks_tasklists_delete": tasks_tasklists_delete,
        "tasks_tasklists_get": tasks_tasklists_get,
        "tasks_tasklists_insert": tasks_tasklists_insert,
        "tasks_tasklists_list": tasks_tasklists_list,
        "tasks_tasklists_patch": tasks_tasklists_patch,
        "tasks_tasklists_update": tasks_tasklists_update,
        "tasks_clear": tasks_clear,
        "tasks_delete": tasks_delete,
        "tasks_get": tasks_get,
        "tasks_insert": tasks_insert,
        "tasks_list": tasks_list,
        "tasks_move": tasks_move,
        "tasks_patch": tasks_patch,
        "tasks_update": tasks_update,
        
        # Calendar functions
        "calendar_colors_get": calendar_colors_get,
        "calendar_events_delete": calendar_events_delete,
        "calendar_events_get": calendar_events_get,
        "calendar_events_instances": calendar_events_instances,
        "calendar_events_list": calendar_events_list,
        "calendar_events_create": calendar_events_create,
        "calendar_events_move": calendar_events_move,
        "calendar_events_patch": calendar_events_patch,
        "calendar_events_quick_add": calendar_events_quick_add,
        "calendar_events_update": calendar_events_update,
        "calendar_freebusy_query": calendar_freebusy_query,
        
        # Container CLI function
        "open_container_cli": open_container_cli,
        
        # LLM Manager function
        "llm_manager": llm_manager,
        
        # User State function
        "update_user_state": update_user_state,
        
        # Search functions
        "searxng_search": searxng_search,
        
        # RAG tool
        "search_local_documents": search_local_documents,
        
        # Ingest documents function
        "ingest_documents": ingest_documents
    }

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def handle_tool_calls(run: Run) -> List[Dict[str, Any]]:
    """Handle tool calls from the assistant."""
    print("\nDEBUG: Starting tool call handling...")
    tool_outputs = []
    function_map = get_function_map()
    
    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
        try:
            function_name = tool_call.function.name
            print(f"\nDEBUG: Processing function: {function_name}")
            function_args = json.loads(tool_call.function.arguments)
            
            # Execute function if it exists
            if function_name in function_map:
                try:
                    print(f"\nDEBUG: Executing {function_name} with args: {function_args}")
                    output = function_map[function_name](**function_args)
                    print(f"\nDEBUG: Function output: {output}")
                except Exception as e:
                    output = f"Error executing {function_name}: {str(e)}"
                    print(f"\nDEBUG: Function error: {output}")
            else:
                output = f"Function {function_name} not found"
                print(f"\nDEBUG: {output}")
            
            # Always append an output for each tool call
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": output
            })
            
        except Exception as e:
            # Ensure we still return an output even if JSON parsing fails
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": f"Error processing tool call: {str(e)}"
            })
    
    return tool_outputs