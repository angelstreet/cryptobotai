# flows/receptionist_flow.py
from typing import List, Dict, Any
from crewai import Flow, Task, Agent
from src.agents.receptionist import ReceptionistAgent
from src.tasks.portfolio_manager_tasks import show_portfolio_task

class ReceptionistFlow(Flow):
    """Flow for handling welcome and user guidance"""
    
    def __init__(self, config, receptionist: ReceptionistAgent, portfolio_manager: Agent):
        self.config = config
        self.receptionist = receptionist
        self.portfolio_manager = portfolio_manager
        super().__init__()

    def get_agents(self) -> List[Agent]:
        """Define the agents used in this flow"""
        return [self.receptionist, self.portfolio_manager]

    def get_tasks(self) -> List[Task]:
        """Define the tasks for this flow"""
        return [
            Task(
                description="Show welcome message",
                expected_output="A welcome message displayed to the user",
                agent=self.receptionist,
                async_execution=False,
            ),
            Task(
                description="Get user command input",
                expected_output="A valid command provided by the user",
                agent=self.receptionist,
                async_execution=False,
            )
        ]

    def kickoff(self) -> Dict[str, Any]:
        """Run the receptionist flow."""
        tasks = self.get_tasks()

        # Task 1: Show welcome message
        self.receptionist.execute_task(tasks[0])

        while True:  
            # Task 2: Handle command input
            command_result = self.receptionist.execute_task(tasks[1])
            command = command_result.get('command')

            # Route the command to task or flow
            if command == 'show_portfolio':
                self.portfolio_manager.show_portfolio()
            elif command == 'exit':
                break