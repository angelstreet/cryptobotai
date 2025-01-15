from abc import abstractmethod
from typing import Dict, Any, List
from crewai import Agent
from pydantic import Field, ConfigDict

class TraderAgent(Agent):
    """Base trader agent with shared functionality"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    historical_data: List = Field(default_factory=list)
    current_position: float = Field(default=0.0)
    entry_price: float = Field(default=0.0)
    
    def __init__(self, config):
        super().__init__(config)
        self._historical_data = []
        self._current_position = 0.0
        self._entry_price = 0.0

    def validate_trade(self, trade_params: Dict[str, Any]) -> bool:
        """Validate trade parameters"""
        try:
            required_fields = ['symbol', 'action', 'amount']
            if not all(field in trade_params for field in required_fields):
                raise ValueError(f"Missing required fields: {required_fields}")
                
            if trade_params['action'] not in ['BUY', 'SELL', 'HOLD']:
                raise ValueError(f"Invalid action: {trade_params['action']}")
                
            if trade_params['amount'] < 0:
                raise ValueError(f"Invalid amount: {trade_params['amount']}")
                
            if trade_params['action'] == 'SELL' and trade_params['amount'] > self._current_position:
                raise ValueError(f"Insufficient position for sell: {trade_params['amount']} > {self._current_position}")
                
            return True
        except Exception as e:
            if self.debug:
                print_trading_error(str(e))
            return False

    def format_order(self, trade_params: Dict[str, Any]) -> Dict[str, Any]:
        """Format trade parameters into order"""
        return {
            'symbol': trade_params['symbol'],
            'type': 'MARKET',
            'side': trade_params['action'],
            'amount': trade_params['amount'],
            'params': {
                'timeInForce': 'GTC',
                'timestamp': trade_params.get('timestamp'),
                'price': trade_params.get('price', 0)
            }
        }

    @abstractmethod
    def execute_trade(self, trade_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trade (to be implemented by child classes)"""
        pass

    def monitor_orders(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor order execution"""
        if self.debug:
            print_trading_data(order)
        return order

    def _get_default_decision(self, reason: str = "Unknown error") -> Dict[str, Any]:
        """Return default HOLD decision when error occurs"""
        return {
            'action': 'HOLD',
            'amount': 0.0,
            'confidence': 0.0,
            'reasoning': f"Error occurred: {reason}",
            'debug': self.debug
        }

    def update_position(self, trade_result: Dict[str, Any]) -> None:
        """Update current position after trade"""
        if trade_result['status'] == 'FILLED':
            if trade_result['side'] == 'BUY':
                self._current_position += trade_result['filled']
                self._entry_price = trade_result['price']
            elif trade_result['side'] == 'SELL':
                self._current_position = max(0.0, self._current_position - trade_result['filled'])
                if self._current_position == 0.0:
                    self._entry_price = 0.0
