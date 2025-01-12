# flows/receptionist_flow.py
from typing import List, Dict, Any
from crewai import Flow, Agent
from src.agents.receptionist import ReceptionistAgent

class ReceptionistFlow(Flow):
    """Flow for handling welcome and user guidance"""
    
    def __init__(self, config, receptionist: ReceptionistAgent, portfolio_manager: Agent):
        self.config = config
        self.receptionist = receptionist
        self.portfolio_manager = portfolio_manager
        super().__init__()

    def route_command(self, cmd: str) -> None:
        """Route the command to the appropriate task or flow"""
        if cmd == 'show_portfolio':
            self.portfolio_manager.show_portfolio()
        elif cmd == 'help':
            self.receptionist.print_helper()


    def kickoff(self) -> Dict[str, Any]:
        """Run the receptionist flow with direct handler execution."""
        self.receptionist.print_welcome()
        self.receptionist.print_helper()  
        while True:  
            user_input = self.receptionist.get_user_input()
            if user_input == 'exit':
                break
            self.route_command(user_input)
            
            