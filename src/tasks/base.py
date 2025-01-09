from abc import ABC, abstractmethod
from typing import Dict, Any

class Task(ABC):
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Any:
        """Execute the task with given context"""
        pass 