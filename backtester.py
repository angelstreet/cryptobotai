from decimal import Decimal
from typing import Dict, List
import pandas as pd
from datetime import datetime
from agent import TradingAgent
from visualization import TradingVisualizer
from config import AgentConfig

class Backtester:
    def __init__(self, initial_balance: Decimal = Decimal('10000')):
        self.initial_balance = initial_balance
        self.trades = []
        self.daily_logs = []
        self.market_data = None
        self.highest_price = None  # For trailing stop-loss
        self.entry_time = None     # For time-based exits
        
    def _check_exits(self, current_price: Decimal, current_time: datetime, 
                     position: Decimal, entry_price: Decimal, config: AgentConfig) -> bool:
        """Check if any exit conditions are met"""
        if position == 0:
            return False
            
        # Check stop loss
        stop_loss = config.stop_loss
        if self.highest_price:
            # Trailing stop-loss if activated
            if float(current_price) >= float(entry_price) * (1 + stop_loss["activation_threshold"]/100):
                stop_price = self.highest_price * (1 - stop_loss["trailing"]/100)
            else:
                stop_price = entry_price * (1 - stop_loss["initial"]/100)
            
            if current_price <= stop_price:
                return True
                
        # Check time-based exit
        time_exit = config.time_exit
        if time_exit["max_holding_period"] is not None:
            holding_period = current_time - self.entry_time
            max_period = pd.Timedelta(time_exit["max_holding_period"])
            if holding_period >= max_period:
                return True
                
        return False
        
    def _calculate_position_size(self, decision: Dict, current_price: Decimal, 
                                balance: Decimal, config: AgentConfig) -> Decimal:
        """Calculate position size based on configuration"""
        position_config = config.position_sizing
        units = position_config["units"]
        
        # Get base position size
        if units["position_size"] == "percent":
            base_size = Decimal(str(position_config["max_position_size"])) * balance
        else:  # "usd"
            base_size = Decimal(str(position_config["max_position_size"]))
            
        # Apply Kelly Criterion adjustment
        kelly_size = base_size * Decimal(str(position_config["kelly_factor"]))
        
        # Apply risk per trade limit
        if units["risk"] == "percent":
            max_risk = balance * Decimal(str(position_config["risk_per_trade"]))
        else:  # "usd"
            max_risk = Decimal(str(position_config["risk_per_trade"]))
            
        risk_adjusted_size = min(kelly_size, max_risk * Decimal('20'))  # Assume 5% stop loss
        
        return min(risk_adjusted_size / current_price, 
                  Decimal(str(decision["amount"])) * balance / current_price)

    async def run(self, agent: TradingAgent, market_data: pd.DataFrame) -> Dict:
        self.market_data = market_data
        balance = self.initial_balance
        position = Decimal('0')
        entry_price = None
        take_profit_levels = agent.config.take_profit_levels.copy()
        
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

    def print_results(self, results: Dict, show_advanced: bool = False, use_unicorn: bool = False):
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
        
        if show_advanced and self.market_data is not None:
            visualizer = TradingVisualizer(self.market_data, self.trades)
            visualizer.plot_chart(use_unicorn=use_unicorn) 