from typing import Dict, Any
from openai import OpenAI
import re
from config import AgentConfig
import numpy as np
from datetime import datetime

class TradingAgent:
    def __init__(self, openai_client: OpenAI, config_name: str = "default"):
        self.client = openai_client
        self.config = AgentConfig(config_name)
        self.historical_data = []  # Store recent price data
        self.current_position = 0.0  # Track current position size
        self.entries = []  # List of dicts containing entry prices and amounts
    
    def _calculate_volatility(self, price_changes: list) -> float:
        """Calculate volatility using standard deviation of recent price changes"""
        if len(price_changes) < 2:
            return 1.0
        return np.std(price_changes) / np.mean(np.abs(price_changes))
    
    def update_position(self, action: str, amount: float, price: float):
        """Update current position after a trade"""
        if action == 'BUY':
            self.current_position += amount
            self.entries.append({
                'price': price,
                'amount': amount,
                'timestamp': datetime.now()
            })
        elif action == 'SELL':
            # Reduce position using FIFO (First In, First Out)
            remaining_sell = amount
            while remaining_sell > 0 and self.entries:
                oldest_entry = self.entries[0]
                if oldest_entry['amount'] <= remaining_sell:
                    # Complete exit of this entry
                    remaining_sell -= oldest_entry['amount']
                    self.entries.pop(0)
                else:
                    # Partial exit of this entry
                    oldest_entry['amount'] -= remaining_sell
                    remaining_sell = 0
            
            self.current_position = max(0.0, self.current_position - amount)
    
    def generate_trading_decision(self, market_data: Dict[str, float]) -> Dict[str, Any]:
        """Generate trading decision based on market data"""
        try:
            # Update historical data
            self.historical_data.append(market_data["change_24h"])
            if len(self.historical_data) > 24:  # Keep last 24 periods
                self.historical_data.pop(0)
            
            # Check price change threshold
            threshold_config = self.config.price_change_threshold
            base_threshold = threshold_config["base"]
            
            # Calculate volatility adjustment
            volatility_adjustment = self._calculate_volatility(self.historical_data)
            
            required_change = base_threshold * threshold_config["volatility_multiplier"] * volatility_adjustment
            required_change = max(threshold_config["min_threshold"], 
                                min(required_change, threshold_config["max_threshold"]))
            
            if abs(market_data["change_24h"]) < required_change:
                return self._get_default_decision(
                    f"Price change ({market_data['change_24h']:.3f}%) below dynamic threshold ({required_change:.3f}%)")
            
            # Format prompt with market data
            prompt = self.config.prompt_template.format(
                price=market_data["price"],
                volume=market_data["volume"],
                change_24h=market_data["change_24h"],
                high_low_range=market_data["high_low_range"],
                current_position=self.current_position,
                entry_price=self.entries[-1]['price'] if self.entries else "None"
            )
            
            # Get response from model
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a cryptocurrency trading assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            # Check if we got a valid response
            if not response or not response.choices or not response.choices[0].message:
                print("Warning: Received invalid response from API")
                return self._get_default_decision("API response invalid")
            
            # Parse response
            decision = self._parse_response(response.choices[0].message.content)
            
            # Apply trading parameters
            decision = self._apply_trading_params(decision, market_data)
            
            return decision
            
        except Exception as e:
            print(f"Error generating trading decision: {e}")
            return self._get_default_decision(str(e))
    
    def _get_default_decision(self, reason: str) -> Dict[str, Any]:
        """Return a safe default decision when errors occur"""
        return {
            "action": "HOLD",
            "amount": 0.0,
            "confidence": 0,
            "reasoning": f"Error occurred: {reason}"
        }
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the model's response into structured decision"""
        try:
            # Extract action (default to HOLD if not found)
            action_match = re.search(r"Action:?\s*(BUY|SELL|HOLD)", response, re.IGNORECASE)
            action = action_match.group(1).upper() if action_match else "HOLD"
            
            # Extract position size (default to 0)
            size_match = re.search(r"Position size:?\s*(0\.\d+|[01])", response)
            amount = float(size_match.group(1)) if size_match else 0.0
            
            # Extract confidence (default to 0)
            conf_match = re.search(r"Confidence:?\s*(\d+)", response)
            confidence = int(conf_match.group(1)) if conf_match else 0
            
            # Extract reasoning
            reason_match = re.search(r"reasoning:?\s*(.+)", response, re.IGNORECASE | re.DOTALL)
            reasoning = reason_match.group(1).strip() if reason_match else "No reasoning provided"
            
            return {
                "action": action,
                "amount": amount,
                "confidence": confidence,
                "reasoning": reasoning
            }
            
        except Exception as e:
            print(f"Error parsing response: {e}")
            print(f"Raw response: {response}")
            return self._get_default_decision("Failed to parse response")
    
    def _apply_trading_params(self, decision: Dict[str, Any], market_data: Dict[str, float]) -> Dict[str, Any]:
        """Apply trading parameters from config"""
        params = self.config.trading_params
        position_config = self.config.position_sizing
        
        # Force position size to 0 for HOLD
        if decision['action'] == 'HOLD':
            decision['amount'] = 0.0
        
        # Apply minimum confidence threshold
        if decision['confidence'] < params['min_confidence']:
            decision['action'] = 'HOLD'
            decision['amount'] = 0.0
            decision['reasoning'] = f"Confidence ({decision['confidence']}%) below minimum threshold ({params['min_confidence']}%)"
        
        # Apply maximum position size
        decision['amount'] = min(decision['amount'], position_config['max_position_size'])
        
        # Ensure minimum position size for active trades
        if decision['action'] != 'HOLD' and decision['amount'] < 0.1:
            decision['amount'] = 0.1
        
        return decision 