from openai import OpenAI
import re
from lib.config.config import Config
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any
import ccxt
import pandas as pd
from lib.utils.display import (
    print_debug_info, print_market_config, 
    print_trading_data, print_api_error, 
    print_trading_params, print_candle_analysis,
    print_trading_decision, format_debug_str,
    print_ai_prompt, print_size_adjustment
)
import os
import time
from lib.utils.api import call_local_model

class TradingAgent:
    def __init__(self, ai_client: OpenAI, config_name: str = "default"):
        self.client = ai_client
        self.config = Config(config_name)
        self.historical_data = []  # Store recent price data
        self.current_position = 0.0  # Track current position size
        self.entries = []  # List of dicts containing entry prices and amounts
        self.debug = False  # Debug mode flag
        self.show_reasoning = False  # Show reasoning flag
        self.symbol = None  # Add trading symbol
        
    def set_debug(self, debug: bool):
        """Enable or disable debug mode"""
        self.debug = debug
    
    def set_show_reasoning(self, show_reasoning: bool):
        """Enable or disable showing reasoning"""
        self.show_reasoning = show_reasoning
    
    def _calculate_volatility(self, price_changes: list) -> float:
        """Calculate volatility using standard deviation of recent price changes"""
        if len(price_changes) < 2:
            return 1.0
        return float(np.std(price_changes) / np.mean(np.abs(price_changes)))
    
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
    
    def _log_api_response(self, response, error=None):
        """Log API response or error for debugging"""
        if error:
            print_api_error(error)
        elif self.debug and response:
            console.print("\n[dim]─── AI Response ───[/]")
            console.print(response)
    
    def generate_trading_decision(self, market_data: Dict[str, float]) -> Dict[str, Any]:
        """Generate trading decision based on market data"""
        try:
            # Update historical data
            self.historical_data.append(market_data["change_24h"])
            if len(self.historical_data) > 24:
                self.historical_data.pop(0)
            
            # Check price change threshold
            threshold_config = self.config.price_change_threshold
            base_threshold = threshold_config["base"]
            
            # Calculate volatility adjustment
            volatility_adjustment = self._calculate_volatility(self.historical_data)
            required_change = base_threshold * threshold_config["volatility_multiplier"] * volatility_adjustment
            required_change = max(threshold_config["min_threshold"], 
                                min(required_change, threshold_config["max_threshold"]))
            
            # Initialize debug string after required_change is calculated
            if self.debug:
                debug_str = format_debug_str(
                    market_data=market_data,
                    position=self.current_position,
                    symbol=self.symbol,
                    required_change=required_change,
                    volatility_adjustment=volatility_adjustment
                )
            
            # Print trading data before decision
            if self.debug:
                print_trading_data(market_data, self.current_position, required_change, volatility_adjustment)
            
            if abs(market_data["change_24h"]) < required_change:
                threshold_message = (
                    f"Price change ({market_data['change_24h']:.3f}%) "
                    f"below dynamic threshold ({required_change:.3f}%)"
                )
                if self.debug:
                    self._log_api_response(threshold_message)
                
                decision = self._get_default_decision(threshold_message)
                if self.debug:
                    print_trading_params(self.config.trading_params)
                return decision
            
            # Format prompt with market data
            take_profit_targets = [f"{tp['size']*100:.0f}% at +{tp['target']:.1f}%" 
                                  for tp in self.config.trading_params['take_profit']]
            take_profit_str = ", ".join(take_profit_targets)
            
            prompt = self.config.prompt_template.format(
                price=market_data["price"],
                volume=market_data["volume"],
                change_24h=market_data["change_24h"],
                high_low_range=market_data["high_low_range"],
                current_position=self.current_position,
                entry_price=self.entries[-1]['price'] if self.entries else "None",
                min_size=self.config.position_sizing['min_position_size'],
                max_size=self.config.position_sizing['max_position_size'],
                base_threshold=self.config.price_change_threshold['base'],
                required_change=required_change,
                stop_loss=self.config.stop_loss['initial'],
                trailing_stop=self.config.stop_loss['trailing'],
                take_profit_str=take_profit_str,
                min_confidence=self.config.trading_params['min_confidence'],
                volatility_mult=self.config.price_change_threshold['volatility_multiplier']
            )
            
            # Show prompt in debug mode
            if self.debug:
                print_ai_prompt(prompt)
            
            provider = os.getenv("AI_PROVIDER", "OPENAI").upper()
            
            try:
                if provider == "LOCAL":
                    try:
                        content = call_local_model(
                            prompt=prompt,
                            model=self.config.model
                        )
                        
                    except Exception as local_error:
                        print_api_error(local_error)
                        return self._get_default_decision(str(local_error))
                        
                elif provider == "CLAUDE":
                    response = self.client.messages.create(
                        model=self.config.model,
                        system="You are a cryptocurrency trading assistant.",
                        messages=[{
                            "role": "user",
                            "content": prompt
                        }],
                        max_tokens=self.config.max_tokens
                    )
                    content = response.content[0].text
                else:
                    response = self.client.chat.completions.create(
                        model=self.config.model,
                        messages=[
                            {"role": "system", "content": "You are a cryptocurrency trading assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=self.config.temperature,
                        max_tokens=self.config.max_tokens,
                        timeout=30.0
                    )
                    content = response.choices[0].message.content
                
                
                # Parse response and include raw content
                decision = self._parse_response(content)
                decision['raw_response'] = content
                
            except Exception as api_error:
                error_msg = f"API error ({provider}): {str(api_error)}"
                if self.debug:
                    print_api_error(error_msg)
                return self._get_default_decision(error_msg)
                
            if self.show_reasoning:
                print_candle_analysis(
                    market_data=market_data,
                    config=self.config,
                    decision=decision,
                    position=self.current_position,
                    required_change=required_change,
                    volatility_adjustment=volatility_adjustment,
                    symbol=self.symbol
                )
            
            # Apply trading parameters
            decision = self._apply_trading_params(
                decision, 
                market_data,
                required_change,
                volatility_adjustment
            )
            
            # Always print the trading decision
            print_trading_decision(
                decision=decision,
                market_data=market_data,
                position=self.current_position,
                required_change=required_change,
                volatility_adjustment=volatility_adjustment,
                symbol=self.symbol
            )
            
            return decision
            
        except Exception as e:
            print(f"Error generating trading decision: {e}")
            return self._get_default_decision(str(e))
    
    def _get_default_decision(self, reason: str) -> Dict[str, Any]:
        """Return a safe default decision when errors occur or conditions are not met."""
        
        # Initialize default response
        decision = {
            "action": "HOLD",
            "amount": 0.0,
            "confidence": 0,
            "raw_response": reason,  # Store the original reason as raw response
            "reasoning": ""  # Will be set below
        }
        
        try:
            if "below dynamic threshold" in reason.lower():
                # Use regex to extract numbers, handling negative values
                price_match = re.search(r"change \(([-\d.]+)%\)", reason)
                threshold_match = re.search(r"threshold \(([-\d.]+)%\)", reason)
                
                if price_match and threshold_match:
                    price_change = float(price_match.group(1))
                    threshold = float(threshold_match.group(1))
                    
                    if abs(price_change) < 0.001:
                        decision["reasoning"] = (
                            f"Market is showing minimal movement (±{abs(price_change):.3f}%). "
                            f"Waiting for more significant price action above {threshold:.3f}% "
                            f"before considering trades."
                        )
                    else:
                        direction = "decrease" if price_change < 0 else "increase"
                        decision["reasoning"] = (
                            f"Current price {direction} of {abs(price_change):.3f}% is below "
                            f"the minimum threshold of {threshold:.3f}%. Holding position until "
                            f"market volatility increases."
                        )
            else:
                decision["reasoning"] = f"Holding position due to: {reason}"
            
        except Exception as e:
            decision["reasoning"] = f"System safety: Holding position. Error details: {str(e)}"
        
        return decision
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured decision"""
        try:
            # Clean up response
            cleaned_response = response.strip()
            
            # Store raw response
            raw_response = cleaned_response
            
            # Extract action
            action_match = re.search(r'action:\s*(\w+)', cleaned_response, re.IGNORECASE)
            action = action_match.group(1).upper() if action_match else "HOLD"
            
            # Extract confidence
            confidence_match = re.search(r'confidence:\s*(\d+)', cleaned_response, re.IGNORECASE)
            confidence = int(confidence_match.group(1)) if confidence_match else 0
            
            # Extract amount
            amount_match = re.search(r'amount:\s*([\d.]+)', cleaned_response, re.IGNORECASE)
            amount = float(amount_match.group(1)) if amount_match else 0.0
            
            # Extract reasoning - if no specific pattern matches, use the whole response
            reasoning = "No reasoning provided"
            reason_patterns = [
                r'reasoning:\s*(.+?)(?=\n\n|\Z)',
                r'reason:\s*(.+?)(?=\n\n|\Z)',
                r'analysis:\s*(.+?)(?=\n\n|\Z)'
            ]
            
            for pattern in reason_patterns:
                reason_match = re.search(pattern, cleaned_response, re.IGNORECASE | re.DOTALL)
                if reason_match:
                    reasoning = reason_match.group(1).strip()
                    break
            else:
                # If no specific reasoning pattern found, use the whole response
                # Remove common patterns that aren't part of the analysis
                cleaned_response = re.sub(r'action:.*?\n', '', cleaned_response, flags=re.IGNORECASE)
                cleaned_response = re.sub(r'confidence:.*?\n', '', cleaned_response, flags=re.IGNORECASE)
                cleaned_response = re.sub(r'amount:.*?\n', '', cleaned_response, flags=re.IGNORECASE)
                reasoning = cleaned_response.strip()
            
            # Clean up whitespace and empty lines
            reasoning = re.sub(r'\s+', ' ', reasoning).strip()
            
            return {
                "action": action,
                "amount": amount,
                "confidence": confidence,
                "reasoning": reasoning,
                "raw_response": raw_response  # Add raw response
            }
            
        except Exception as e:
            print(f"Error parsing response: {e}")
            print(f"Raw response: {response}")
            return self._get_default_decision("Failed to parse response")
    
    def _apply_trading_params(self, decision: Dict[str, Any], market_data: Dict[str, float], 
                            required_change: float, volatility_adjustment: float) -> Dict[str, Any]:
        """Apply trading parameters from config"""
        params = self.config.trading_params
        position_config = self.config.position_sizing
        
        # Store original values we want to preserve
        raw_response = decision.get('raw_response')
        original_reasoning = decision.get('reasoning')
        
        # Add min_confidence and debug flag to decision for display
        decision['min_confidence'] = params['min_confidence']
        decision['debug'] = self.debug
        
        # Debug trading parameters
        if self.debug:
            print_trading_params(params)
        
        # Force position size to 0 for HOLD
        if decision['action'] == 'HOLD':
            decision['amount'] = 0.0
        
        # Apply minimum confidence threshold
        if decision['confidence'] < params['min_confidence']:
            decision['action'] = 'HOLD'
            decision['amount'] = 0.0
            decision['raw_response'] = raw_response or original_reasoning
            decision['reasoning'] = f"Confidence ({decision['confidence']}%) below minimum threshold ({params['min_confidence']}%)"
            return decision
        
        # Position sizing - amount is treated as the desired position size in crypto units
        if decision['action'] != 'HOLD':
            # Apply maximum position size
            decision['amount'] = min(decision['amount'], position_config['max_position_size'])
            
            # Ensure minimum position size
            if decision['amount'] < position_config['min_position_size']:
                decision['amount'] = position_config['min_position_size']
                if self.debug:
                    print_size_adjustment(decision['amount'])
        
        # Prevent SELL when no position
        if decision['action'] == 'SELL' and self.current_position <= 0:
            decision['action'] = 'HOLD'
            decision['amount'] = 0.0
            decision['raw_response'] = raw_response or original_reasoning
            decision['reasoning'] = "Cannot SELL: No position to sell"
        
        return decision
    
    def _get_change_color(self, change: float) -> str:
        """Return the appropriate color for a price change"""
        if abs(change) < 0.0001:  # Effectively zero
            return "dim white"
        return "red" if change < 0 else "green" 
    
    async def fetch_market_data(
        self,
        exchange: str, 
        symbol: str, 
        timeframe: str = '1h',
        start_date: datetime = None,
        end_date: datetime = None
    ) -> pd.DataFrame:
        try:
            self.symbol = symbol  # Store the symbol
            exchange_instance = getattr(ccxt, exchange)()
            
            # Convert dates to timestamps if provided
            since = int(start_date.timestamp() * 1000) if start_date else None
            until = int(end_date.timestamp() * 1000) if end_date else None
            
            # Fetch OHLCV data
            ohlcv = []
            if since:
                while True:
                    data = exchange_instance.fetch_ohlcv(
                        symbol, 
                        timeframe, 
                        since=since,
                        limit=1000
                    )
                    ohlcv.extend(data)
                    
                    if not data or (until and data[-1][0] >= until):
                        break
                        
                    since = data[-1][0] + 1
                    
            else:
                ohlcv = exchange_instance.fetch_ohlcv(symbol, timeframe, limit=1000)
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Filter by date range if provided
            if start_date:
                df = df[df['timestamp'] >= start_date]
            if end_date:
                df = df[df['timestamp'] <= end_date]
                
            if self.debug:
                print_market_config(exchange, symbol, timeframe, len(df), start_date, end_date)
            
            return df
            
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return pd.DataFrame() 