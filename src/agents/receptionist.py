# receptionist.py
from typing import Dict, Any, Optional, List
from crewai import Agent, Task
from crewai.tools import BaseTool

class WelcomeTool(BaseTool):
    """Tool to display welcome message and available commands"""
    name: str = "welcome"
    description: str = "Display welcome message and available commands"
    
    def _run(self) -> Dict[str, Any]:
        """
        Return welcome message and available commands
        
        Returns:
            Dict[str, Any]: Welcome message details
        """        
        commands = {
            'show_portfolio': 'Portfolio overview',
            'trade': 'Execute live trade',
            'virtual_trade': 'Execute virtual trade',
            'backtest': 'Run backtest simulation',
            'exit': 'Exit the program'
        }
        
        message = (
            "\nHi, crypto lover! How can I help you?\n\n"
            "Available commands:\n"
        )
        
        for cmd, desc in commands.items():
            message += f"• {cmd:<14} - {desc}\n"
            
        print(message)
        return {
            'message': message,
            'commands': commands
        }

# receptionist.py
from typing import Dict, Any, Optional, List
from crewai import Agent, Task
from crewai.tools import BaseTool

class UserInputTool(BaseTool):
    """Tool to capture and validate user input"""
    name: str = "user_input"
    description: str = "Capture and validate user command input"
    valid_commands: List[str] = [
        'show_portfolio', 'exit'
    ]  

    def _run(self) -> Dict[str, Any]:
        """Capture and validate user input"""
        while True:
            try:
                print("Enter a command:")
                user_input = input("> ").strip().lower()
                
                if user_input in self.valid_commands:
                    return {
                        'command': user_input,
                        'is_valid': True,
                        'message': f"Command '{user_input}' received"
                    }
                
                print(f"Invalid command. Available: {', '.join(self.valid_commands)}")
                continue
                
            except KeyboardInterrupt:
                return {
                    'command': 'exit',
                    'is_valid': True,
                    'message': 'Operation cancelled by user'
                }

class ReceptionistAgent(Agent):
    """Frontend agent handling user interactions"""
    
    def __init__(self, config):
        super().__init__(
            name="Receptionist",
            role="Client Interface Specialist",
            goal="Welcome users and help them navigate the trading system",
            backstory="An expert in user interaction and crypto trading assistance",
            tools=[WelcomeTool(), UserInputTool()],
            llm=config.llm,
            verbose=config.debug
        )

    def execute_task(self, task: Task, context: Optional[str] = None, tools: Optional[List[BaseTool]] = None) -> Dict[str, Any]:
        """
        Execute specific receptionist tasks
        
        Args:
            task (Task): The task to execute
            context (Optional[str]): Additional context for the task
            tools (Optional[List[BaseTool]]): List of available tools
        
        Returns:
            Dict[str, Any]: Task execution result
        """
        # Identify the appropriate tool based on task description
        if "welcome" in task.description.lower():
            welcome_tool = next((tool for tool in self.tools if tool.name == "welcome"), None)
            return welcome_tool._run() if welcome_tool else {"message": "Welcome tool not found"}
        
        if "input" in task.description.lower():
            input_tool = next((tool for tool in self.tools if tool.name == "user_input"), None)
            return input_tool._run() if input_tool else {"command": None, "is_valid": False, "message": "Input tool not found"}
        
        return {"command": None, "is_valid": False, "message": "Unknown task"}