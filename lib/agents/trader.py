from typing import Dict, Any
from lib.utils.display import (
    print_trading_data, print_api_error, print_trading_params,
    print_trading_decision, print_ai_prompt, print_parse_error,
    print_trading_error, print_ai_response, print_mock_trading
)
from lib.utils.api import call_local_model
from lib.config.config import Config
from lib.agents.agent import Agent
from lib.utils.mock_data import get_mock_trade_suggestion

class TraderAgent(Agent):
    def __init__(self, config):
        super().__init__(config)
        self.debug = False

    def set_debug(self, debug: bool):
        """Enable or disable debug mode"""
        self.debug = debug

    def _get_default_decision(self, reason: str = "Unknown error") -> Dict[str, Any]:
        """Return default HOLD decision when error occurs"""
        return {
            'action': 'HOLD',
            'amount': 0.0,
            'confidence': 0.0,
            'reasoning': f"Error occurred: {reason}",
            'debug': self.debug
        }

    def generate_trading_decision(self, market_data: Dict, **kwargs) -> Dict:
        """Generate trading decision"""
        if self.mock:
            print_mock_trading()
            return get_mock_trade_suggestion()
            
        # Regular trading logic...

    def _format_prompt(self, market_data: Dict[str, float], current_position: float, entry_price: float) -> str:
        """Format prompt for AI model"""
        take_profit_targets = [
            f"{tp['size']*100:.0f}% at +{tp['target']:.1f}%" 
            for tp in self.config.trading_params['take_profit']
        ]
        take_profit_str = ", ".join(take_profit_targets)
        
        # Get trading parameters
        trading_params = self.config.trading_params.copy()
        price_threshold = self.config.price_change_threshold
        stop_loss = self.config.stop_loss
        position_sizing = self.config.position_sizing
        
        # Add position warning to prompt
        position_note = "\nNOTE: Cannot SELL when Current Position is 0. Only BUY or HOLD actions are valid.\n" if current_position <= 0 else ""
        
        return self.config.prompt_template.format(
            price=market_data["price"],
            volume=market_data["volume"],
            change_24h=market_data["change_24h"],
            high_low_range=market_data["high_low_range"],
            current_position=current_position,
            entry_price=entry_price,
            min_size=position_sizing['min_position_size'],
            max_size=position_sizing['max_position_size'],
            base_threshold=price_threshold['base'],
            required_change=price_threshold['base'],
            stop_loss=stop_loss['initial'],
            trailing_stop=stop_loss['trailing'],
            take_profit_str=take_profit_str,
            min_confidence=trading_params['min_confidence'],
            position_note=position_note
        )

    def _get_ai_response(self, prompt: str) -> str:
        """Get response from AI model"""
        try:
            response = call_local_model(prompt)
            #if self.debug:
            #    print_ai_response(response)
            return response
        except Exception as e:
            print_api_error(str(e))
            raise

    def _parse_response(self, response: str, current_position: float) -> Dict[str, Any]:
        """Parse AI response into trading decision"""
        try:
            # Extract action, amount, confidence from response
            lines = response.strip().split('\n')
            decision = {
                'debug': self.debug
            }
            
            reasoning_lines = []
            in_reasoning = False
            
            for line in lines:
                line = line.strip()
                if line.startswith('Action:'):
                    action = line.split(':')[1].strip()
                    # Prevent SELL when no position
                    if action == 'SELL' and current_position <= 0:
                        action = 'HOLD'
                        reasoning_lines.append("Cannot SELL: No current position")
                    decision['action'] = action
                elif line.startswith('Amount:'):
                    try:
                        decision['amount'] = float(line.split(':')[1].strip())
                    except:
                        decision['amount'] = 0.0
                elif line.startswith('Confidence:'):
                    try:
                        decision['confidence'] = float(line.split(':')[1].strip().rstrip('%'))
                    except:
                        decision['confidence'] = 0.0
                elif line.startswith('Reasoning:'):
                    in_reasoning = True
                    reasoning_lines.append(line.split(':', 1)[1].strip())
                elif in_reasoning and line:
                    reasoning_lines.append(line)
            
            # Join all reasoning lines
            decision['reasoning'] = ' '.join(reasoning_lines) if reasoning_lines else 'No reasoning provided'
            
            # Validate decision
            if 'action' not in decision:
                decision['action'] = 'HOLD'
            if 'amount' not in decision:
                decision['amount'] = 0.0
            if 'confidence' not in decision:
                decision['confidence'] = 0.0
            
            return decision
            
        except Exception as e:
            print_parse_error(str(e), response)
            return self._get_default_decision(f"Failed to parse response: {str(e)}") 