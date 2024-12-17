from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict
from functools import lru_cache

@dataclass
class ToolInfo:
    function: Callable
    version: str
    description: str
    last_updated: datetime

class ToolRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'tools'):
            self.tools: Dict[str, ToolInfo] = {}

    def register_tool(self, name: str, func: Callable, version: str, description: str):
        self.tools[name] = ToolInfo(
            function=func,
            version=version,
            description=description,
            last_updated=datetime.now()
        )

    def get_tool(self, name: str) -> ToolInfo:
        return self.tools.get(name)

@register_tool(
    name="your_api_function",
    version="1.0.0",
    description="Description of what this tool does"
)
def your_api_function():
    # Function implementation
    pass