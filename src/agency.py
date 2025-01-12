import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from crewai import Crew, Task, LLM
from src.agents.receptionist import ReceptionistAgent
from src.agents.portfolio_manager import PortfolioManagerAgent
from flows.receptionist_flow import ReceptionistFlow
from src.config.models.portfolio import Action

class CryptoAgency:
    """AI Crypto Trading Agency using crewai"""
    
    def __init__(self, config): 
        self.config = config
        self.config.debug = config.debug
        llm = self._init_llm()
        self.config.llm = llm
    
    def _init_llm(self) -> LLM:
        """Initialize LLM after loading environment variables"""
        load_dotenv()
        AI_API_PROVIDER = os.getenv('AI_API_PROVIDER', 'ollama')
        AI_API_URL= os.getenv('AI_API_URL', 'http://localhost:11434')
        AI_API_MODEL= os.getenv('AI_API_MODEL', 'mistral')
        AI_API_KEY= os.getenv('AI_API_KEY', '')
        provider = AI_API_PROVIDER.lower()
        llm_params = {
            "model": AI_API_MODEL,
            "base_url": AI_API_URL
        }
        if provider in ("openai", "anthropic"):
            llm_params["api_key"] = 'AI_API_KEY'
        return LLM(**llm_params)
    
    def receptionnist_flow(self) -> None:
        """Kickoff the receptionnist"""
        flow = ReceptionistFlow(
            config=self.config,
            receptionist=self.receptionist,
            portfolio_manager =self.portfolio_manager
        )
        flow.kickoff()     
    
    def start(self) -> None:
        """Start the crypto agency"""      
        # Initialize agents
        self.receptionist = ReceptionistAgent(config=self.config)
        self.portfolio_manager = PortfolioManagerAgent(config=self.config)
        # kickoff workflow
        #self.receptionnist_flow()
        
        #self.portfolio_manager.add_transaction("virtual","virtual-1","ETH/USDT",1,3276.46,Action.BUY)
        #self.portfolio_manager.add_transaction("virtual","virtual-1","BTC/USDT",0.1,80000,Action.SELL) 
        #self.portfolio_manager.delete_transaction("virtual","virtual-1","sell-20250112-202525")
        self.portfolio_manager.show_portfolio()
        self.portfolio_manager.show_orders()
