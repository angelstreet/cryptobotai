from typing import Dict, Any, Optional
from crewai import Agent, Task
from pydantic import Field, ConfigDict

class ReceptionistAgent(Agent):
    """Frontend agent handling user interactions"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    parent_crew: Any = Field(default=None)
    
    def __init__(self, config, parent_crew=None):
        if not config.llm:
            raise ValueError("LLM not initialized in config")
            
        super().__init__(
            name="Receptionist",
            role="Client Interface Specialist",
            goal="Provide a seamless user experience by managing client interactions",
            backstory="A skilled front-end specialist with expertise in user interface design",
            llm=config.llm, 
            verbose=config.debug
        )
        self.parent_crew = parent_crew

def welcome_task(self) :
    """Execute welcome task with a formatted message and available commands."""
    return Task(
        description="Print welcome message",
        agent=self.receptionist(),
        expected_output="Welcome message"
    )
    # Format the welcome message
    welcome_message = [
        "\n=== AI Crypto Agency ===",
        "Welcome crypto lover! How can I help you?\n",
        "=== Available Commands ===",
    ]
    
    # Define available commands with descriptions
    commands = {
        'portfolio': 'Show portfolio overview',
        'trade': 'Execute live trade',
        'backtest': 'Run backtest simulation',
        'test': 'Run test trade in sandbox',
        'help': 'Show this help message'
    }
    
    # Format commands
    command_lines = [
        f"{cmd:<10} - {desc}" 
        for cmd, desc in commands.items()
    ]
    
    # Combine all parts and create final output
    output = '\n'.join(welcome_message + command_lines)
    
    # Return both the formatted string and commands dict
    return {
        'message': output,
        'commands': commands
    }