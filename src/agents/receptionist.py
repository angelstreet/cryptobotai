# receptionist.py
from typing import Dict, Any, Optional, List
from crewai import Agent, Task
from crewai.tools import BaseTool

class WelcomeTool(BaseTool):
    name: str = "welcome"
    description: str = "Display welcome message and available commands"
    
    def _run(self) -> str:
        """Return welcome message and available commands"""
        message = "=== AI Crypto Agency ===\n\n"
        
        commands = {
            'portfolio': 'Show portfolio overview',
            'trade': 'Execute live trade',
            'backtest': 'Run backtest simulation',
            'virtual': 'Run virtual trade in sandbox',
            'help': 'Show this help message'
        }
        
        message += (
            "Hi, crypto lover! How can I help you?\n\n"
            "Available commands:\n"
        )
        
        for cmd, desc in commands.items():
            message += f"• {cmd:<10} - {desc}\n"
            
        print(message)  # Print directly from the tool
        return message  # Still return for potential logging/chaining

class ReceptionistAgent(Agent):
    """Frontend agent handling user interactions"""
    
    def __init__(self, config):
        super().__init__(
            name="Receptionist",
            role="Client Interface Specialist",
            goal="Welcome users and help them navigate the trading system",
            backstory="An expert in user interaction and crypto trading assistance",
            tools=[WelcomeTool()],
            llm=config.llm,
            verbose=config.debug
        )

    def execute_task(self, task: Task, context: Optional[str] = None, tools: Optional[List[BaseTool]] = None) -> str:
        """Execute task without LLM for welcome message"""
        if "welcome" in task.description.lower():
            tool = WelcomeTool()
            return tool._run()
        return "Unknown task"