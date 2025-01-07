from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from datetime import datetime
from typing import Dict, Any
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

def print_debug_info(debug_str: str, decision: dict = None):
    """Print debug information"""
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

def print_trading_analysis(debug_str: str, decision: dict):
    """Print trading analysis and decision"""
    console.print("\n[dim]─── Trading Analysis ───[/]")
    console.print(debug_str)
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
    console.print("\n[dim]─── API Configuration ───[/]")
    table = Table(show_edge=False, box=None, padding=(0, 1))
    table.add_column("Provider", style="dim")
    table.add_column("Model", style="dim")
    
    # Get provider with better default handling
    provider = os.getenv('AI_PROVIDER', 'LOCAL')
    
    # Only add temperature and max_tokens columns for non-local providers
    if provider != 'LOCAL':
        table.add_column("Temperature", style="dim")
        table.add_column("Max Tokens", style="dim")
    
    table.add_column("Base URL", style="dim")
    
    row = [provider, config.model or 'N/A']
    
    # Add temperature and max_tokens only for non-local providers
    if provider != 'LOCAL':
        row.extend([
            str(getattr(config, 'temperature', 'N/A')),
            str(getattr(config, 'max_tokens', 'N/A'))
        ])
    
    # Handle None client in mock mode
    base_url = client.base_url if client else 'MOCK'
    row.append(base_url)
    
    table.add_row(*row)
    console.print(table)

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

def print_api_error(error: str):
    """Print API error response"""
    console.print(f"API Error Response: {error}", style="error")

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

def print_ai_prompt(prompt: str):
    """Print AI prompt in debug mode"""
    console.print("\n[dim]─── AI Prompt ───[/]")
    console.print(prompt)

def print_parse_error(error: str, response: str):
    """Print error information when parsing AI response"""
    console.print(f"[error]Error parsing response: {error}[/]")
    console.print(f"[dim]Raw response:[/]\n{response}")

def print_trading_error(error: str):
    """Print error when generating trading decision"""
    console.print(f"[error]Error generating trading decision: {error}[/]")

def print_ai_response(response: str):
    """Print AI response in debug mode"""
    console.print("[dim]─── AI Response ───[/]")
    console.print(response)

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

def print_loading_start(exchange: str):
    """Print market data loading start message"""
    console.print("\n[dim]─── Data Loading ───[/]")
    console.print(f"Loading market data from {exchange.upper()}...", style="info")

def print_loading_complete():
    """Print market data loading complete message"""
    console.print("Market data loading complete.", style="success")

def print_api_params(config=None):
    """Print API configuration parameters"""
    console.print("\n[dim]─── API Configuration ───[/]")
    table = Table(show_edge=False, box=None, padding=(0, 1))
    table.add_column("Provider", style="dim")
    table.add_column("Model", style="dim")
    table.add_column("Temperature", style="dim")
    table.add_column("Max Tokens", style="dim")
    table.add_column("Base URL", style="dim")
    
    # Get provider with better default handling
    provider = os.getenv('AI_PROVIDER', 'LOCAL')
    if not provider:
        provider = 'LOCAL'
    
    row = [
        provider,
        config.model if config else 'llama2',
        str(config.temperature if config else '0.7'),
        str(config.max_tokens if config else '200'),
        os.getenv("API_URL", "http://localhost:11434")
    ]
    
    table.add_row(*row)
    console.print(table)

def print_portfolio(portfolio: Dict):
    """Print current portfolio summary"""
    console.print("\n[dim]─── Portfolio Summary ───[/]")
    
    table = Table(show_edge=False, box=None, padding=(0, 1))
    table.add_column("Exchange", style="dim")
    table.add_column("Symbol", style="dim")
    table.add_column("Amount", style="dim")
    table.add_column("Mean Price", style="dim")
    table.add_column("Current Value", justify="right", style="dim")
    table.add_column("P/L", justify="right", style="dim")
    
    total_value = 0.0
    
    for exchange, positions in portfolio['positions'].items():
        for symbol, pos in positions.items():
            amount = pos['amount']
            mean_price = pos['mean_price']
            current_price = pos.get('current_price', mean_price)
            
            position_value = amount * current_price
            total_value += position_value
            
            pl_pct = ((current_price - mean_price) / mean_price) * 100
            pl_style = "green" if pl_pct >= 0 else "red"
            
            table.add_row(
                exchange,
                symbol,
                f"{amount:.8f}",
                f"${mean_price:,.2f}",
                f"${position_value:,.2f}",
                f"[{pl_style}]{pl_pct:+.2f}%[/]"
            )
    
    console.print(table)
    console.print(f"\nTotal Portfolio Value: ${total_value:,.2f}")

def print_transactions(portfolio: Dict, exchange: str, symbol: str):
    """Print transaction history for specific crypto"""
    if exchange not in portfolio['positions'] or symbol not in portfolio['positions'][exchange]:
        console.print(f"\nNo transactions found for {symbol} on {exchange}")
        return
        
    position = portfolio['positions'][exchange][symbol]
    
    console.print(f"\n[dim]─── Transaction History: {exchange} {symbol} ───[/]")
    
    table = Table(show_edge=False, box=None, padding=(0, 1))
    table.add_column("Date", style="dim")
    table.add_column("Action", style="dim")
    table.add_column("Amount", style="dim")
    table.add_column("Price", style="dim")
    table.add_column("Total", justify="right", style="dim")
    
    for tx in position['transactions']:
        action_style = "green" if tx['action'] == 'BUY' else "red"
        total = tx['amount'] * tx['price']
        
        table.add_row(
            tx['date'],
            f"[{action_style}]{tx['action']}[/]",
            f"{tx['amount']:.8f}",
            f"${tx['price']:,.2f}",
            f"${total:,.2f}"
        )
    
    console.print(table)

def print_mock_loading():
    """Print mock data loading message"""
    console.print("\n[dim]─── Mock Data Loading ───[/]")
    console.print("Loading mock market data...", style="info")
    console.print("Mock data loaded successfully.", style="success")

def print_mock_trading():
    """Print mock trading message"""
    console.print("\n[dim]─── Mock Trading ───[/]")
    console.print("Generating mock trading decision...", style="info")
