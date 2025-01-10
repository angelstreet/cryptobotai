# flows/receptionist_flow.py
from typing import List, Dict, Any
from crewai import Flow, Agent
from src.agents.receptionist import ReceptionistAgent, WelcomeHandler, UserInputHandler, RouteCommandHandler, HelpHandler

class ReceptionistFlow(Flow):
    """Flow for handling welcome and user guidance"""
    
    def __init__(self, config, receptionist: ReceptionistAgent, portfolio_manager: Agent):
        self.config = config
        self.receptionist = receptionist
        self.portfolio_manager = portfolio_manager
        self.welcome_handler = WelcomeHandler()
        self.input_handler = UserInputHandler()
        self.route_command_handler = RouteCommandHandler(self.config)
        self.help_handler = HelpHandler()
        super().__init__()

    def get_agents(self) -> List[Agent]:
        """Define the agents used in this flow"""
        return [self.receptionist, self.portfolio_manager]

    def route_command(self, command: str) -> None:
        """Route the command to the appropriate task or flow"""
        if command == 'show_portfolio':
            self.portfolio_manager.show_portfolio()
        elif command == 'help':
            self.help_handler.run()

    def kickoff(self) -> Dict[str, Any]:
        """Run the receptionist flow with direct handler execution."""
 
        if self.config.command != 'welcome':
            command_result = self.route_command_handler.run()
            command = command_result.get('command')
            self.route_command(command)
        else:
            self.welcome_handler.run()
            self.help_handler.run()

        while True:  
            command_result = self.input_handler.run()
            command = command_result.get('command')
            self.route_command(command)
            if command == 'exit':
                break