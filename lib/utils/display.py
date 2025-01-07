from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from datetime import datetime
from typing import Dict

# Define shared theme
SHARED_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red",
    "success": "green",
    "aggressive": "red",
    "conservative": "blue",
    "default": "white"
})

# Create console instance
console = Console(theme=SHARED_THEME)

def print_debug_info(debug_str: str, decision: dict = None, show_reasoning: bool = False):
    """Print debug information with optional decision details"""
    if not show_reasoning:
        console.print(debug_str)
    else:
        # Print debug string first if provided
        if debug_str:
            console.print(debug_str)
        
        # Print decision details if available
        if decision:
            console.print(f"\n[bold]Decision:[/] {decision['action']} | "
                         f"Size: {decision['amount']:.2f} | "
                         f"Confidence: {decision['confidence']}%")
            if decision.get('reasoning'):
                console.print(f"[bold]Reasoning:[/] {decision['reasoning']}")

def print_header(symbol: str):
    """Print bot header"""
    console.print("\n=== Crypto AI Trading Bot ===", style="bold cyan")
    console.print(f"Trading {symbol}\n", style="bold")

def print_trading_analysis(debug_str: str, decision: dict, show_reasoning: bool = False):
    """Print trading analysis and decision"""
    if not show_reasoning:
        console.print(debug_str)
    else:
        console.print(f"\n[bold]Decision:[/] {decision['action']} | "
                     f"Size: {decision['amount']:.2f} | "
                     f"Confidence: {decision['confidence']}%")
        if decision.get('reasoning'):
            console.print(f"[bold]Reasoning:[/] {decision['reasoning']}")

def print_chart(data, symbol: str):
    """Print trading chart"""
    # Create table
    table = Table(title=f"{symbol} Market Data")
    
    # Add columns
    table.add_column("Time", justify="left", style="cyan")
    table.add_column("Price", justify="right")
    table.add_column("Change", justify="right")
    table.add_column("Volume", justify="right")
    
    # Add rows
    for index, row in data.iterrows():
        time = datetime.fromtimestamp(row['timestamp']/1000).strftime('%Y-%m-%d %H:%M')
        price = f"${row['close']:,.2f}"
        change = f"{((row['close'] - row['open'])/row['open']*100):+.2f}%"
        volume = f"{row['volume']:,.2f}"
        
        # Color code the change
        change_style = "red" if "-" in change else "green"
        table.add_row(time, price, change, volume, style=change_style)
    
    console.print(table) 

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