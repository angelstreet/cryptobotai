from typing import Dict, Any, Optional
from queue import Queue
from threading import Thread, Event
from .trader import TraderAgent
from pydantic import Field, ConfigDict

class BacktestTraderAgent(TraderAgent):
    """Simulates trades using historical data"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    result_queue: Queue = Field(default_factory=Queue)
    stop_event: Event = Field(default_factory=Event)
    running: bool = Field(default=False)
    
    def __init__(self, config):
        super().__init__(config)
        self.result_queue = Queue()
        self.stop_event = Event()
        self.running = False

    def execute_trade(self, trade_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute backtest trade simulation in separate thread"""
        try:
            if self.running:
                return {'error': 'Backtest already running'}

            if not self.validate_trade(trade_params):
                return self._get_default_decision("Invalid trade parameters")
                
            order = self.format_order(trade_params)
            
            # Create and start backtest thread
            self.stop_event.clear()
            self._current_thread = Thread(
                target=self._run_backtest,
                args=(order,),
                name="BacktestThread"
            )
            self._current_thread.daemon = True  # Thread will be terminated when main program exits
            self._current_thread.start()
            
            # Wait for result from thread
            result = self.result_queue.get()
            return result
            
        except Exception as e:
            if self.debug:
                print_backtest_error(f"Error starting backtest: {str(e)}")
            return self._get_default_decision(str(e))

    def _run_backtest(self, order: Dict[str, Any]):
        """Run backtest simulation in separate thread"""
        try:
            self.running = True
            
            if self.debug:
                print_backtest_progress("Starting backtest simulation...")
            
            # Check if we should stop
            if self.stop_event.is_set():
                raise InterruptedError("Backtest stopped by user")
            
            # Simulate trade with historical data
            result = self.simulate_historical_trade(order)
            
            if self.debug:
                print_backtest_progress("Backtest completed successfully")
            
            self.result_queue.put(result)
            
        except Exception as e:
            if self.debug:
                print_backtest_error(f"Backtest error: {str(e)}")
            self.result_queue.put(self._get_default_decision(str(e)))
        finally:
            self.running = False

    def simulate_historical_trade(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate trade using historical data"""
        if not self.historical_data:
            raise ValueError("No historical data available")
            
        # Periodically check if we should stop
        if self.stop_event.is_set():
            raise InterruptedError("Backtest stopped by user")
            
        # Find relevant historical prices
        entry_price = self._find_historical_price(order['params']['timestamp'])
        
        return {
            'id': f"backtest-{order['symbol']}-{order['params']['timestamp']}",
            'status': 'FILLED',
            'filled': order['amount'],
            'price': entry_price,
            'cost': order['amount'] * entry_price,
            'fees': order['amount'] * entry_price * 0.001,
            'timestamp': order['params']['timestamp']
        }
        
    def _find_historical_price(self, timestamp: int) -> float:
        """Find closest historical price to timestamp"""
        # Implementation depends on historical data format
        pass

    def stop_backtest(self):
        """Stop the current backtest gracefully"""
        if self.running:
            self.stop_event.set()
            if self._current_thread and self._current_thread.is_alive():
                self._current_thread.join(timeout=5)  # Wait up to 5 seconds
                if self._current_thread.is_alive():
                    if self.debug:
                        print_backtest_error("Backtest thread did not stop gracefully")
                    return False
        return True

    def is_running(self) -> bool:
        """Check if backtest is currently running"""
        return self.running

    def cleanup(self):
        """Cleanup resources before shutdown"""
        self.stop_backtest()
        while not self.result_queue.empty():
            _ = self.result_queue.get_nowait() 