# crew.py
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from crewai import Crew, Task
from langchain.chat_models import ChatOpenAI
from src.agents.receptionist import ReceptionistAgent

class CryptoAgency:
    """AI Crypto Trading Agency using crewai"""
    
    def __init__(self, llm_config: Optional[Dict[str, Any]] = None, welcome_config: Optional[Dict[str, Any]] = None):
        self.env = self._init_environment()
        self.llm = self._init_llm(llm_config)
    
    def _init_environment(self) -> Dict[str, str]:
        """Initialize environment variables"""
        load_dotenv()
        return {
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'AI_MODEL': os.getenv('AI_MODEL', 'gpt-3.5-turbo'),
            'DEBUG': os.getenv('DEBUG', 'False').lower() == 'true'
        }
    
    def _init_llm(self, config: Optional[Dict[str, Any]] = None) -> ChatOpenAI:
        """Initialize LLM with provided config or defaults"""
        default_config = {
            'model': self.env['AI_MODEL'],
            'temperature': 0.7,
            'api_key': self.env['OPENAI_API_KEY']
        }
        
        final_config = {**default_config, **(config or {})}
        return ChatOpenAI(**final_config)
    
    def receptionist(self) -> ReceptionistAgent:
        """Create receptionist agent with custom welcome configuration"""
        return ReceptionistAgent(
            llm=self.llm,
            verbose=self.env['DEBUG']
        )
    
    def create_welcome_task(self) -> Task:
        """Create the welcome task"""
        return Task(
            description="Welcome the user and show available commands",
            agent=self.receptionist()
        )

    def kickoff(self):
        """Create and run the crew"""
        welcome_task = self.create_welcome_task()
        
        crew = Crew(
            agents=[welcome_task.agent],
            tasks=[welcome_task]
        )
        
        return crew.kickoff()