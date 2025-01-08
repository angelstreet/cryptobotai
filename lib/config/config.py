import json
import os
from typing import Dict, Any
from dotenv import load_dotenv
from lib.utils.display import console, SHARED_THEME

class Config:
    """Base configuration class that handles loading and validating trading configs"""
    
    def __init__(self, strategy: str = "default"):
        load_dotenv()
        self.strategy = strategy
        self.console = console
        self.debug_mode = False
        self.current_timestamp = None
        self.timeframe = '1h'
        self.risk_parameters = {
            'max_position_size': 0.1,
            'stop_loss': 0.02,
            'take_profit': 0.05
        }
        self.execution_parameters = {
            'slippage': 0.001,
            'timeout': 30,
            'retry_attempts': 3
        }
        
        # Load strategy config
        self.config = self._load_strategy_config()
        
        # Load AI settings
        self._load_ai_settings()
        
        # Validate all settings
        self._validate_config()
    
    def _load_strategy_config(self) -> Dict[str, Any]:
        """Load strategy configuration from JSON file"""
        config_path = os.path.join("lib", "config", f"{self.strategy}.json")
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.console.print(f"[warning]Strategy '{self.strategy}' not found, using default[/]")
            with open(os.path.join("lib", "config", "default.json"), 'r') as f:
                return json.load(f)
    
    def _load_ai_settings(self):
        """Load AI-specific settings from environment"""
        provider = os.getenv("AI_PROVIDER", "OPENAI").upper()
        
        self.config.update({
            "model": os.getenv(f"{provider}_MODEL", self.config.get("model")),
            "temperature": float(os.getenv(f"{provider}_TEMPERATURE", self.config.get("temperature", 0.7))),
            "max_tokens": int(os.getenv(f"{provider}_MAX_TOKENS", self.config.get("max_tokens", 200)))
        })
    
    def _validate_config(self):
        """Validate all configuration parameters"""
        required_sections = [
            "trading_params",
            "stop_loss",
            "price_change_threshold",
            "position_sizing"
        ]
        
        # Validate sections exist
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required section: {section}")
        
        self._validate_trading_params()
        self._validate_position_sizing()
        self._validate_price_threshold()
        self._validate_stop_loss()
        self._validate_ai_settings()
    
    def _validate_trading_params(self):
        params = self.config["trading_params"]
        if not 0 <= params["min_confidence"] <= 100:
            raise ValueError("min_confidence must be between 0 and 100")
        
        for tp in params["take_profit"]:
            if not all(k in tp for k in ["target", "size"]):
                raise ValueError("take_profit entries must have target and size")
    
    def _validate_position_sizing(self):
        pos = self.config["position_sizing"]
        if not 0 < pos["min_position_size"] <= pos["max_position_size"] <= 1:
            raise ValueError("Invalid position size range")
    
    def _validate_price_threshold(self):
        thresh = self.config["price_change_threshold"]
        if not 0 < thresh["min_threshold"] <= thresh["max_threshold"]:
            raise ValueError("Invalid threshold range")
    
    def _validate_stop_loss(self):
        sl = self.config["stop_loss"]
        if not 0 < sl["trailing"] <= sl["initial"]:
            raise ValueError("Invalid stop loss configuration")
    
    def _validate_ai_settings(self):
        required = ["model", "temperature", "max_tokens"]
        for field in required:
            if field not in self.config:
                raise ValueError(f"Missing AI setting: {field}")
    
    def __getattr__(self, name):
        """Allow direct access to config parameters"""
        if name in self.config:
            return self.config[name]
        raise AttributeError(f"No configuration parameter named '{name}'") 