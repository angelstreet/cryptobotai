from typing import Dict
from .base import BaseTask

class WelcomeTask(BaseTask):
    """Task for welcoming users and showing available commands"""
    
    async def execute(self, context: Dict) -> Dict:
        """Execute the welcome task"""
        return {
            'message': 'Hi, crypto lover! How can I help you?',
            'commands': {
                'portfolio': 'Show portfolio overview',
                'trade': 'Execute live trade',
                'backtest': 'Run backtest simulation',
                'test': 'Run test trade in sandbox',
                'help': 'Show this help message'
            }
        } 