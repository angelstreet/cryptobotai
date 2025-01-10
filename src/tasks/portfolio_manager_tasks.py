# src/tasks/portfolio_tasks.py
from crewai import Task
from typing import Any

def show_portfolio_task(agent: Any) -> Task:
    """Create a task to show portfolio overview"""
    return Task(
        description="Show current portfolio overview and balance",
        expected_output="A detailed overview of the current portfolio status",
        agent=agent,
        async_execution=False
    )