import os
import sys
import time
import datetime
import requests
import json
from openai import OpenAI
from openai.types.beta.threads import Run
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import anthropic
import logging
import asyncio

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import local modules
from tools import handle_tool_calls, get_tool_definitions
from terminalstyle import (
    print_assistant_response,
    print_system_message,
    print_code,
    clear_screen,
    print_welcome_message,
    print_divider,
    get_user_input,
    print_tool_usage,
)
from prompts import SUPER_ASSISTANT_INSTRUCTIONS, get_enhanced_prompt, get_tool_result_prompt, get_user_details
from tools.file_tools import read_thread_id, save_thread_id, clear_thread_id
from tools.universal_tool_handler import UniversalToolHandler
from tools.llm_config import LLM_PROVIDERS
from tools.user_state import get_user_state

class BaseLLMProvider:
    """Base class for all LLM providers"""
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config.get('base_url')
        self.model_name = config.get('model_name')
        self.api_key = os.getenv(config.get('api_key_env')) if config.get('api_key_env') else None
        self.client = None

    def generate_response(self, prompt: str) -> str:
        """Generate response using the LLM"""
        raise NotImplementedError("Each provider must implement generate_response")

    def initialize_client(self) -> None:
        """Initialize the API client"""
        raise NotImplementedError("Each provider must implement initialize_client")

class OpenAIProvider(BaseLLMProvider):
    def initialize_client(self) -> None:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=self.api_key)

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.initialize_client()  # Initialize client immediately

    def generate_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

class OllamaProvider(BaseLLMProvider):
    def initialize_client(self) -> None:
        # Ollama doesn't need a client initialization
        pass

    def log_api_interaction(self, request_data: dict, response: requests.Response = None, error: str = None) -> None:
        """Log complete HTTP API request/response to file."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "http_request": {
                "method": "POST",
                "url": f"{self.base_url}/api/generate",
                "headers": dict(response.request.headers) if response else {},
                "body": request_data
            },
            "http_response": {
                "status_code": response.status_code if response else None,
                "headers": dict(response.headers) if response else {},
                "body": response.json() if response else None
            } if response else None,
            "error": error
        }
        
        with open('agent_directory/ollama_api_log.json', 'a') as f:
            f.write(json.dumps(log_entry, indent=2) + "\n\n")

    def generate_response(self, prompt: str) -> str:
        try:
            request_data = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=request_data
            )
            response.raise_for_status()
            
            # Log successful interaction with full HTTP details
            self.log_api_interaction(request_data, response)
            
            return response.json()["response"]
        except Exception as e:
            # Log failed interaction
            self.log_api_interaction(request_data, error=str(e))
            return f"Error generating Ollama response: {str(e)}"

class AnthropicProvider(BaseLLMProvider):
    def initialize_client(self) -> None:
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        # Initialize Anthropic client
        self.client = anthropic.Client(api_key=self.api_key)

    def generate_response(self, prompt: str) -> str:
        if not self.client:
            self.initialize_client()
        response = self.client.messages.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content

# Factory to create providers
def create_llm_provider(provider_name: str) -> BaseLLMProvider:
    """Create an LLM provider instance based on provider name"""
    if provider_name not in LLM_PROVIDERS:
        raise ValueError(f"Unknown provider: {provider_name}")
    
    provider_map = {
        "openai": OpenAIProvider,
        "ollama": OllamaProvider,
        "anthropic": AnthropicProvider,
        # Add other providers here
    }
    
    provider_class = provider_map.get(provider_name)
    if not provider_class:
        raise ValueError(f"Provider {provider_name} not implemented yet")
    
    return provider_class(LLM_PROVIDERS[provider_name])

class AssistantManager:
    def __init__(self, llm_provider: str = "openai"):
        """Initialize the AssistantManager with specified LLM provider."""
        load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'), override=True)
        
        # Initialize LLM provider
        self.llm = create_llm_provider(llm_provider)
        self.provider_name = llm_provider
        self.tool_handler = UniversalToolHandler()
        self.user_state = get_user_state()
        
        # Only OpenAI uses assistants and threads
        if llm_provider == "openai":
            self.assistant_id = os.getenv("ASSISTANT_ID")
            if not self.assistant_id:
                raise ValueError("ASSISTANT_ID not found in environment variables")
            
            try:
                self.assistant = self.llm.client.beta.assistants.retrieve(self.assistant_id)
                self.update_assistant_configuration()
            except Exception as e:
                raise ValueError(f"Could not retrieve assistant with ID {self.assistant_id}: {str(e)}")
            
            self.thread_id = read_thread_id()
            if not self.thread_id:
                self.create_new_thread()
    
    def create_new_thread(self):
        """Create a new thread and save it."""
        thread = self.llm.client.beta.threads.create()
        self.thread_id = thread.id
        save_thread_id(self.thread_id)
        print_system_message("New conversation thread created.")
    
    def reset_thread(self):
        """Reset the conversation thread."""
        clear_thread_id()
        self.create_new_thread()
        print_system_message("Conversation thread has been reset.")
    
    def process_user_input(self, user_input: str) -> bool:
        """Process user input and return False if the conversation should end."""
        try:
            # Handle special commands
            if user_input.lower() in ['exit', 'quit']:
                print_system_message("Goodbye!")
                return False
            elif user_input.lower() == 'reset':
                self.reset_thread()
                return True
            
            if self.provider_name == "openai":
                # OpenAI-specific processing
                self.cancel_active_runs()
                self.llm.client.beta.threads.messages.create(
                    thread_id=self.thread_id,
                    role="user",
                    content=user_input
                )
                run = self.llm.client.beta.threads.runs.create(
                    thread_id=self.thread_id,
                    assistant_id=self.assistant.id
                )
                if completed_run := self.wait_for_completion(run.id):
                    messages = self.llm.client.beta.threads.messages.list(thread_id=self.thread_id)
                    for message in messages.data:
                        if message.role == "assistant":
                            print_assistant_response(message.content[0].text.value)
                            break
            else:
                # Direct LLM response for other providers
                print("\nDEBUG: Processing tool call...")
                tool_context = self.tool_handler.get_tool_description()
                
                # Get user details using the existing function
                user_details = get_user_details()
                
                # Update user state if needed
                if not user_details['core']['name'] or user_details['core']['name'] == 'Unknown User':
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.user_state.update_field("default", "name", "Bob"))
                    user_details = get_user_details()  # Refresh after update

                user_context = f"""
