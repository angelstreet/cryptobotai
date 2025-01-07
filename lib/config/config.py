import json
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from rich.console import Console
from rich.theme import Theme
from lib.utils.display import console, SHARED_THEME

class AgentConfig:
    def __init__(self, config_name: str = "default"):
        load_dotenv()
        self.config_name = config_name
        self.console = Console(theme=SHARED_THEME)
        self.color_style = {
            "aggressive": "aggressive",
            "conservative": "conservative",
            "default": "default"
        }.get(config_name, "default")
        self.default_config = {
            "price_change_threshold": {
                "base": 0.2,
                "min_threshold": 0.1,
                "max_threshold": 2.0,
                "volatility_multiplier": 1.5
            },
            "position_sizing": {
                "max_position_size": 0.5,
                "min_position_size": 0.1,
                "risk_per_trade": 0.05
            },
            "trading_params": {
                "min_confidence": 40,
                "take_profit": [
                    {"target": 2.0, "size": 0.5},
                    {"target": 5.0, "size": 1.0}
                ]
            }
        }
        self.config = self._load_config()
        
        # Get provider-specific settings
        provider = os.getenv("AI_PROVIDER", "OPENAI").upper()
        self.config["model"] = os.getenv(f"{provider}_MODEL")
        self.config["temperature"] = float(os.getenv(f"{provider}_TEMPERATURE", "0.7"))
        self.config["max_tokens"] = int(os.getenv(f"{provider}_MAX_TOKENS", "200"))
        
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load agent configuration from JSON file"""
        config_path = os.path.join("lib", "config", f"{self.config_name}.json")
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Override with environment variables if set
            if os.getenv("AI_TEMPERATURE"):
                config["temperature"] = float(os.getenv("AI_TEMPERATURE"))
            if os.getenv("AI_MAX_TOKENS"):
                config["max_tokens"] = int(os.getenv("AI_MAX_TOKENS"))
            
            return config
            
        except FileNotFoundError:
            print(f"Warning: Config '{self.config_name}' not found, using default")
            with open(os.path.join("lib", "config", "default.json"), 'r') as f:
                return json.load(f)
    
    def _validate_config(self):
        """Validate the configuration parameters"""
        required_sections = [
            "trading_params",
            "stop_loss",
            "price_change_threshold",
            "position_sizing"
        ]
        
        # Check required sections
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate trading parameters
        trading_params = self.config["trading_params"]
        if "min_confidence" not in trading_params:
            raise ValueError("Missing min_confidence in trading_params")
        if not isinstance(trading_params["min_confidence"], (int, float)):
            raise ValueError("min_confidence must be a number")
        if not 0 <= trading_params["min_confidence"] <= 100:
            raise ValueError("min_confidence must be between 0 and 100")
        
        # Validate position sizing
        position_sizing = self.config["position_sizing"]
        required_position_fields = ["max_position_size", "min_position_size"]
        for field in required_position_fields:
            if field not in position_sizing:
                raise ValueError(f"Missing {field} in position_sizing")
            if not isinstance(position_sizing[field], (int, float)):
                raise ValueError(f"{field} must be a number")
            if not 0 <= position_sizing[field] <= 1:
                raise ValueError(f"{field} must be between 0 and 1")
        
        # Validate price change threshold
        threshold = self.config["price_change_threshold"]
        required_threshold_fields = ["base", "volatility_multiplier", "min_threshold", "max_threshold"]
        for field in required_threshold_fields:
            if field not in threshold:
                raise ValueError(f"Missing {field} in price_change_threshold")
            if not isinstance(threshold[field], (int, float)):
                raise ValueError(f"{field} must be a number")
            if threshold[field] < 0:
                raise ValueError(f"{field} cannot be negative")
        
        # Validate stop loss
        stop_loss = self.config["stop_loss"]
        required_stop_fields = ["initial", "trailing"]
        for field in required_stop_fields:
            if field not in stop_loss:
                raise ValueError(f"Missing {field} in stop_loss")
            if not isinstance(stop_loss[field], (int, float)):
                raise ValueError(f"{field} must be a number")
            if stop_loss[field] < 0:
                raise ValueError(f"{field} cannot be negative")
        
        # Validate model settings
        required_model_fields = ["model", "temperature", "max_tokens"]
        for field in required_model_fields:
            if field not in self.config:
                raise ValueError(f"Missing {field} in configuration")
    
    def __getattr__(self, name):
        """Allow direct access to config parameters"""
        if name in self.config:
            return self.config[name]
        raise AttributeError(f"'AgentConfig' object has no attribute '{name}'") 