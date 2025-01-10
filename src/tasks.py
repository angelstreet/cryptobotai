from typing import List
from crewai import Task, Agent

def welcome_task(agent: Agent) -> Task:
    """Create a welcome task that doesn't require LLM processing"""
    return Task(
        description="Welcome the user and show available commands",
        expected_output="""A welcome message with the list of available commands, 
        including portfolio, trade, backtest, virtual, and help options.""",
        agent=agent,
        async_execution=False,
    )

def portfolio_overview_task(agent: Agent) -> Task:
    """Create portfolio overview task"""
    return Task(
        description="Show the current portfolio status and holdings",
        expected_output="A detailed overview of the portfolio including holdings and performance",
        agent=agent #PortfolioManagerAgent
    )