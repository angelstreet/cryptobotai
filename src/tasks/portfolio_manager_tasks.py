import json
from crewai import Task
from src.agents.portfolio_manager import PortfolioManagerAgent
import agentops

def AnalyzePortfolioTask(portfolio_manager: PortfolioManagerAgent) -> Task:
        portfolio_data = portfolio_manager.update_portfolio()
        description = f"""
        Analyze the following portfolio data and provide insights:
        {json.dumps(portfolio_data, indent=2)}
        """
        expected_output = f"""
        Consider the following:
        1. Overall portfolio performance.
        2. Diversification across assets.
        3. Profit/Loss for each asset.
        4. Suggestions for improvement (e.g., rebalancing, adding new assets).
        5. Any risks or opportunities you notice.

        Provide your analysis in a clear and concise manner.
        """
        description ="Say hello"
        expected_output ="be original and creative"
        agent = portfolio_manager
        tools = []
        return Task(description=description, expected_output=expected_output, agent=agent, tools=tools)