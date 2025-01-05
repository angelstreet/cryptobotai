from rich.console import Console
from rich.theme import Theme
from .agent import TradingAgent
from typing import Dict, Any

# Create custom theme for trading colors
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

def print_trading_analysis(
    symbol: str,
    market_data: Dict[str, float],
    decision: Dict[str, Any],
    agent: TradingAgent,
    show_reasoning: bool = False
):
    if show_reasoning:
        action_style = {'BUY': 'buy', 'SELL': 'sell', 'HOLD': 'hold'}.get(decision['action'], 'white')
        console.print(f"[{action_style}]{decision['action']:4}[/] | "
                     f"Position: {agent.current_position:.3f} | "
                     f"Size: {decision['amount']:.2f} | "
                     f"Conf: {decision['confidence']}% | "
                     f"Reason: {decision['reasoning']}")
    
    console.print("\n" + "=" * 50, style="header") 