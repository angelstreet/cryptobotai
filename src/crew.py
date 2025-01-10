import os
from dotenv import load_dotenv
from crewai import Task, Crew, LLM
from src.tools import api as api_tool, display as display_tool
from src.agents.receptionist import welcome_task
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

    def live_trader(self):
        """Trader Agent"""
        return LiveTraderAgent(self.config)
    
    def backtest_trader(self):
        """Trader Agent"""
        return BacktestTraderAgent(self.config)
    
    def virtual_trader(self):
        """Trader Agent"""
        return VirtualTraderAgent(self.config)

    def receptionist(self):
        """Receptionist Agent"""
        return ReceptionistAgent(self.config)


    @classmethod
    def kickoff(cls, config):
        """Create and run the crew"""
        agency = cls(config)
        receptionnist=agency.receptionist()
        # Create crew
        crew = Crew(
            agents=[receptionnist
            ],
            tasks=[
                welcome_task(receptionnist)
            ],
        )
        
        return crew.kickoff()