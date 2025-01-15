from typing import Dict, Any
from queue import Queue
from threading import Event
from .trader import TraderAgent
import time
from pydantic import Field, ConfigDict

class LiveTraderAgent(TraderAgent):
    """Executes real trades on the exchange"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    exchange: Any = Field(default=None)
    trading_pairs: Queue = Field(default_factory=Queue)
    stop_event: Event = Field(default_factory=Event)
    running: bool = Field(default=False)
    
    def __init__(self, config, exchange_client=None):
        super().__init__(config)
        self.exchange = exchange_client
        self.stop_event = Event()
        self.running = False

    def start_trading(self):
        """Start the trading loop"""
        self.running = True
        self.stop_event.clear()
        
        while not self.stop_event.is_set():
            try:
                # Get trading pair from queue (if any)
                if not self.trading_pairs.empty():
                    symbol = self.trading_pairs.get()
                    
                    # 1. Get fresh market data
                    market_data = self.data_analyst.fetch_market_data(
                        self.exchange, symbol
                    )
                    
                    # 2. Make trading decision
                    decision = self.generate_trading_decision(market_data)
                    
                    # 3. Execute if needed
                    if decision['action'] != 'HOLD':
                        self.execute_trade(decision)
                        
                # Sleep between iterations
                time.sleep(self.config.trading_interval)
                    
            except Exception as e:
                if self.debug:
                    print_api_error(f"Trading error: {str(e)}")

    def stop_trading(self):
        """Stop the trading loop"""
        self.stop_event.set()
        self.running = False

    def add_trading_pair(self, symbol: str):
        """Add a pair to trade"""
        self.trading_pairs.put(symbol)

    def execute_trade(self, trade_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute live trade on exchange"""
        try:
            if not self.validate_trade(trade_params):
                return self._get_default_decision("Invalid trade parameters")
                
            order = self.format_order(trade_params)
            
            if self.mock:
                return self.mock_execute_trade(order)
                
            # Execute on real exchange
            response = self.exchange.create_order(**order)
            
            # Monitor execution
            execution_result = self.monitor_orders(response)
            
            if self.debug:
                print_trading_data(execution_result)
                
            return execution_result
            
        except Exception as e:
            print_api_error(str(e))
            return self._get_default_decision(str(e))
            
    def mock_execute_trade(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mock trade for testing"""
        return {
            'id': 'mock-order-id',
            'status': 'FILLED',
            'filled': order['amount'],
            'price': order['params']['price'],
            'cost': order['amount'] * order['params']['price']
        }

    @property
    def is_running(self) -> bool:
        """Check if trader is running"""
        return self.running 