# receptionist.py
from typing import Dict, Any, List
from crewai import Agent
from rich.console import Console

console = Console()  # Create console instance for colored output

class HelpHandler:
    """Handler for available commands"""
    
    def run(self) -> Dict[str, Any]:
        """Return available commands"""        
        
        commands = {
            'show_portfolio': 'Portfolio overview',
            'help': 'Show help menu',
            'trade': 'Execute live trade',
            'virtual_trade': 'Execute virtual trade',
            'backtest': 'Run backtest simulation',
            'exit': 'Exit the program'
        }

        # Use rich formatting
        console.print("\n[bold cyan]Available commands:[/]")
        for cmd, desc in commands.items():
            console.print(f"[green]•[/] [yellow]{cmd:<14}[/] - {desc}")
            
        return {
            'commands': commands
        }

class WelcomeHandler:
    def run(self) -> Dict[str, Any]:
        console.print("\n[bold cyan]Hi, crypto lover! How can I help you?[/]")
        return {'message': 'welcome'}

class UserInputHandler:
    valid_commands: List[str] = ['show_portfolio', 'help', 'exit']

    def run(self) -> Dict[str, Any]:
        while True:
            try:
                console.print("\n[bold green]Enter a command:[/]")
                user_input = input("> ").strip().lower()
                
                if user_input in self.valid_commands:
                    return {'command': user_input, 'is_valid': True}
                
                console.print(f"[red]Invalid command![/] Available: {', '.join(self.valid_commands)}\n")
                continue
                
            except KeyboardInterrupt:
                return {'command': 'exit', 'is_valid': True}

class RouteCommandHandler:
    """Handler for command routing"""
    valid_commands: List[str] = ['show_portfolio']

    def __init__(self, config):
        self.config = config

    def run(self) -> Dict[str, Any]:
        """Return command to be executed"""        
        command = self.config.command
        console.print(f"\n[bold cyan]Executing command:[/] [yellow]{command}[/]")
        return {
            'command': command
        }

class ReceptionistAgent(Agent):
    """Frontend agent handling user interactions"""
    
    def __init__(self, config):
        super().__init__(
            name="Receptionist",
            role="Client Interface Specialist",
            goal="Welcome users and help them navigate the trading system",
            backstory="An expert in user interaction and crypto trading assistance",
            tools=[],  
            llm=config.llm,
            verbose=config.debug
        )