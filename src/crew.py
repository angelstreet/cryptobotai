# crew.py
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from crewai import Crew, Task
from langchain.chat_models import ChatOpenAI
from src.agents.receptionist import ReceptionistAgent

class CryptoAgency:
    """AI Crypto Trading Agency using crewai"""
    
    def __init__(self, config):
        self.config = config
        self.env = self._init_environment()
        self.config.llm = self._init_llm()
    
    def _init_environment(self) -> Dict[str, str]:
        """Initialize environment variables"""
        load_dotenv()
        return {
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'AI_MODEL': os.getenv('AI_MODEL', 'gpt-3.5-turbo'),
            'DEBUG': os.getenv('DEBUG', 'False').lower() == 'true'
        }
    
    def _init_llm(self) -> ChatOpenAI:
        """Initialize LLM"""
        return ChatOpenAI(
            model=self.env['AI_MODEL'],
            temperature=0.7,
            api_key=self.env['OPENAI_API_KEY']
        )
    
    @classmethod
    def kickoff(cls, config):
        """Create and run the crew"""
        agency = cls(config)
        receptionist = ReceptionistAgent(config=agency.config)
        
        welcome_task = Task(
            description="Welcome the user and show available commands",
            agent=receptionist
        )
        
        crew = Crew(
            agents=[receptionist],
            tasks=[welcome_task]
        )
        
        return crew.kickoff()