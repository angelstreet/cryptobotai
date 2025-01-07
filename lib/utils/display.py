from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from datetime import datetime
from typing import Dict
import os

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
        if debug_str:
            console.print(debug_str)

        if decision:
            console.print(f"\n[bold]Decision:[/] {decision['action']} | "
                         f"Size: {decision['amount']:.2f} | "
                         f"Confidence: {decision['confidence']}%")
            if decision.get('reasoning'):
                console.print(f"[bold]Reasoning:[/] {decision['reasoning']}")

def print_header(symbol: str):
    """Print bot header"""
    console.print("=== Crypto AI Trading Bot ===", style="bold cyan")
    console.print(f"Trading {symbol}", style="bold")

def print_trading_analysis(debug_str: str, decision: dict, show_reasoning: bool = False):
    """Print trading analysis and decision"""
    console.print("\n[dim]─── Trading Analysis ───[/]")
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
    console.print("\n[dim]─── Trading Chart ───[/]")
    table = Table(title=f"{symbol} Market Data")
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
    console.print("\n[dim]─── Backtest Results ───[/]")
    
    console.print(f"Initial Balance: ${results['initial_balance']:,.2f}")
    console.print(f"Final Balance: ${results['final_balance']:,.2f}")
    
    total_return = ((results['final_balance'] - results['initial_balance']) / results['initial_balance']) * 100
    return_str = f"Total Return: {total_return:+.2f}%"
    console.print(return_str, style="profit" if total_return > 0 else "loss") 

def print_api_config(config, client, debug: bool = False):
    """Print API configuration details when in debug mode"""
    if not debug:
        return
        
    console.print("\n[dim]─── API Configuration ───[/]")
    table = Table(show_edge=False, box=None, padding=(0, 1))
    table.add_column("Provider", style="dim")
    table.add_column("Model", style="dim")
    table.add_column("Temperature", style="dim")
    table.add_column("Max Tokens", style="dim")
    table.add_column("Base URL", style="dim")
    
    # Get provider with better default handling
    provider = os.getenv('AI_PROVIDER', '').upper()
    if not provider:
        if 'localhost' in client.base_url:
            provider = 'LOCAL'
        elif 'anthropic' in client.base_url:
            provider = 'CLAUDE'
        elif 'openai' in client.base_url:
            provider = 'OPENAI'
        elif 'openrouter' in client.base_url:
            provider = 'OPENROUTER'
        else:
            provider = 'UNKNOWN'
    
    row = [
        provider,
        config.model or 'N/A',
        str(getattr(config, 'temperature', 'N/A')),
        str(getattr(config, 'max_tokens', 'N/A')),
        client.base_url or 'N/A'
    ]
    
    table.add_row(*row)
    console.print(table)

def print_market_config(exchange: str, symbol: str, timeframe: str, candles: int = None, 
                       start_date: datetime = None, end_date: datetime = None):
    """Print market configuration in a compact table"""
    console.print("\n[dim]─── Market Configuration ───[/]")
    table = Table(show_edge=False, box=None, padding=(0, 1))
    table.add_column("Exchange", style="dim")
    table.add_column("Symbol", style="dim")
    table.add_column("Timeframe", style="dim")
    table.add_column("Candles", style="dim")
    table.add_column("Date Range", style="dim")
    
    date_range = "N/A"
    if start_date and end_date:
        date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    elif start_date:
        date_range = f"From {start_date.strftime('%Y-%m-%d')}"
    elif end_date:
        date_range = f"Until {end_date.strftime('%Y-%m-%d')}"
    
    row = [
        exchange.upper(),
        symbol,
        timeframe,
        str(candles) if candles else "N/A",
        date_range
    ]
    
    table.add_row(*row)
    console.print(table) 

def print_trading_data(market_data: Dict, current_position: float, required_change: float = None, 
                      volatility_adjustment: float = None):
    """Print trading data analysis in a compact table"""
    console.print("\n[dim]─── Trading Data ───[/]")
    
    table = Table(show_edge=False, box=None, padding=(0, 1))
    table.add_column("Price", style="dim")
    table.add_column("Change", style="dim")
    table.add_column("Volume", style="dim")
    table.add_column("Position", style="dim")
    if required_change is not None:
        table.add_column("Required", style="dim")
        table.add_column("Volatility", style="dim")
    
    row = [
        f"${market_data['price']:,.2f}",
        f"{market_data['change_24h']:+.4f}%",
        f"{market_data['volume']:.2f}",
        f"{current_position:.3f}"
    ]
    
    if required_change is not None:
        row.extend([
            f"{required_change:.4f}%",
            f"{volatility_adjustment:.2f}x" if volatility_adjustment else "N/A"
        ])
    
    table.add_row(*row)
    console.print(table) 

def print_api_error(error: str):
    """Print API error response"""
    console.print(f"API Error Response: {error}", style="error")

def print_trading_decision(decision: Dict, show_reasoning: bool = True):
    """Print trading decision and reasoning"""
    console.print("\n[dim]─── Trading Decision ───[/]")
    
    # Color-code the action
    action_style = {
        'HOLD': 'dim',
        'BUY': 'green',
        'SELL': 'red'
    }.get(decision['action'], 'default')
    
    console.print(
        f"Action: [{action_style}]{decision['action']}[/] | "
        f"Size: {decision['amount']:.2f} | "
        f"AI Confidence: {decision['confidence']}% (Need: {decision.get('min_confidence', 40)}%)"
    )
    
    if show_reasoning and decision.get('reasoning'):
        console.print("\n[dim]─── AI Reasoning ───[/]")
        console.print(decision['reasoning'])

