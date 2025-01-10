# flows/welcome_flow.py
from crewai import Flow, Task
from agents.receptionist import ReceptionistAgent  # Remove src.

class ReceptionistFlow(Flow):
    """Flow for handling welcome and user guidance"""
    
    def __init__(self, config):
        self.config = config
        self.receptionist = ReceptionistAgent(config=self.config)
        super().__init__()

    def start(self):
        """Define the starting task(s) for the flow"""
        welcome_task = Task(
            description="Show welcome message and available commands",
            agent=self.receptionist
        )
        return [welcome_task]
        
    async def run(self):
        """Run the welcome flow"""
        # Execute the welcome task
        tasks = self.start()
        results = []
        for task in tasks:
            result = await self.execute_task(task)
            results.append(result)
        return "\n".join(results)