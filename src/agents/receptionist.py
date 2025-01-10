# receptionist.py
from typing import Dict, Any, Optional
from crewai import Agent
from crewai.tools import BaseTool
from pydantic import Field, BaseModel

class WelcomeOutput(BaseModel):
    message: str
    commands: Dict[str, str]

class CustomWelcomeTool(BaseTool):
    name: str = "welcome"
    description: str = "Display welcome message and available commands"
    
    def __init__(self, welcome_config=None):
        super().__init__()
        self.welcome_config = welcome_config or {}
    
    def _execute(self, *args, **kwargs) -> WelcomeOutput:
        """Execute the welcome tool functionality"""
        # Get custom message or use default
        title = self.welcome_config.get('title', '=== AI Crypto Agency ===')
        greeting = self.welcome_config.get('greeting', 'Welcome crypto lover! How can I help you?\n')
        commands_title = self.welcome_config.get('commands_title', '=== Available Commands ===')
        
        welcome_message = [
            f"\n{title}",
            f"{greeting}",
            f"{commands_title}"
        ]
        
        # Get custom commands or use defaults
        commands = self.welcome_config.get('commands', {
            'portfolio': 'Show portfolio overview',
            'trade': 'Execute live trade',
            'backtest': 'Run backtest simulation',
            'virtual': 'Run virtual trade in sandbox',
            'help': 'Show this help message'
        })
        
        command_lines = [
            f"{cmd:<10} - {desc}" 
            for cmd, desc in commands.items()
        ]
        
        output = '\n'.join(welcome_message + command_lines)
        
        return WelcomeOutput(
            message=output,
            commands=commands
        )

class ReceptionistAgent(Agent):
    """Frontend agent handling user interactions"""
    
    parent_crew: Any = Field(default=None)
    
    def __init__(self, llm, welcome_config=None, verbose=False):
        welcome_tool = CustomWelcomeTool(welcome_config)
        
        super().__init__(
            name="Receptionist",
            role="Client Interface Specialist",
            goal="Provide a seamless user experience by managing client interactions",
            backstory="A skilled front-end specialist with expertise in user interface design",
            tools=[welcome_tool],
            llm=llm,
            verbose=verbose
        )