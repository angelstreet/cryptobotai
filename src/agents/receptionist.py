# receptionist.py
from typing import Dict, Any, List
from crewai import Agent
import readline
from rich.console import Console
console = Console()  # Create console instance for colored output
# Autocomplete function
def completer(text, state):
    options = [word for word in VALID_COMMANDS if word.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None

# Set the completer function
readline.set_completer(completer)
# Use tab for autocomplete
readline.parse_and_bind("tab: complete")

VALID_COMMANDS: Dict[str, str] = {
            'show_portfolio': 'Portfolio overview',
            'help': 'Show help menu',
            #'trade': 'Execute live trade',
            #'virtual_trade': 'Execute virtual trade',
            #'backtest': 'Run backtest simulation',
            'exit': 'Exit the program'
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
    def print_welcome(self) -> None:
        console.print("\n[bold cyan]Hi, crypto lover! How can I help you?[/]")

    def print_helper(self) -> None:
        console.print("\n[bold cyan]Available commands:[/]")
        for cmd, desc in VALID_COMMANDS.items():
            console.print(f"[green]•[/] [yellow]{cmd:<14}[/] - {desc}")

    def get_user_input(self) -> str:
        console.print("\n[bold green]Enter a command:[/]")
        user_input = input("> ").strip().lower()
        if user_input in VALID_COMMANDS:
            return user_input # Invalid User input
        else:
            console.print(f"[red]Invalid command ![/] ({', '.join(VALID_COMMANDS)})")
            return self.get_user_input()
    
    def kickoff(self) -> None:
        self.print_welcome()
        self.print_helper()