from rich.console import Console
from rich.theme import Theme
from .agent import TradingAgent

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

def print_trading_analysis(symbol: str, market_data: dict, decision: dict, agent: TradingAgent, show_reasoning: bool):
    """Print trading analysis with configurable detail level"""
    console.print("\n" + "=" * 50, style="header")
    console.print(f"TRADING ANALYSIS FOR {symbol}", style="header")
    console.print("=" * 50 + "\n", style="header")
    
    # Market Data Section
    console.print("Market Data:", style="info")
    console.print("-" * 30)
    console.print(f"Current Price: ${market_data['price']:,.2f}")
    # Format and color the change value
    change_value = f"{market_data['change_24h']:+.2f}%"
    if market_data['change_24h'] < 0:
        change_str = f"24h Change: [loss]{change_value}[/]"
    else:
        change_str = f"24h Change: [profit]{change_value}[/]"
    console.print(change_str)
    
    if show_reasoning:
        console.print(f"24h Volume: {market_data['volume']:,.2f}")
        range_str = f"24h Range: {market_data['high_low_range']:.2f}% "
        range_str += f"(High: ${market_data['high_24h']:,.2f}, Low: ${market_data['low_24h']:,.2f})"
        console.print(range_str)
        
        # Volatility Analysis Section
        console.print("\nVolatility Analysis:", style="info")
        console.print("-" * 30)
        console.print("Recent price changes:")
        for i, change in enumerate(market_data['historical_changes'][:5]):
            change_value = f"{change:+.3f}%"
            if change < 0:
                change_str = f"  {i+1}h ago: [loss]{change_value}[/]"
            else:
                change_str = f"  {i+1}h ago: [profit]{change_value}[/]"
            console.print(change_str)

    if agent.entries:
        console.print("Entry Points:")
        for i, entry in enumerate(agent.entries, 1):
            profit_loss = ((market_data['price'] - entry['price']) / entry['price']) * 100
            entry_str = f"  {i}. Amount: {entry['amount']:.3f} @ ${entry['price']:,.2f}"
            if show_reasoning:
                pl_value = f"{profit_loss:+.2f}%"
                entry_str += f" ({entry['timestamp'].strftime('%Y-%m-%d %H:%M')}) P/L: "
                if profit_loss < 0:
                    entry_str += f"[loss]{pl_value}[/]"
                else:
                    entry_str += f"[profit]{pl_value}[/]"
            console.print(entry_str)
    
    # Decision Section
    console.print("\nDecision:", style="info", end=" ")
    action_style = {
        'BUY': 'buy',
        'SELL': 'sell',
        'HOLD': 'hold'
    }.get(decision['action'], 'white')
    console.print(decision['action'], style=action_style)
    console.print("-" * 30)
    console.print(f"Current Position: {agent.current_position:.3f}")
    console.print(f"Position Size: {decision['amount']:.2f}")
    console.print(f"Confidence: {decision['confidence']}%")
    
    
    if show_reasoning:
        console.print("\nDetailed Analysis:", style="info")
        console.print("-" * 30)
        console.print(f"Reasoning:\n{decision['reasoning']}")
    
    console.print("\n" + "=" * 50, style="header") 