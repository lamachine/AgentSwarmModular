import asyncio
import json
from functools import lru_cache
from .file_tools import read_file, write_file, list_files
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List, Dict, Any, Optional
from openai.types.beta.threads import Run
from .gmail_tools import (
    list_emails, read_email, send_email, search_emails,
    get_profile, manage_labels, manage_drafts, manage_threads,
    batch_modify_messages, get_message_attachment
)
from .calendar_tools import (
    list_events, create_event, delete_event, update_event,
    manage_calendar_acl, manage_calendar_list, quick_add_event,
    move_event, get_event_instances, import_event, query_freebusy,
    manage_settings, get_calendar_colors
)
from .reminders_tools import create_reminder, complete_reminder, add_notes_to_reminder, list_reminders
from .sheets_tools import (
    create_spreadsheet, read_range, write_range, append_values,
    clear_range, batch_update, get_spreadsheet_info
)
from .drive_tools import (
    list_files as list_drive_files,
    upload_file as upload_drive_file,
    download_file as download_drive_file,
    create_folder as create_drive_folder,
    delete_file as delete_drive_file,
    share_file as share_drive_file,
    move_file as move_drive_file,
    get_file_info as get_drive_file_info
)
from .slides_tools import (
    create_presentation,
    get_presentation,
    create_slide,
    add_text_box
)
from .perplexity_tools import ask_perplexity, ask_perplexity_with_context
from .interpreter_tools import execute_code, execute_python_with_vars
from .firecrawl_tools import (
    scrape_url,
    crawl_url,
    check_crawl_status,
    map_url,
    batch_scrape
)
from .browser_tools import browse_web

# Cache the function mapping
@lru_cache(maxsize=1)
def get_function_map():
    return {
        "read_file": read_file,
        "write_file": write_file,
        "list_files": list_files,
        "list_emails": list_emails,
        "read_email": read_email,
        "send_email": send_email,
        "search_emails": search_emails,
        "get_profile": get_profile,
        "manage_labels": manage_labels,
        "manage_drafts": manage_drafts,
        "manage_threads": manage_threads,
        "batch_modify_messages": batch_modify_messages,
        "get_message_attachment": get_message_attachment,
        "list_events": list_events,
        "create_event": create_event,
        "delete_event": delete_event,
        "update_event": update_event,
        "manage_calendar_acl": manage_calendar_acl,
        "manage_calendar_list": manage_calendar_list,
        "quick_add_event": quick_add_event,
        "move_event": move_event,
        "get_event_instances": get_event_instances,
        "import_event": import_event,
        "query_freebusy": query_freebusy,
        "manage_settings": manage_settings,
        "get_calendar_colors": get_calendar_colors,
        "create_reminder": create_reminder,
        "complete_reminder": complete_reminder,
        "add_notes_to_reminder": add_notes_to_reminder,
        "list_reminders": list_reminders,
        "create_spreadsheet": create_spreadsheet,
        "read_range": read_range,
        "write_range": write_range,
        "append_values": append_values,
        "clear_range": clear_range,
        "batch_update": batch_update,
        "get_spreadsheet_info": get_spreadsheet_info,
        "list_drive_files": list_drive_files,
        "upload_drive_file": upload_drive_file,
        "download_drive_file": download_drive_file,
        "create_drive_folder": create_drive_folder,
        "delete_drive_file": delete_drive_file,
        "share_drive_file": share_drive_file,
        "move_drive_file": move_drive_file,
        "get_drive_file_info": get_drive_file_info,
        "create_presentation": create_presentation,
        "get_presentation": get_presentation,
        "create_slide": create_slide,
        "add_text_box": add_text_box,
        "ask_perplexity": ask_perplexity,
        "ask_perplexity_with_context": ask_perplexity_with_context,
        "execute_code": execute_code,
        "execute_python_with_vars": execute_python_with_vars,
        "scrape_url": scrape_url,
        "crawl_url": crawl_url,
        "check_crawl_status": check_crawl_status,
        "map_url": map_url,
        "batch_scrape": batch_scrape,
        "browse_web": browse_web,
    }

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def handle_tool_calls(run: Run) -> List[Dict[str, Any]]:
    """
    Handle tool calls from the assistant.
    """
    tool_outputs = []
    function_map = get_function_map()
    
    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        if function_name in function_map:
            try:
                func = function_map[function_name]
                # Check if the function is async
                if asyncio.iscoroutinefunction(func):
                    output = await func(**function_args)
                else:
                    output = func(**function_args)
                    
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": output
                })
            except Exception as e:
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": f"Error executing {function_name}: {str(e)}"
                })
    
    return tool_outputs