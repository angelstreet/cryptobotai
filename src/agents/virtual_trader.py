from typing import Dict, Any
from .trader import TraderAgent
#from src.utils.display import print_mock_trading

class VirtualTraderAgent(TraderAgent):
    """Simulates trades in sandbox environment"""
    
    def execute_trade(self, trade_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute simulated trade"""
        try:
            if not self.validate_trade(trade_params):
                return self._get_default_decision("Invalid trade parameters")
                
            order = self.format_order(trade_params)
            
            # Simulate trade execution
            execution_result = self.simulate_execution(order)
            
            if self.debug:
                print_mock_trading()
                
            return execution_result
            
        except Exception as e:
            return self._get_default_decision(str(e))
            
    def simulate_execution(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate trade execution with artificial delay"""
        import time
        time.sleep(self._trade_delay)  # Simulate network delay
        
        return {
            'id': f"test-{order['symbol']}-{time.time()}",
            'status': 'FILLED',
            'filled': order['amount'],
            'price': order['params']['price'],  # Use price from order params
            'cost': order['amount'] * order['params']['price'],
            'fees': order['amount'] * order['params']['price'] * 0.001,
            'side': order['side']  # Add side for position tracking
        } 