def print_trading_params(params: Dict):
    """Print trading parameters in a compact table"""
    console.print("\n[dim]─── Trading Parameters ───[/]")
    params_table = Table(show_edge=False, box=None, padding=(0, 1))
    params_table.add_column("Min Conf", style="dim")
    params_table.add_column("Base Thresh", style="dim")
    params_table.add_column("Position Range", style="dim")
    params_table.add_column("Stop Loss", style="dim")
    
    # Access nested config values correctly
    min_confidence = params.get('min_confidence', 'N/A')
    base_threshold = params.get('base_threshold', 'N/A')
    min_position = params.get('position_sizing', {}).get('min_position_size', 'N/A')
    max_position = params.get('position_sizing', {}).get('max_position_size', 'N/A')
    stop_loss = params.get('stop_loss', {}).get('initial', 'N/A')
    trailing_stop = params.get('stop_loss', {}).get('trailing', 'N/A')
    
    params_table.add_row(
        f"{min_confidence}%",
        f"{base_threshold:.4f}%" if isinstance(base_threshold, (int, float)) else "N/A",
        f"{min_position}-{max_position}",
        f"{stop_loss}% (Trail: {trailing_stop}%)"
    )
    console.print(params_table)

def print_candle_analysis(market_data: Dict, config: Dict, decision: Dict, position: float, 
                         required_change: float, volatility_adjustment: float, symbol: str):
    """Print detailed candle analysis with configuration and decision"""
    # Print separator
    console.print("─" * 120, style="dim")
    
    # Print debug line using shared format
    debug_str = format_debug_str(
        market_data=market_data,
        position=position,
        symbol=symbol,
        required_change=required_change,
        volatility_adjustment=volatility_adjustment,
        include_decision=True,
        decision=decision
    )
    console.print(debug_str)
    
    # Print detailed analysis
    console.print(f"[bold cyan]Candle #{market_data.get('candle_number', 0)}:[/] "
                 f"[bold]Config:[/] Min Conf: {config.trading_params['min_confidence']}% | "
                 f"Base Thresh: {config.price_change_threshold['base']:.4f}% | "
                 f"Pos Range: {config.position_sizing['min_position_size']:.1f}-{config.position_sizing['max_position_size']:.1f} | "
                 f"SL: {config.stop_loss['initial']:.1f}% (Trail: {config.stop_loss['trailing']:.1f}%) | "
                 f"[bold]Market:[/] Change: {market_data['change_24h']:+.4f}% (Req: {required_change:.4f}%) | "
                 f"Vol: {market_data['volume']:.2f} | "
                 f"H-L Range: {market_data['high_low_range']:.2f}% | "
                 f"Position: {position:.3f} | "
                 f"[bold]Decision:[/] {decision['action']} | Size: {decision['amount']:.2f} | AI Conf: {decision['confidence']}% | "
                 f"[bold]Reason:[/] {decision['reasoning']}")

def print_trading_check(params: Dict, decision: Dict, position: float):
    """Print trading parameters check"""
    # 1. Trading Parameters
    console.print("\n[dim]─── Trading Parameters ───[/]")
    params_table = Table(show_edge=False, box=None, padding=(0, 1))
    params_table.add_column("Min Conf", style="dim")
    params_table.add_column("Base Thresh", style="dim")
    params_table.add_column("Position Range", style="dim")
    params_table.add_column("Stop Loss", style="dim")
    
    # Access nested config values correctly
    min_confidence = params.get('min_confidence', 'N/A')
    base_threshold = params.get('base_threshold', 'N/A')
    min_position = params.get('position_sizing', {}).get('min_position_size', 'N/A')
    max_position = params.get('position_sizing', {}).get('max_position_size', 'N/A')
    stop_loss = params.get('stop_loss', {}).get('initial', 'N/A')
    trailing_stop = params.get('stop_loss', {}).get('trailing', 'N/A')
    
    params_table.add_row(
        f"{min_confidence}%",
        f"{base_threshold:.4f}%" if isinstance(base_threshold, (int, float)) else "N/A",
        f"{min_position}-{max_position}",
        f"{stop_loss}% (Trail: {trailing_stop}%)"
    )
    console.print(params_table)

    # 2. Decision
    console.print("\n[dim]─── Trading Decision ───[/]")
    console.print(f"Action: {decision['action']} | "
                 f"Size: {decision['amount']:.2f} | "
                 f"Confidence: {decision['confidence']}%")

def print_size_adjustment(new_size: float):
    """Print size adjustment message"""
    console.print(f"[dim]Adjusted size to minimum: {new_size:.2f}[/]") 

def format_debug_str(market_data: Dict, position: float, symbol: str, 
                    required_change: float = None, volatility_adjustment: float = None,
                    include_decision: bool = False, decision: Dict = None) -> str:
    """Format debug string with market data"""
    debug_str = (
        f"Candle#{market_data.get('candle_number', 0):04d} | "
        f"{symbol} | "
        f"Price: ${market_data['price']:,.2f} | "
        f"Change: {market_data['change_24h']:+.4f}% | "
        f"Vol: {market_data['volume']:.2f} | "
        f"Pos: {position:.3f}"
    )
    
    if required_change is not None:
        debug_str += f" | Req: {required_change:.4f}% (Vol: {volatility_adjustment:.2f}x)"
        
    if include_decision and decision:
        debug_str += f" | {decision['action']} ({decision['confidence']}%)"
        
    return debug_str 