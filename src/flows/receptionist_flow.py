# flows/receptionist_flow.py
from typing import List, Dict, Any
from crewai import Flow, Task, Agent
from src.agents.receptionist import ReceptionistAgent

class ReceptionistFlow(Flow):
    """Flow for handling welcome and user guidance (No llm required)"""
    
    def __init__(self, config, receptionist: ReceptionistAgent):
        self.config = config
        self.receptionist = receptionist
        super().__init__()

    def get_agents(self) -> List[Agent]:
        """Define the agents used in this flow"""
        return [self.receptionist]

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
        tasks = self.get_tasks()  # Define tasks outside the loop

        # Task 1: Show welcome message
        welcome_result = self.receptionist.execute_task(tasks[0])

        while True:  # Loop indefinitely
            # Task 2: Handle command input
            command_result = self.receptionist.execute_task(tasks[1])
            command = command_result.get('command')

            # Route the command to the appropriate agent or flow
            if command == 'portfolio':
                print("portfolio")
                # portfolio_result = self.portfolio_manager.execute_show_portfolio({'type':})
            elif command == 'exit':
                break

            # After the next flow is done, return to the receptionist
            print("Back to the receptionist...\n")