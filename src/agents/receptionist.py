# receptionist.py
from typing import Dict, Any, Optional
from crewai import Agent
from crewai.tools import BaseTool
from pydantic import Field, BaseModel
from src.tools.display import print_header

class WelcomeOutput(BaseModel):
    message: str
    commands: Dict[str, str]

class WelcomeTool(BaseTool):
    name: str = "welcome"
    description: str = "Display welcome message and available commands"
    
    def _execute(self) -> WelcomeOutput:
        """Execute the welcome tool functionality"""
        print_header("AI Crypto Agency")
        
        commands = {
            'portfolio': 'Show portfolio overview',
            'trade': 'Execute live trade',
            'backtest': 'Run backtest simulation',
            'virtual': 'Run virtual trade in sandbox',
            'help': 'Show this help message'
        }
        
        message = (
            "Hi, crypto lover! How can I help you?\n\n"
            "Available commands:\n"
        )
        
        for cmd, desc in commands.items():
            message += f"• {cmd:<10} - {desc}\n"
        
        return WelcomeOutput(
            message=message,
            commands=commands
        )

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

    def execute(self, task: str) -> Dict[str, Any]:
        """Execute the given task"""
        if "welcome" in task.lower():
            tool = WelcomeTool()
            result = tool._execute()
            return result.dict()
        return {"error": "Unknown task"}