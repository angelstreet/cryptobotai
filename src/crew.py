import os
from dotenv import load_dotenv
from crewai import Task, Crew, LLM
from src.tools import api as api_tool, display as display_tool
from src.agents import (
    DataAnalystAgent, PortfolioManagerAgent, 
    LiveTraderAgent, TestTraderAgent, BacktestTraderAgent, ReceptionistAgent
)

class CryptoAgency:
    """AI Crypto Trading Agency using crewai"""
    
    def __init__(self, config):
        self.env = self._init_environment()
        self.config = config
        self.config.llm = self._init_llm()  # Set LLM in config
        self.tools = self._init_tools()

    def _init_environment(self):
        load_dotenv()
        env_vars = {
            'AI_API_PROVIDER': os.getenv('AI_API_PROVIDER', 'ollama'),
            'AI_API_URL': os.getenv('AI_API_URL', 'http://localhost:11434'),
            'AI_API_MODEL': os.getenv('AI_API_MODEL', 'mistral'),
            'AI_API_KEY': os.getenv('AI_API_KEY', '')
        }
        return env_vars

    def _init_llm(self) -> LLM:
        """Initialize LLM based on config."""
        provider = self.env['AI_API_PROVIDER'].lower()
        # Initialize LLM with common parameters
        llm_params = {
            "model": self.env['AI_API_MODEL'],
            "base_url": self.env['AI_API_URL']
        }

        # Add API key if required
        if provider in ("openai", "anthropic"):
            llm_params["api_key"] = self.env['AI_API_KEY']

        return LLM(**llm_params)

    def _init_tools(self):
        return {
            'api': api_tool,
            'display': display_tool
        }

    def data_analyst(self):
        """Data Analyst Agent"""
        return DataAnalystAgent(self.config)

    def portfolio_manager(self):
        """Portfolio Manager Agent"""
        return PortfolioManagerAgent(self.config)

    def trader(self):
        """Trader Agent"""
        if self.config.trading_mode == 'live':
            return LiveTraderAgent(self.config)
        elif self.config.trading_mode == 'backtest':
            return BacktestTraderAgent(self.config)
        else:
            return TestTraderAgent(self.config)

    def receptionist(self):
        """Receptionist Agent"""
        return ReceptionistAgent(self.config)

    def analyze_market_task(self):
        """Task for analyzing market data"""
        return Task(
            description="Analyze market data",
            agent=self.data_analyst(),
            expected_output="Market analysis report"
        )

    def manage_portfolio_task(self):
        """Task for managing portfolio"""
        return Task(
            description="Manage portfolio",
            agent=self.portfolio_manager(),
            expected_output="Portfolio overview"
        )

    def execute_trade_task(self):
        """Task for executing trades"""
        return Task(
            description="Execute trade",
            agent=self.trader(),
            expected_output="Trade execution report"
        )

    def welcome_task(self):
        """Task for welcoming users"""
        return Task(
            description="Welcome user and show available commands",
            agent=self.receptionist(),
            expected_output="Welcome message : Hellow crypto lover! How can I help you?"
        )

    @classmethod
    def kickoff(cls, config):
        """Create and run the crew"""
        agency = cls(config)
        
        # Create crew
        crew = Crew(
            agents=[
                agency.receptionist()
            ],
            tasks=[
                agency.welcome_task()
            ],
        )
        
        return crew.kickoff()