USER INFORMATION:
- Name: {user_details['core']['name']}
- Expertise Level: {user_details['core']['expertise_level']}
- Goals: {user_details['core']['goals']}

User Preferences:
{chr(10).join(f"  - {k}: {v}" for k, v in user_details['core']['preferences'].items())}

Current Context:
{chr(10).join(f"  - {k}: {v}" for k, v in user_details['core']['context'].items()) if user_details['core']['context'] else "  No specific context set"}

SYSTEM INFORMATION:
- OS Version: {user_details['system']['os_version']}
- Workspace: {user_details['system']['workspace_path']}
- Shell: {user_details['system']['shell']}
"""
                
                enhanced_prompt = get_enhanced_prompt(
                    model_name=self.llm.model_name,
                    tool_context=tool_context,
                    user_input=user_input,
                    user_context=user_context
                )
                print(f"\nDEBUG: Sending prompt to LLM...")
                response = self.llm.generate_response(enhanced_prompt)
                
                # Check for tool calls
                print(f"\nDEBUG: Checking for tool calls in response...")
                tool_call = self.tool_handler.parse_tool_call(response)
                if tool_call:
                    print(f"\nDEBUG: Executing tool: {tool_call['name']}")
                    tool_result = self.tool_handler.execute_tool(
                        tool_call["name"],
                        **tool_call["arguments"]
                    )
                    print(f"\nDEBUG: Tool result: {tool_result}")
                    final_prompt = get_tool_result_prompt(enhanced_prompt, tool_result)
                    response = self.llm.generate_response(final_prompt)
                
                print_assistant_response(response)

        except Exception as e:
            print_system_message(f"An error occurred: {str(e)}")
            if self.provider_name == "openai":
                print_system_message("Starting a new conversation...")
                self.reset_thread()

        return True

    def run(self) -> None:
        """Main conversation loop."""
        try:
            clear_screen()
            print_welcome_message()
            print_divider()

            while True:
                user_input = get_user_input()
                print_divider()
                
                if not self.process_user_input(user_input):
                    break
                    
                print_divider()

        except Exception as e:
            print_system_message(f"Fatal error: {str(e)}")
            sys.exit(1)

    def update_assistant_configuration(self) -> None:
        """Update the assistant with current tools and instructions."""
        try:
            print_system_message("Updating assistant configuration...")
            self.assistant = self.llm.client.beta.assistants.update(
                assistant_id=self.assistant_id,
                instructions=SUPER_ASSISTANT_INSTRUCTIONS,
                tools=get_tool_definitions(),
                model=self.llm.model_name
            )
            print_system_message("Assistant configuration updated successfully!")
        except Exception as e:
            print_system_message(f"Warning: Failed to update assistant configuration: {str(e)}")

    def cancel_active_runs(self):
        """Cancel any active runs on the current thread."""
        try:
            runs = self.llm.client.beta.threads.runs.list(thread_id=self.thread_id)
            for run in runs.data:
                if run.status in ["queued", "in_progress"]:
                    self.llm.client.beta.threads.runs.cancel(
                        thread_id=self.thread_id,
                        run_id=run.id
                    )
        except Exception as e:
            print_system_message(f"Error canceling runs: {str(e)}")
    
    def wait_for_completion(self, run_id: str, timeout: int = 300) -> Optional[Run]:
        """Wait for a run to complete."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            run = self.llm.client.beta.threads.runs.retrieve(
                thread_id=self.thread_id,
                run_id=run_id
            )
            
            if run.status == "completed":
                return run
            elif run.status == "requires_action":
                try:
                    tool_outputs = handle_tool_calls(run)
                    if tool_outputs:  # Only submit if we have outputs
                        run = self.llm.client.beta.threads.runs.submit_tool_outputs(
                            thread_id=self.thread_id,
                            run_id=run_id,
                            tool_outputs=tool_outputs
                        )
                except Exception as e:
                    print_system_message(f"Error handling tool calls: {str(e)}")
                    return None
            elif run.status in ["failed", "cancelled", "expired"]:
                print_system_message(f"Run ended with status: {run.status}")
                return None
                
            time.sleep(1)
        
        print_system_message("Run timed out")
        return None

def main():
    """Entry point of the application."""
    try:
        # Get LLM provider from environment or default to OpenAI
        llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        assistant_manager = AssistantManager(llm_provider)
        assistant_manager.run()
    except KeyboardInterrupt:
        print_system_message("\nGoodbye!")
    except Exception as e:
        print_system_message(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
