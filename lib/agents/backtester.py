from decimal import Decimal
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Any, List
from .agent import Agent
from lib.utils.display import console, print_backtest_results

class BacktesterAgent(Agent):
    def __init__(self, config, data_analyst=None, trader=None, portfolio_manager=None):
        super().__init__(config)
        self._data_analyst = data_analyst
        self._trader = trader
        self._portfolio_manager = portfolio_manager
        self._initial_balance = Decimal('10000')
        self._request_delay = 0.5

    @property
    def data_analyst(self):
        return self._data_analyst

    @data_analyst.setter
    def data_analyst(self, value):
        self._data_analyst = value

    @property
    def trader(self):
        return self._trader

    @trader.setter
    def trader(self, value):
        self._trader = value

    @property
    def portfolio_manager(self):
        return self._portfolio_manager

    @portfolio_manager.setter
    def portfolio_manager(self, value):
        self._portfolio_manager = value

    @property
    def initial_balance(self) -> Decimal:
        return self._initial_balance

    @property
    def request_delay(self) -> float:
        return self._request_delay

    async def run_simulation(self, market_data: pd.DataFrame, show_reasoning: bool = False) -> Dict[str, Any]:
        """Run backtest simulation using other agents"""
        try:
            total_candles = len(market_data)
            console.print(f"\nStarting backtest simulation with {total_candles} candles...")
            
            trades = []
            balance = self.initial_balance
            position = Decimal('0')
            entry_price = None
            
            for i in range(len(market_data) - 1):
                current_data = market_data.iloc[i]
                next_data = market_data.iloc[i + 1]
                
                # Prepare market data
                agent_data = self._prepare_market_data(market_data, i)
                
                # Get trading decision from trader agent
                decision = self.trader.generate_trading_decision(agent_data)
                
                # Execute trade if needed
                if decision['action'] != 'HOLD':
                    trade = self._execute_trade(
                        decision, next_data, balance, position, entry_price
                    )
                    if trade:
                        trades.append(trade)
                        balance = trade['balance']
                        position = trade['position']
                        entry_price = trade.get('entry_price', entry_price)
                
            return self._prepare_results(trades, balance, position, market_data)
            
        except Exception as e:
            console.print(f"Error during backtest: {e}", style="error")
            return self._empty_results()
        
    def analyze_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze backtest results"""
        # (Moving analysis logic here)
        
    async def run_backtest(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete backtest workflow"""
        market_data = await self.data_analyst.fetch_historical_data(
            params['exchange'],
            params['symbol'],
            params['timeframe'],
            params.get('start_date'),
            params.get('end_date')
        )
        
        results = await self.run_simulation(market_data, params.get('show_reasoning', False))
        analysis = self.analyze_results(results)
        
        if results['trades']:
            print_backtest_results(results)
            
        return {**results, **analysis} 

    def _prepare_market_data(self, market_data: pd.DataFrame, index: int) -> Dict[str, Any]:
        """Prepare market data for trading decision"""
        current_data = market_data.iloc[index]
        return {
            "candle_number": index + 1,
            "price": float(current_data['close']),
            "volume": float(current_data['volume']),
            "change_24h": float((current_data['close'] - market_data['close'].iloc[max(0, index-24)]) / 
                              market_data['close'].iloc[max(0, index-24)] * 100),
            "high_low_range": float((current_data['high'] - current_data['low']) / current_data['low'] * 100),
            "high_24h": float(market_data['high'].iloc[max(0, index-24):index+1].max()),
            "low_24h": float(market_data['low'].iloc[max(0, index-24):index+1].min())
        }

    def _execute_trade(self, decision: Dict, candle: pd.Series, 
                      balance: Decimal, position: Decimal, entry_price: float) -> Dict:
        """Execute a trade in the simulation"""
        trade = {
            'timestamp': candle.name,
            'action': decision['action'],
            'price': Decimal(str(candle['open'])),
            'amount': Decimal(str(decision['amount'])),
            'fee': Decimal('0.001'),
            'balance': balance,
            'position': position
        }
        
        if decision['action'] == 'BUY':
            cost = trade['price'] * trade['amount'] * (1 + trade['fee'])
            if cost <= balance:
                trade['balance'] = balance - cost
                trade['position'] = position + trade['amount']
                trade['entry_price'] = float(trade['price'])
                return trade
        
        elif decision['action'] == 'SELL' and position > 0:
            proceeds = trade['price'] * min(trade['amount'], position) * (1 - trade['fee'])
            trade['balance'] = balance + proceeds
            trade['position'] = max(Decimal('0'), position - trade['amount'])
            return trade
        
        return None

    def _prepare_results(self, trades: List[Dict], balance: Decimal, 
                        position: Decimal, market_data: pd.DataFrame) -> Dict[str, Any]:
        """Prepare final backtest results"""
        final_position_value = position * Decimal(str(market_data['close'].iloc[-1]))
        return {
            'trades': trades,
            'final_balance': balance,
            'final_position': position,
            'final_position_value': final_position_value,
            'total_value': balance + final_position_value
        }

    def _empty_results(self) -> Dict[str, Any]:
        """Return empty results structure"""
        return {
            'trades': [],
            'final_balance': self.initial_balance,
            'final_position': Decimal('0'),
            'final_position_value': Decimal('0'),
            'total_value': self.initial_balance
        } 