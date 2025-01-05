from decimal import Decimal
from typing import Dict, List
import pandas as pd
from agent import TradingAgent

class Backtester:
    def __init__(self, 
                 initial_balance: Decimal = Decimal('10000'),
                 trading_fee: Decimal = Decimal('0.001')):  # 0.1% fee
        self.initial_balance = initial_balance
        self.trading_fee = trading_fee
        self.trades = []
        
    async def run(self, agent: TradingAgent, market_data: pd.DataFrame) -> Dict:
        balance = self.initial_balance
        position = Decimal('0')
        
        for i in range(1, len(market_data)):
            current_price = market_data['close'].iloc[i]
            
            # Prepare market data for agent
            decision = agent.generate_trading_decision({
                "price": current_price,
                "volume": market_data['volume'].iloc[i],
                "change_24h": (current_price - market_data['close'].iloc[i-1]) / market_data['close'].iloc[i-1] * 100
            })
            
            # Execute trade based on agent's decision
            if decision['action'] == 'BUY' and balance > 0:
                amount = min(
                    decision['amount'],
                    balance / current_price
                )
                cost = amount * current_price
                fee = cost * self.trading_fee
                
                if cost + fee <= balance:
                    balance -= (cost + fee)
                    position += amount
                    self.trades.append({
                        'timestamp': market_data['timestamp'].iloc[i],
                        'action': 'BUY',
                        'price': current_price,
                        'amount': amount,
                        'fee': fee,
                        'balance': balance,
                        'position': position
                    })
                    
            elif decision['action'] == 'SELL' and position > 0:
                amount = min(decision['amount'], position)
                revenue = amount * current_price
                fee = revenue * self.trading_fee
                
                balance += (revenue - fee)
                position -= amount
                self.trades.append({
                    'timestamp': market_data['timestamp'].iloc[i],
                    'action': 'SELL',
                    'price': current_price,
                    'amount': amount,
                    'fee': fee,
                    'balance': balance,
                    'position': position
                })
        
        # Calculate final portfolio value
        final_value = balance + (position * market_data['close'].iloc[-1])
        
        return {
            'initial_balance': self.initial_balance,
            'final_balance': balance,
            'final_position': position,
            'final_value': final_value,
            'return_pct': ((final_value / self.initial_balance) - 1) * 100,
            'n_trades': len(self.trades),
            'trades': self.trades
        }

    def print_results(self, results: Dict):
        print("\nBacktesting Results:")
        print(f"Initial Balance: ${results['initial_balance']:.2f}")
        print(f"Final Balance: ${results['final_balance']:.2f}")
        print(f"Final Position: {results['final_position']:.6f}")
        print(f"Final Portfolio Value: ${results['final_value']:.2f}")
        print(f"Return: {results['return_pct']:.2f}%")
        print(f"Number of Trades: {results['n_trades']}") 