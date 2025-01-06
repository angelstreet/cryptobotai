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