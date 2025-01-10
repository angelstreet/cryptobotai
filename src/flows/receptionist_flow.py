# flows/welcome_flow.py
from crewai import Flow, Task
from agents.receptionist import ReceptionistAgent

class ReceptionistFlow(Flow):
    """Flow for handling welcome and user guidance (No llm required)"""
    
    def __init__(self, config):
        self.receptionist = ReceptionistAgent(config=config)
        super().__init__()

    def kickoff(self) -> str:
        """Run the welcome flow synchronously"""
        welcome_task = Task(
            description="Show welcome message and available commands",
            expected_output="A welcome message with list of available commands",
            agent=self.receptionist,
            async_execution=False,
        )
        return self.receptionist.execute_task(welcome_task)