from typing import List
from crewai import Task, Agent

def show_welcome_task(agent: Agent) -> Task:
    """Create a welcome task that doesn't require LLM processing"""
    return Task(
        description="Welcome the user and show available commands",
        expected_output="""A welcome message with the list of available commands, 
        including portfolio, trade, backtest, virtual, and help options.""",
        agent=agent,
        async_execution=False,
    )