from typing import Dict, Any, Optional
from crewai import Agent
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
            llm=config.llm,  # Now config.llm is guaranteed to exist
            verbose=config.debug
        )
        self.parent_crew = parent_crew

    def execute_welcome(self, context: Dict) -> Dict[str, Any]:
        """Execute welcome task"""
        print("=== AI Crypto Agency ===")
        print("Welcome crypto lover!\n How can I help you?")
        
        commands = {
            'portfolio': 'Show portfolio overview',
            'trade': 'Execute live trade',
            'backtest': 'Run backtest simulation',
            'test': 'Run test trade in sandbox',
            'help': 'Show this help message'
        }
        
        print("=== Available Commands ===")
        for cmd, desc in commands.items():
            print(f"{cmd:10} - {desc}")
            
        return {'commands': commands}