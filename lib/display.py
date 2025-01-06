from rich.console import Console
from rich.theme import Theme
from typing import Dict, Any
import plotly.graph_objects as go
from datetime import datetime

# Create shared theme that can be imported by other modules
SHARED_THEME = Theme({
    "buy": "bold green",
    "sell": "bold red",
    "hold": "dim white",
    "profit": "green",
    "loss": "red",
    "info": "bold blue",
    "header": "bold white",
    "error": "bold red"
})

# Use the shared theme
console = Console(theme=SHARED_THEME)

def print_trading_analysis(
    symbol: str,
    market_data: Dict[str, float],
    decision: Dict[str, Any],
    agent: Any,
    show_reasoning: bool = False
):
    # Import at function level to avoid circular import
    from .agent import TradingAgent
    
    if not isinstance(agent, TradingAgent):
        raise TypeError("agent must be an instance of TradingAgent")
        
    if show_reasoning:
        action_style = {'BUY': 'buy', 'SELL': 'sell', 'HOLD': 'hold'}.get(decision['action'], 'white')
        console.print(f"[{action_style}]{decision['action']:4}[/] | "
                     f"Position: {agent.current_position:.3f} | "
                     f"Size: {decision['amount']:.2f} | "
                     f"Conf: {decision['confidence']}% | "
                     f"Reason: {decision['reasoning']}")
    
    console.print("\n" + "=" * 50, style="header") 

def print_header(symbol: str):
    """Print the header for trading analysis"""
    console.print("\n" + "=" * 50, style="header")
    console.print(f"TRADING ANALYSIS FOR {symbol}", style="header")
    console.print("=" * 50, style="header") 

def print_chart(market_data, trades):
    """Print interactive trading chart"""
    fig = go.Figure()
    
    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=market_data['timestamp'],
        open=market_data['open'],
        high=market_data['high'],
        low=market_data['low'],
        close=market_data['close'],
        name='Price'
    ))
    
    # Add trade markers
    for trade in trades:
        marker_color = 'green' if trade['action'] == 'BUY' else 'red'
        fig.add_trace(go.Scatter(
            x=[trade['timestamp']],
            y=[trade['price']],
            mode='markers',
            marker=dict(size=10, color=marker_color, symbol='triangle-up' if trade['action'] == 'BUY' else 'triangle-down'),
            name=f"{trade['action']} @ {trade['price']:.2f}"
        ))
    
    fig.update_layout(title='Trading Chart with Signals')
    fig.show() 

def print_backtest_results(results: Dict):
    """Print backtest results"""
    console.print("\n" + "=" * 50, style="header")
    console.print("BACKTEST RESULTS", style="header")
    console.print("=" * 50, style="header")
    
    # Performance metrics
    console.print("\nPerformance Metrics:", style="info")
    console.print("-" * 30)
    console.print(f"Initial Balance: ${results['initial_balance']:,.2f}")
    console.print(f"Final Balance: ${results['final_balance']:,.2f}")
    
    total_return = ((results['final_balance'] - results['initial_balance']) / results['initial_balance']) * 100
    return_str = f"Total Return: {total_return:+.2f}%"
    console.print(return_str, style="profit" if total_return > 0 else "loss")

def print_debug_info(debug_str: str, decision: Dict[str, Any], show_reasoning: bool = False):
    """Print debug information"""
    if not show_reasoning:
        action_style = {
            'BUY': 'buy',
            'SELL': 'sell',
            'HOLD': 'dim white'
        }.get(decision['action'], 'dim white')
        debug_str += f" | [{action_style}]{decision['action']}[/] ({decision['confidence']}%)"
        console.print(debug_str) 