# crew.py
import os
from typing import Optional, Dict, Any, List
from argparse import Namespace
from dotenv import load_dotenv
from crewai import Crew, Task, LLM
from src.agents.receptionist import ReceptionistAgent
from src.agents.portfolio_manager import PortfolioManagerAgent
from src.tasks.portfolio_manager_tasks import show_portfolio_task
from flows.receptionist_flow import ReceptionistFlow

class CryptoAgency(Crew):
    """AI Crypto Trading Agency using crewai"""
    
    def __init__(self, config: Namespace):
        self.config = config
        self.env = self._init_environment()
        self.llm = self._init_llm()
        
        # Initialize agents with LLM
        self.receptionist = ReceptionistAgent(
            config=self.config,
            llm=self.llm
        )
        self.portfolio_manager = PortfolioManagerAgent(
            config=self.config,
            llm=self.llm
        )
        
        # Initialize Crew with agents
        super().__init__(
            agents=[self.receptionist, self.portfolio_manager],
            tasks=[],  # Tasks will be added dynamically based on commands
            verbose=config.debug
        )

    def _init_environment(self) -> Dict[str, str]:
        """Initialize environment variables"""
        load_dotenv()
        return {
            'AI_API_PROVIDER': os.getenv('AI_API_PROVIDER', 'ollama'),
            'AI_API_URL': os.getenv('AI_API_URL', 'http://localhost:11434'),
            'AI_API_MODEL': os.getenv('AI_API_MODEL', 'mistral'),
            'AI_API_KEY': os.getenv('AI_API_KEY', '')
        }

    def _init_llm(self) -> LLM:
        """Initialize LLM based on environment"""
        provider = self.env['AI_API_PROVIDER'].lower()
        llm_params = {
            "model": self.env['AI_API_MODEL'],
            "base_url": self.env['AI_API_URL']
        }

        if provider in ("openai", "anthropic"):
            llm_params["api_key"] = self.env['AI_API_KEY']

        return LLM(**llm_params)
    
    def kickoff(self) -> None:
        """Initialize and run the trading system using Crew's process"""
        if self.config.command == "show_portfolio":
            # Use Crew's task processing for portfolio command
            self.tasks = [show_portfolio_task(self.portfolio_manager)]
            return super().kickoff()
        else:
            # Use receptionist flow for interactive commands
            flow = ReceptionistFlow(
                config=self.config,
                llm=self.llm
            )
            flow.kickoff()