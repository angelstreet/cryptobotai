from decimal import Decimal
from typing import Dict, List
import pandas as pd
from datetime import datetime
from .agent import TradingAgent
from .visualization import TradingVisualizer

class Backtester:
    def __init__(self, initial_balance: Decimal = Decimal('10000')):
        self.initial_balance = initial_balance
        
    async def run(self, agent: TradingAgent, market_data: pd.DataFrame) -> List[Dict]:
        """Run backtest simulation"""
        trades = []
        balance = self.initial_balance
        position = Decimal('0')
        entry_price = None
        
        for i in range(len(market_data) - 1):
            current_data = market_data.iloc[i]
            next_data = market_data.iloc[i + 1]
            
            # Prepare market data for agent
            agent_data = {
                "price": float(current_data['close']),
                "volume": float(current_data['volume']),
                "change_24h": float((current_data['close'] - market_data['close'].iloc[max(0, i-24)]) / 
                                  market_data['close'].iloc[max(0, i-24)] * 100),
                "high_low_range": float((current_data['high'] - current_data['low']) / current_data['low'] * 100),
                "high_24h": float(market_data['high'].iloc[max(0, i-24):i+1].max()),
                "low_24h": float(market_data['low'].iloc[max(0, i-24):i+1].min()),
                "historical_changes": [
                    float((market_data['close'].iloc[j] - market_data['close'].iloc[j-1]) / 
                          market_data['close'].iloc[j-1] * 100)
                    for j in range(max(0, i-24), i+1)
                ]
            }
            
            # Get trading decision
            decision = agent.generate_trading_decision(agent_data)
            
            # Execute trade
            if decision['action'] != 'HOLD':
                trade = {
                    'timestamp': current_data['timestamp'],
                    'action': decision['action'],
                    'price': Decimal(str(next_data['open'])),  # Use next candle's open price
                    'amount': Decimal(str(decision['amount'])),
                    'fee': Decimal('0.001'),  # 0.1% fee
                    'balance': balance,
                    'position': position,
                    'reasoning': decision['reasoning']
                }
                
                if decision['action'] == 'BUY':
                    cost = trade['price'] * trade['amount'] * (1 + trade['fee'])
                    if cost <= balance:
                        balance -= cost
                        position += trade['amount']
                        entry_price = trade['price']
                        trades.append(trade)
                
                elif decision['action'] == 'SELL' and position > 0:
                    proceeds = trade['price'] * min(trade['amount'], position) * (1 - trade['fee'])
                    balance += proceeds
                    position = max(Decimal('0'), position - trade['amount'])
                    if position == 0:
                        entry_price = None
                    trades.append(trade)
        
        return trades
    
    def print_results(self, trades: List[Dict], show_advanced: bool = False):
        """Print backtest results"""
        if not trades:
            print("No trades executed")
            return
        
        # Calculate metrics
        initial_balance = trades[0]['balance']
        final_balance = trades[-1]['balance'] + trades[-1]['position'] * trades[-1]['price']
        total_profit = final_balance - initial_balance
        profit_percentage = (total_profit / initial_balance) * 100
        
        print("\nBacktest Results:")
        print(f"Initial Balance: ${float(initial_balance):.2f}")
        print(f"Final Balance: ${float(final_balance):.2f}")
        print(f"Total Profit: ${float(total_profit):.2f} ({float(profit_percentage):.2f}%)")
        print(f"Number of Trades: {len(trades)}")
        
        if show_advanced:
            print("\nDetailed Trade History:")
            for trade in trades:
                print(f"\nTime: {trade['timestamp']}")
                print(f"Action: {trade['action']}")
                print(f"Price: ${float(trade['price']):.2f}")
                print(f"Amount: {float(trade['amount']):.4f}")
                print(f"Balance: ${float(trade['balance']):.2f}")
                if trade.get('reasoning'):
                    print(f"Reasoning: {trade['reasoning']}") 