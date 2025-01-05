import json
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

class AgentConfig:
    def __init__(self, config_name: str = "default"):
        load_dotenv()
        self.config_name = config_name
        self.config = self._load_config()
        # Override model from environment if set
        self.config["model"] = os.getenv("AI_MODEL", self.config["model"])
    
    def _load_config(self) -> Dict[str, Any]:
        """Load agent configuration from JSON file"""
        config_path = os.path.join(
            "agents",
            f"{self.config_name}.json"
        )
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config '{self.config_name}' not found, using default")
            with open(os.path.join("agents", "default.json"), 'r') as f:
                return json.load(f)
    
    @property
    def prompt_template(self) -> str:
        return self.config["prompt_template"]
    
    @property
    def model(self) -> str:
        return self.config["model"]
    
    @property
    def temperature(self) -> float:
        return self.config["temperature"]
    
    @property
    def max_tokens(self) -> int:
        return self.config["max_tokens"]
    
    @property
    def trading_params(self) -> Dict[str, Any]:
        return self.config["trading_params"]
    
    @property
    def position_sizing(self) -> Dict[str, Any]:
        return self.config["position_sizing"]
    
    @property
    def price_change_threshold(self) -> Dict[str, Any]:
        return self.config["price_change_threshold"]
    
    @property
    def stop_loss(self) -> Dict[str, Any]:
        return self.config["stop_loss"]
    
    @property
    def time_exit(self) -> Dict[str, Any]:
        return self.config["time_exit"]
    
    @property
    def take_profit_levels(self) -> List[Dict[str, float]]:
        return self.config["trading_params"]["take_profit"] 