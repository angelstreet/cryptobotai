from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from datetime import datetime
from typing import Dict, Any
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
console = Console(theme=SHARED_THEME)

def print_friendly_table(data: Dict[str, Any], title: str = "Data Overview"):
    """
    Print any dictionary in a friendly table format using rich, with dynamic formatting based on column titles.

    Args:
        data (Dict[str, Any]): The dictionary to display.
        title (str): The title of the table (default: "Data Overview").
    """
    console = Console()
    
    table = Table(title=title, show_header=True, header_style="bold magenta")
    
    # Determine the columns dynamically, preserving the order of keys
    columns = []  # Use a list to preserve order
    for crypto, details in data.items():
        if isinstance(details, dict):
            # Add keys to the columns list in the order they appear
            for key in details.keys():
                if key not in columns:  # Avoid duplicates
                    columns.append(key)
            break  # Stop after the first cryptocurrency to get the keys
    
    # Add the "Cryptocurrency" column first
    table.add_column("Cryptocurrency", style="cyan", justify="left")
    
    # Add the remaining columns in the order of keys
    for column in columns:
        table.add_column(column.capitalize(), justify="right")
    
    # Iterate through the dictionary and add rows
    for crypto, details in data.items():
        if isinstance(details, dict):
            # Start the row with the cryptocurrency name
            row = [crypto.capitalize()]
            
            # Add values for each column in the correct order
            for column in columns:
                value = details.get(column, "N/A")
                
                # Format the value based on the column title
                formatted_value = format_value(value, column)
                row.append(formatted_value)
            
            # Add the row to the table
            table.add_row(*row)
        else:
            # Handle flat dictionaries (if any)
            table.add_row(crypto.capitalize(), format_value(details))
    
    # Print the table
    console.print(table)

def format_value(value: Any, column: str) -> str:
    """
    Format a value for display in the table based on the column title.

    Args:
        value (Any): The value to format.
        column (str): The column title (used to determine formatting).

    Returns:
        str: The formatted value.
    """
    if isinstance(value, (float, int)):
        # Handle numeric values
        if "last" in column.lower():
            # Convert timestamp to readable date-time
            try:
                timestamp = int(value)  # Convert to integer
                return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                return str(value)  # Return as-is if conversion fails
        elif "usd" in column.lower():
            return f"${value:,.2f}"  # USD currency format
        elif "eur" in column.lower():
            return f"€{value:,.2f}"  # EUR currency format
        elif "change" in column.lower():
            return f"{value:,.2f}%"  # Percentage change format
        else:
            return f"{value:,.2f}"  # Default number format
    else:
        return str(value)  # Convert other types to strings

def print_backtest_results(results: Dict):
    """Print backtest results"""
    console.print("\n[dim]─── Backtest Results ───[/]")
    
    console.print(f"Initial Balance: ${results['initial_balance']:,.2f}")
    console.print(f"Final Balance: ${results['final_balance']:,.2f}")
    
    total_return = ((results['final_balance'] - results['initial_balance']) / results['initial_balance']) * 100
    return_str = f"Total Return: {total_return:+.2f}%"
    console.print(return_str, style="profit" if total_return > 0 else "loss") 

def print_market_config(exchange: str, symbol: str, timeframe: str, candles: int = None, 
                       start_date: datetime = None, end_date: datetime = None):
    """Print market configuration in a compact table"""
    console.print("\n[dim]─── Data Analysis ───[/]")
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

def print_trading_decision(decision: Dict, market_data: Dict = None, position: float = None, 
                         required_change: float = None, volatility_adjustment: float = None,
                         symbol: str = None):
    """Print trading decision with market data and reasoning"""
    console.print("\n[dim]─── Trading Decision ───[/]")
    
    # 1. Print market data line if available
    if market_data and symbol:
        debug_str = format_debug_str(
            market_data=market_data,
            position=position,
            symbol=symbol,
            required_change=required_change,
            volatility_adjustment=volatility_adjustment
        )
        console.print(debug_str)
    
    # 2. Print decision line
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
    
    # 3. Print agent reasoning
    console.print(f"Agent Reasoning: {decision['reasoning']}")

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

def print_risk_analysis(trade: Dict[str, Any], market_data: Dict[str, Any]):
    """Print risk analysis for a trade"""
    console.print("\n[dim]─── Risk Analysis ───[/]")
    
    table = Table(show_edge=False, box=None, padding=(0, 1))
    table.add_column("Action", style="dim")
    table.add_column("Amount", style="dim")
    table.add_column("Price", style="dim")
    table.add_column("Total Value", style="dim")
    table.add_column("Risk Level", style="dim")
    
    # Calculate total value of trade
    total_value = trade['amount'] * market_data['price']
    
    # Determine risk level
    if trade['action'] == 'BUY':
        risk_style = "red"
        risk_level = "Increasing"
    elif trade['action'] == 'SELL':
        risk_style = "green"
        risk_level = "Decreasing"
    else:
        risk_style = "white"
        risk_level = "Unchanged"
    
    table.add_row(
        trade['action'],
        f"{trade['amount']:.3f}",
        f"${market_data['price']:,.2f}",
        f"${total_value:,.2f}",
        f"[{risk_style}]{risk_level}[/]"
    )
    
    console.print(table)


