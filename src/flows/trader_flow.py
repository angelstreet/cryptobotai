    # """from typing import List
    # from crewai import Flow, Task, Agent
    # from src.agents.receptionist import ReceptionistAgent

    # class TraderFlow(Flow):
    #     def __init__(self, data_analyst: DataAnalyst, trader: Trader, portfolio_manager: PortfolioManager):
    #         self.data_analyst = data_analyst
    #         self.trader = trader
    #         self.portfolio_manager = portfolio_manager
    #         super().__init__()

    #     def get_tasks(self) -> List[Task]:
    #         """Define the tasks for this flow."""
    #         return [
    #             Task(
    #                 description="Fetch market data",
    #                 expected_output="Market data fetched successfully",
    #                 agent=self.data_analyst,
    #                 output_key='market_data',
    #             ),
    #             Task(
    #                 description="Execute trade",
    #                 expected_output="Trade executed successfully",
    #                 agent=self.trader,
    #                 input_data={'market_data': 'market_data'},  # Use output from previous task
    #                 output_key='transaction',
    #             ),
    #             Task(
    #                 description="Update portfolio",
    #                 expected_output="Portfolio updated with new transaction",
    #                 agent=self.portfolio_manager,
    #                 input_data={'transaction': 'transaction'},  # Use output from previous task
    #             ),
    #         ]

    #     def kickoff(self) -> Dict[str, Any]:
    #         """Run the trade flow."""
    #         tasks = self.get_tasks()

    #         # Task 1: Fetch market data
    #         market_data_result = self.data_analyst.execute_task(tasks[0])
    #         print(market_data_result.get('message'))

    #         # Task 2: Execute trade
    #         trade_result = self.trader.execute_task(tasks[1], context=market_data_result)
    #         print(trade_result.get('message'))

    #         # Task 3: Update portfolio
    #         portfolio_result = self.portfolio_manager.execute_task(tasks[2], context=trade_result)
    #         print(portfolio_result.get('message'))

    #         return portfolio_result