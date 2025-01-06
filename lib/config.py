import json
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from rich.console import Console
from rich.theme import Theme
from .display import SHARED_THEME

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
        # Override model from environment if set
        self.config["model"] = os.getenv("AI_MODEL", self.config["model"])
        self._validate_config()
    
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
    
    def _validate_config(self):
        """Validate and normalize configuration values"""
        try:
            # Ensure required sections exist
            for section in ["price_change_threshold", "position_sizing", "trading_params"]:
                if section not in self.config:
                    print(f"Warning: Missing {section} section, using defaults")
                    self.config[section] = self.default_config[section]
            
            # Print agent configuration in one line
            self.console.print(f"Agent Configuration: [{self.color_style}]{self.config_name}[/]")
            
            # Set minimum allowed values
            if self.config_name == "aggressive":
                MIN_BASE = 0.05
                MIN_THRESHOLD = 0.01
            else:
                MIN_BASE = 0.1
                MIN_THRESHOLD = 0.05
            
            thresh = self.config.get("price_change_threshold", {})
            base = thresh.get("base", MIN_BASE)
            min_thresh = thresh.get("min_threshold", MIN_THRESHOLD)
            max_thresh = thresh.get("max_threshold", base * 2)
            
            # Assign values without modification
            thresh["base"] = base
            thresh["min_threshold"] = min_thresh
            thresh["max_threshold"] = max_thresh
            thresh["volatility_multiplier"] = thresh.get("volatility_multiplier", 1.5)
            
            # Display base threshold with warning if too low
            base_str = f"Base: {thresh['base']:.3f}%"
            if thresh['base'] < MIN_BASE:
                base_str += f" [warning](Warning: Below recommended minimum {MIN_BASE}%)[/]"
            self.console.print(base_str)
            
            # Display min threshold with warning if too low
            min_str = f"Min: {thresh['min_threshold']:.3f}%"
            if thresh['min_threshold'] < MIN_THRESHOLD:
                min_str += f" [warning](Warning: Below recommended minimum {MIN_THRESHOLD}%)[/]"
            self.console.print(min_str)
            
            # Display max threshold
            self.console.print(f"Max: {thresh['max_threshold']:.3f}%")
            self.console.print(f"Volatility multiplier: {thresh['volatility_multiplier']:.1f}x")
            
            if not (thresh['min_threshold'] <= thresh['base'] <= thresh['max_threshold']):
                raise ValueError("Invalid threshold configuration: min <= base <= max not satisfied")
            
            # Position sizing
            pos = self.config.get("position_sizing", {})
            pos["max_position_size"] = max(0.1, min(1.0, pos.get("max_position_size", 0.5)))
            pos["min_position_size"] = max(0.01, min(pos["max_position_size"], pos.get("min_position_size", 0.1)))
            pos["risk_per_trade"] = max(0.01, min(0.1, pos.get("risk_per_trade", 0.05)))
            
        except Exception as e:
            print(f"\nError in configuration: {e}")
            print("Falling back to default configuration")
            self.config.update(self.default_config)
    
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