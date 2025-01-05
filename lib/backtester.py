from decimal import Decimal
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime
import asyncio
from .agent import TradingAgent
from .visualization import TradingVisualizer
from rich.console import Console
from rich.table import Table
from rich.theme import Theme
from .display import console, print_trading_analysis

# Use same theme as main.py
custom_theme = Theme({
    "buy": "bold green",
    "sell": "bold red",
    "hold": "dim white",
    "profit": "green",
    "loss": "red",
    "info": "bold blue",
    "header": "bold white"
})

console = Console(theme=custom_theme)

class Backtester:
    def __init__(self, initial_balance: Decimal = Decimal('10000')):
        self.initial_balance = initial_balance
        self.request_delay = 0.5  # Delay between API calls in seconds
        
    async def run(self, agent: TradingAgent, market_data: pd.DataFrame, show_reasoning: bool = False) -> Dict[str, Any]:
        """Run backtest simulation"""
        try:
            total_candles = len(market_data)
            print(f"\nStarting backtest simulation with {total_candles} candles...")
            print(f"Time range: {market_data['timestamp'].iloc[0]} to {market_data['timestamp'].iloc[-1]}\n")
            
            current_day = None
            progress_counter = 0
            
            for index, row in market_data.iterrows():
                # Track progress by day
                day = row['timestamp'].date()
                if day != current_day:
                    if current_day is not None:
                        print(f"Processing {day}...")
                    current_day = day
                
                # Show progress
                progress = (progress_counter / total_candles) * 100
                if progress_counter % 5 == 0 and progress > 0:  # Update every 5 candles, skip 0%
                    print(f"Progress: {progress:.1f}%", end="\r")
                progress_counter += 1
            
            trades = []
            balance = self.initial_balance
            position = Decimal('0')
            entry_price = None
            
            # Group candles by date for progress tracking
            current_date = None
            
            for i in range(len(market_data) - 1):
                # Show progress when date changes
                candle_date = market_data['timestamp'].iloc[i].date()
                if candle_date != current_date:
                    current_date = candle_date
                    print(f"Processing {current_date.strftime('%Y-%m-%d')}...")
                
                current_data = market_data.iloc[i]
                next_data = market_data.iloc[i + 1]
                
                # Prepare market data for agent
                agent_data = {
                    "candle_number": i + 1,
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
                
                if show_reasoning:
                    # Print progress separator
                    print("\n" + "=" * 80, style="dim")
                    print(f"Analyzing candle {i+1}/{total_candles} ({(i+1)/total_candles*100:.1f}%)", style="dim")
                    print("=" * 80 + "\n", style="dim")
                    
                    # Display trading analysis for all decisions
                    print_trading_analysis(
                        market_data.name,  # Symbol
                        agent_data,        # Market data
                        decision,          # Trading decision
                        agent,             # Trading agent
                        True              # Show reasoning
                    )
                elif i % max(1, total_candles // 10) == 0 and progress > 0:
                    print(f"Progress: {progress:.1f}%", end="\r")
                
                await asyncio.sleep(self.request_delay)  # Rate limiting
                
                # Execute trade
                if decision['action'] != 'HOLD':
                    print(f"\nPotential {decision['action']} signal detected:", style="info")
                    print(f"Price: ${float(next_data['open']):,.2f}")
                    print(f"Amount: {decision['amount']:.3f}")
                    print(f"Current Balance: ${float(balance):,.2f}")
                    
                    trade = {
                        'timestamp': current_data['timestamp'],
                        'action': decision['action'],
                        'price': Decimal(str(next_data['open'])),
                        'amount': Decimal(str(decision['amount'])),
                        'fee': Decimal('0.001'),
                        'balance': balance,
                        'position': position,
                        'cost': Decimal('0'),
                        'profit': Decimal('0'),
                        'reasoning': decision['reasoning']
                    }
                    
                    if decision['action'] == 'BUY':
                        cost = trade['price'] * trade['amount'] * (1 + trade['fee'])
                        if cost <= balance:
                            balance -= cost
                            position += trade['amount']
                            entry_price = trade['price']
                            trade['cost'] = cost
                            trades.append(trade)
                            print("Trade executed successfully", style="buy")
                        else:
                            print(f"Insufficient balance (needed: ${float(cost):,.2f})", style="loss")
                    
                    elif decision['action'] == 'SELL' and position > 0:
                        proceeds = trade['price'] * min(trade['amount'], position) * (1 - trade['fee'])
                        balance += proceeds
                        trade['cost'] = entry_price * trade['amount'] if entry_price else Decimal('0')
                        trade['profit'] = proceeds - trade['cost']
                        position = max(Decimal('0'), position - trade['amount'])
                        if position == 0:
                            entry_price = None
                        trades.append(trade)
                        print("Trade executed successfully", style="sell")
                    else:
                        print("Trade not executed (no position to sell)", style="loss")
            
            # Calculate final results
            final_position_value = position * Decimal(str(market_data['close'].iloc[-1]))
            final_balance = balance + final_position_value
            
            return {
                'trades': trades,
                'final_balance': final_balance,
                'final_position': position,
                'final_position_value': final_position_value
            }
        except Exception as e:
            print(f"Error during backtest: {e}")
            return {
                'trades': [],
                'final_balance': self.initial_balance,
                'final_position': Decimal('0'),
                'final_position_value': Decimal('0')
            }
    
    def print_results(self, results: Dict):
        """Print backtest results"""
        console.print("\n" + "=" * 50, style="header")
        console.print("BACKTEST RESULTS", style="header")
        console.print("=" * 50, style="header")
        
        # Performance metrics
        console.print("\nPerformance Metrics:", style="info")
        console.print("-" * 30)
        console.print(f"Initial Balance: ${self.initial_balance:,.2f}")
        console.print(f"Final Balance: ${results['final_balance']:,.2f}")
        
        total_return = ((results['final_balance'] - self.initial_balance) / self.initial_balance) * 100
        return_str = f"Total Return: {total_return:+.2f}%"
        console.print(return_str, style="profit" if total_return > 0 else "loss")
        
        # Trade statistics
        console.print("\nTrade Statistics:", style="info")
        console.print("-" * 30)
        console.print(f"Total Trades: {len(results['trades'])}")
        
        if results['trades']:
            wins = sum(1 for t in results['trades'] if t['profit'] > 0)
            losses = sum(1 for t in results['trades'] if t['profit'] < 0)
            win_rate = (wins / len(results['trades'])) * 100
            
            console.print(f"Winning Trades: {wins}", style="profit")
            console.print(f"Losing Trades: {losses}", style="loss")
            console.print(f"Win Rate: {win_rate:.1f}%")
            
            # Trade list
            console.print("\nTrade History:", style="info")
            console.print("-" * 30)
            for trade in results['trades']:
                date = trade['timestamp'].strftime('%Y-%m-%d %H:%M')
                profit_pct = (trade['profit'] / trade['cost']) * 100 if trade['cost'] > 0 else 0
                trade_str = f"{date} | {trade['action']} | Amount: {trade['amount']:.3f} @ ${trade['price']:,.2f} | "
                if profit_pct != 0:
                    trade_str += f"P/L: [{'profit' if profit_pct > 0 else 'loss'}]{profit_pct:+.2f}%[/]"
                else:
                    trade_str += "P/L: 0.00%"
                
                action_style = "buy" if trade['action'] == "BUY" else "sell"
                console.print(trade_str, style=action_style)
        
        console.print("\n" + "=" * 50, style="header") 