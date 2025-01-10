# crew.py
import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from crewai import Crew, Task, LLM
from src.agents.receptionist import ReceptionistAgent
from src.agents.portfolio_manager import PortfolioManagerAgent
from flows.receptionist_flow import ReceptionistFlow

class CryptoAgency:
    """AI Crypto Trading Agency using crewai"""
    
    def __init__(self, config):
        self.config = config
        self.env = self._init_environment()
        self.config.llm = self._init_llm()
        
        # Initialize agents
        self.receptionist = ReceptionistAgent(config=self.config)
        self.portfolio_manager = PortfolioManagerAgent(config=self.config)
        
        # Initialize crew with all agents
        self.crew = Crew(
            agents=[self.receptionist, self.portfolio_manager],
            tasks=[],  # Tasks will be managed by flows
            verbose=self.config.debug
        )

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
        llm_params = {
            "model": self.env['AI_API_MODEL'],
            "base_url": self.env['AI_API_URL']
        }

        if provider in ("openai", "anthropic"):
            llm_params["api_key"] = self.env['AI_API_KEY']

        return LLM(**llm_params)
    
    
    def kickoff(self) -> None:
        """Orchestrate the crypto agency"""      
        # Receptionist flow
        flow = ReceptionistFlow(
            config=self.config,
            receptionist=self.receptionist
        )
        flow.kickoff()
        
