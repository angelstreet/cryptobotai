from decimal import Decimal
from typing import Dict, List
import pandas as pd
from datetime import datetime
from agent import TradingAgent

class Backtester:
    def __init__(self, 
                 initial_balance: Decimal = Decimal('10000'),
                 trading_fee: Decimal = Decimal('0.001')):  # 0.1% fee
        self.initial_balance = initial_balance
        self.trading_fee = trading_fee
        self.trades = []
        self.daily_logs = []
        
    async def run(self, agent: TradingAgent, market_data: pd.DataFrame) -> Dict:
        balance = self.initial_balance
        position = Decimal('0')
        max_balance = self.initial_balance
        max_drawdown = Decimal('0')
        
        print("\nStarting backtest simulation...")
        print(f"Initial balance: ${float(self.initial_balance):.2f}")
        print("=" * 50)
        
        for i in range(1, len(market_data)):
            current_price = Decimal(str(market_data['close'].iloc[i]))
            timestamp = market_data['timestamp'].iloc[i]
            
            # Prepare market data for agent
            decision = agent.generate_trading_decision({
                "price": float(current_price),
                "volume": float(market_data['volume'].iloc[i]),
                "change_24h": float((current_price - Decimal(str(market_data['close'].iloc[i-1]))) / 
                                  Decimal(str(market_data['close'].iloc[i-1])) * 100)
            })
            
            # Calculate current portfolio value
            portfolio_value = balance + (position * current_price)
            
            # Track maximum balance and drawdown
            max_balance = max(max_balance, portfolio_value)
            current_drawdown = (max_balance - portfolio_value) / max_balance * 100
            max_drawdown = max(max_drawdown, current_drawdown)
            
            # Log daily state
            daily_log = {
                'timestamp': timestamp,
                'price': float(current_price),
                'portfolio_value': float(portfolio_value),
                'balance': float(balance),
                'position': float(position),
                'action': decision['action'],
                'confidence': decision['confidence'],
                'reasoning': decision['reasoning']
            }
            self.daily_logs.append(daily_log)
            
            # Print daily update
            print(f"\nDate: {timestamp.strftime('%Y-%m-%d %H:%M')}")
            print(f"Price: ${float(current_price):.2f}")
            print(f"Portfolio Value: ${float(portfolio_value):.2f}")
            print(f"Decision: {decision['action']} (Confidence: {decision['confidence']}%)")
            
            # Execute trade based on agent's decision
            if decision['action'] == 'BUY' and balance > 0:
                amount = min(
                    Decimal(str(decision['amount'])),
                    balance / current_price
                )
                cost = amount * current_price
                fee = cost * self.trading_fee
                
                if cost + fee <= balance:
                    balance -= (cost + fee)
                    position += amount
                    self.trades.append({
                        'timestamp': timestamp,
                        'action': 'BUY',
                        'price': float(current_price),
                        'amount': float(amount),
                        'fee': float(fee),
                        'balance': float(balance),
                        'position': float(position),
                        'reasoning': decision['reasoning']
                    })
                    print(f"Executed: BUY {float(amount):.6f} @ ${float(current_price):.2f}")
                    
            elif decision['action'] == 'SELL' and position > 0:
                amount = min(Decimal(str(decision['amount'])), position)
                revenue = amount * current_price
                fee = revenue * self.trading_fee
                
                balance += (revenue - fee)
                position -= amount
                self.trades.append({
                    'timestamp': timestamp,
                    'action': 'SELL',
                    'price': float(current_price),
                    'amount': float(amount),
                    'fee': float(fee),
                    'balance': float(balance),
                    'position': float(position),
                    'reasoning': decision['reasoning']
                })
                print(f"Executed: SELL {float(amount):.6f} @ ${float(current_price):.2f}")
            
            print("-" * 50)
        
        # Calculate final portfolio value and metrics
        final_price = Decimal(str(market_data['close'].iloc[-1]))
        final_value = balance + (position * final_price)
        
        return {
            'initial_balance': float(self.initial_balance),
            'final_balance': float(balance),
            'final_position': float(position),
            'final_value': float(final_value),
            'return_pct': float(((final_value / self.initial_balance) - 1) * 100),
            'max_drawdown': float(max_drawdown),
            'n_trades': len(self.trades),
            'trades': self.trades,
            'daily_logs': self.daily_logs
        }

    def print_results(self, results: Dict):
        print("\n" + "=" * 50)
        print("BACKTEST RESULTS SUMMARY")
        print("=" * 50)
        print(f"Initial Balance: ${results['initial_balance']:.2f}")
        print(f"Final Balance: ${results['final_balance']:.2f}")
        print(f"Final Position: {results['final_position']:.6f}")
        print(f"Final Portfolio Value: ${results['final_value']:.2f}")
        print(f"Total Return: {results['return_pct']:.2f}%")
        print(f"Maximum Drawdown: {results['max_drawdown']:.2f}%")
        print(f"Number of Trades: {results['n_trades']}")
        
        if results['n_trades'] > 0:
            print("\nTrade History:")
            for trade in results['trades']:
                print(f"\nDate: {trade['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                print(f"Action: {trade['action']}")
                print(f"Price: ${trade['price']:.2f}")
                print(f"Amount: {trade['amount']:.6f}")
                print(f"Fee: ${trade['fee']:.2f}")
                print(f"Reasoning: {trade['reasoning']}")
                print("-" * 30) 