import json
from typing import Dict, Any, List, Optional
from .tool_handler import get_function_map
from .tool_definitions import get_tool_definitions
from .rag_tools import search_local_documents

class UniversalToolHandler:
    """Handles tools for any LLM provider"""
    def __init__(self):
        self.function_map = get_function_map()
        self.tool_definitions = get_tool_definitions()
        self.tools = {
            "search_local_documents": search_local_documents,
            # ... existing tools ...
        }
        
    def get_tool_description(self) -> str:
        """Get a description of available tools for context"""
        tool_desc = "Available tools:\n"
        for tool in self.tool_definitions:
            if tool["type"] == "function":
                func = tool["function"]
                tool_desc += f"- {func['name']}: {func['description']}\n"
        return tool_desc

    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a specific tool with given arguments"""
        if tool_name not in self.function_map:
            return f"Error: Tool '{tool_name}' not found"
        
        try:
            result = self.function_map[tool_name](**kwargs)
            return result
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def parse_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse tool call from response."""
        print("\nDEBUG: Starting parse_tool_call")
        print(f"\nDEBUG: Response to parse: {response}")
        
        # Look for tool call patterns
        if "Use tool:" in response:
            print("\nDEBUG: Found 'Use tool:' pattern")
            try:
                # Extract tool call
                tool_part = response.split("Use tool:")[1].strip()
                print(f"\nDEBUG: Extracted tool part: {tool_part}")
                
                # Parse function name and args
                func_name = tool_part.split("(")[0].strip()
                args_str = tool_part[tool_part.find("(")+1:tool_part.rfind(")")]
                print(f"\nDEBUG: Function name: {func_name}")
                print(f"\nDEBUG: Arguments string: {args_str}")
                
                # Parse arguments
                args = {}
                if args_str:
                    # Split by commas, but not within quotes
                    import re
                    arg_pairs = re.findall(r'(\w+)\s*=\s*(?:"([^"]*)"|\{([^}]*)\}|([^,\s]*))', args_str)
                    for pair in arg_pairs:
                        key = pair[0]
                        # Take the first non-empty value from the captured groups
                        value = next(v for v in pair[1:] if v)
                        # Convert to appropriate type if needed
                        try:
                            if value.isdigit():
                                value = int(value)
                            elif value.lower() in ['true', 'false']:
                                value = value.lower() == 'true'
                        except:
                            pass
                        args[key] = value
                
                print(f"\nDEBUG: Parsed arguments: {args}")
                return {
                    "name": func_name,
                    "arguments": args
                }
            except Exception as e:
                print(f"\nDEBUG: Error parsing tool call: {str(e)}")
                return None
        
        print("\nDEBUG: No tool call pattern found")
        return None