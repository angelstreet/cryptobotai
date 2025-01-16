import os
from dotenv import load_dotenv
from crewai import LLM
from src.agents.receptionist import ReceptionistAgent
from src.agents.portfolio_manager import PortfolioManagerAgent
from src.agents.data_analyst import DataAnalystAgent
from flows.receptionist_flow import ReceptionistFlow
from src.config.models.portfolio import Action
from src.agents.data_analyst import BTC,ETH,TimeFrame
import src.agents.data_analyst  as dt
from src.utils.display import print_friendly_table
from src.tasks.portfolio_manager_tasks import AnalyzePortfolioTask
from crewai import Crew
import agentops

class CryptoAgency:
    """AI Crypto Trading Agency using crewai"""
    
    def __init__(self, config): 
        self.config = config
        self.config.debug = config.debug
        self.config.display_currency = config.display_currency
        
        llm = self._init_llm()
        self.config.llm = llm
    
    def _init_llm(self) -> LLM:
        """Initialize LLM after loading environment variables"""
        load_dotenv()
        agentops.init(api_key=os.getenv('AGENTOPS_API_KEY'))
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
    
    def start(self) -> None:
        """Start the crypto agency"""      
        # Initialize agents
        receptionist = ReceptionistAgent(config=self.config)
        portfolio_manager = PortfolioManagerAgent(config=self.config)
        data_analyst = DataAnalystAgent(config=self.config)
        # kickoff workflow
        receptionnist_flow(receptionist,portfolio_manager)
        #portfolio_manager.add_transaction("virtual","virtual-1","BTC/USDT",1,99000,Action.BUY)
        #portfolio_manager.add_transaction("virtual","virtual-1","ETH/USDT",1,3276.46,Action.BUY) 
        #portfolio_manager.add_transaction("virtual","virtual-1","BTC/USDT",0.1,80000,Action.SELL) 
        #portfolio_manager.delete_transaction("virtual","virtual-1","sell-20250112-202525")
        #print_friendly_table(dt.coingecko_get_price([BTC,ETH]), "CoinGecko Simple Price")
        #portfolio_manager.sync_coinbase()
        #portfolio_manager.show_portfolio()
        #analyze_portfolio_task(portfolio_manager)
        #portfolio_manager.show_orders()
        #data = dt.coingecko_get_historical_data(BTC,"USD",TimeFrame.DAY,)
        #dt.print_coingecko_historical_table(BTC,"USD",TimeFrame.DAY,data)
        #dt.print_coingecko_historical_chart(BTC,"USD",TimeFrame.DAY,data)
        #dt.plot_plotext_chart(BTC,"USD",data)

def receptionnist_flow(receptionist,portfolio_manager) -> None:
        """Kickoff receptionnist Flow"""
        flow = ReceptionistFlow(
            receptionist=receptionist,
            portfolio_manager =portfolio_manager
        )
        flow.kickoff()   

def analyze_portfolio_task(portfolio_manager) -> None:
        """Kickoff analyze portfolio task"""
        crew = Crew(
            agents=[portfolio_manager],
            tasks=[AnalyzePortfolioTask(portfolio_manager)]
        )
        result = crew.kickoff()
        print(result)