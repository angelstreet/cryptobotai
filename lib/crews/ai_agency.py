from typing import Dict, List
from crewai import Agent as CrewAgent, Task as CrewTask, Crew
from lib.agents import DataAnalystAgent, PortfolioManagerAgent, TraderAgent, BacktesterAgent
from lib.tasks import (
    MarketAnalysis,
    StrategyDevelopment,
    BacktestExecution,
    TradeExecution,
    PerformanceEvaluation
)

class AIAgency:
    def __init__(self, config):
        self.config = config
        # Initialize base agents
        self.data_analyst = DataAnalystAgent(config)
        self.portfolio_manager = PortfolioManagerAgent(config)
        self.trader = TraderAgent(config)
        self.backtester = BacktesterAgent(config)
        
        # Initialize crew components
        self.tools = self._initialize_tools()
        self.crew_agents = self._initialize_crew_agents()
        self.tasks = self._create_tasks()
        self.crew = Crew(
            agents=list(self.crew_agents.values()),
            tasks=self.tasks,
            verbose=self.config.debug_mode
        )

    def _initialize_tools(self) -> Dict:
        """Initialize tools for crew agents"""
        return {
            'market_analysis': MarketAnalysis(self.data_analyst),
            'strategy_development': StrategyDevelopment(self.portfolio_manager),
            'backtest_execution': BacktestExecution(self.backtester),
            'trade_execution': TradeExecution(self.trader),
            'performance_evaluation': PerformanceEvaluation(self.portfolio_manager)
        }

    def _initialize_crew_agents(self) -> Dict[str, CrewAgent]:
        """Initialize crew agents with specific roles"""
        return {
            'data_analyst': CrewAgent(
                name="Data Analyst",
                role="Market Data & Analysis Specialist",
                goal="Provide comprehensive market analysis and data insights",
                backstory="""Expert in market data analysis, combining technical, fundamental, 
                            and sentiment analysis to provide actionable insights.""",
                tools=[
                    self.tools['fetch_historical_data'],
                    self.tools['fetch_live_data'],
                    self.tools['technical_analysis'],
                    self.tools['sentiment_analysis']
                ],
                verbose=self.config.debug_mode
            ),
            'portfolio_manager': CrewAgent(
                name="Portfolio Manager",
                role="Strategy & Portfolio Director",
                goal="Optimize portfolio performance through strategic management",
                backstory="""Senior portfolio manager specializing in strategy development,
                            risk management, and portfolio optimization.""",
                tools=[
                    self.tools['strategy_development'],
                    self.tools['portfolio_management'],
                    self.tools['risk_analysis'],
                    self.tools['performance_evaluation']
                ],
                verbose=self.config.debug_mode
            ),
            'backtester': CrewAgent(
                name="Strategy Backtester",
                role="Strategy Validation Specialist",
                goal="Validate trading strategies through historical testing",
                backstory="""Expert in strategy validation and historical data analysis,
                            providing performance metrics and optimization insights.""",
                tools=[
                    self.tools['backtest_strategy'],
                    self.tools['historical_analysis']
                ],
                verbose=self.config.debug_mode
            ),
            'trader': CrewAgent(
                name="Execution Trader",
                role="Trade Execution Specialist",
                goal="Execute trades efficiently while minimizing slippage",
                backstory="""Technical execution specialist focused on optimal trade execution
                            and real-time monitoring.""",
                tools=[
                    self.tools['execute_trade'],
                    self.tools['monitor_orders']
                ],
                verbose=self.config.debug_mode
            )
        }

    def _create_tasks(self) -> List[CrewTask]:
        """Create tasks following the specified workflow"""
        return [
            # Data Analysis Phase
            CrewTask(
                description="Fetch and analyze market data",
                agent=self.crew_agents['data_analyst'],
                context={
                    'mode': 'analysis',
                    'requirements': ['historical_data', 'live_data', 'technical_analysis', 'sentiment']
                }
            ),
            # Strategy Development Phase
            CrewTask(
                description="Develop and optimize trading strategy",
                agent=self.crew_agents['portfolio_manager'],
                context={
                    'mode': 'strategy',
                    'portfolio_status': self.portfolio_manager.get_position
                },
                depends_on=["Fetch and analyze market data"]
            ),
            # Backtesting Phase
            CrewTask(
                description="Validate strategy through backtesting",
                agent=self.crew_agents['backtester'],
                context={
                    'mode': 'backtest',
                    'parameters': self.config.risk_parameters
                },
                depends_on=["Develop and optimize trading strategy"]
            ),
            # Trade Execution Phase
            CrewTask(
                description="Execute trading decisions",
                agent=self.crew_agents['trader'],
                context={
                    'mode': 'execution',
                    'execution_parameters': self.config.execution_parameters
                },
                depends_on=["Validate strategy through backtesting"]
            ),
            # Post-Trade Analysis
            CrewTask(
                description="Evaluate trading performance",
                agent=self.crew_agents['portfolio_manager'],
                context={
                    'mode': 'evaluation',
                    'portfolio_status': self.portfolio_manager.get_position
                },
                depends_on=["Execute trading decisions"]
            )
        ]

    def set_debug(self, debug: bool):
        """Set debug mode for all components"""
        self.config.debug_mode = debug
        for agent in [self.data_analyst, self.portfolio_manager, self.trader, self.backtester]:
            agent.set_debug(debug)
        for crew_agent in self.crew_agents.values():
            crew_agent.verbose = debug

    def set_mock(self, mock: bool):
        """Set mock mode for all components"""
        for agent in [self.data_analyst, self.portfolio_manager, self.trader, self.backtester]:
            agent.mock = mock

    def execute_trading_cycle(self, exchange: str, symbol: str) -> Dict:
        """Execute a complete trading cycle"""
        context = {
            'exchange': exchange,
            'symbol': symbol,
            'timestamp': self.config.current_timestamp
        }
        
        try:
            result = self.crew.kickoff()
            return self._process_crew_result(result)
        except Exception as e:
            if self.config.debug_mode:
                print(f"Error in trading cycle: {str(e)}")
            return {'error': str(e)}

    def _process_crew_result(self, result: Dict) -> Dict:
        """Process and validate crew execution results"""
        try:
            return {
                'analysis': result.get('market_analysis', {}),
                'strategy': result.get('portfolio_strategy', {}),
                'backtest': result.get('backtest_results', {}),
                'execution': result.get('trade_execution', {}),
                'evaluation': result.get('performance_evaluation', {}),
                'timestamp': self.config.current_timestamp
            }
        except Exception as e:
            if self.config.debug_mode:
                print(f"Error processing crew result: {str(e)}")
            return {'error': str(e)} 