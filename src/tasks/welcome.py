from typing import Dict
from .base import BaseTask

class WelcomeTask(BaseTask):
    """Task for welcoming users and showing available commands"""
    
    def execute(self, context: Dict) -> Dict:
            """Execute the welcome task"""
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