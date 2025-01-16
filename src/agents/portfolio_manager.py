from typing import Dict, Optional
from rich.console import Console
from rich.table import Table, box
from datetime import datetime
from pathlib import Path
import json
from dotenv import load_dotenv
from crewai import Agent
from src.config.models.portfolio import AccountType, Action
from src.agents.data_analyst import BTC, ETH
import src.agents.data_analyst as dt
from coinbase.rest import RESTClient
import os
from rich.console import Console
console = Console()  # Create console instance for colored output
from pydantic import Field, ConfigDict

from src.config.models.portfolio import (
    Portfolio, Position, OrderDetails, Exchange, 
    Account, AccountType, Action
)

class PortfolioPrinter:
    def __init__(self, console: Console):
        self.console = console

    def print_transaction_added(self, action: Action, amount: float, symbol: str, 
                              price: float, exchange: str, account: str):
        self.console.print(
            f"\n[green]{action.value}[/] {amount} {symbol} @ {price:,.2f} "
            f"on {exchange} ({account})"
        )

    def get_portfolio(self, portfolio: Dict, coingecko_prices: Dict):
        self.console.print("\n[dim]─── Portfolio Overview ───[/]")

    def print_portfolio(self, portfolio: Dict):
        """
        Print the portfolio overview using rich.
        
        Args:
            portfolio (Dict): Updated portfolio data.
        """
        self.console.print("\n[dim]─── Portfolio Overview ───[/]")
        
        currency = portfolio.get('display_currency', '$')
        total_portfolio_value = 0
        total_cost = 0
        total_pnl = 0

        for exchange_name, exchange in portfolio['exchanges'].items():
            self.console.print(f"[bold]{exchange_name}[/]")
            
            if not exchange['accounts']:
                print("Empty portfolio...continue")
                continue

            for account_id, account in exchange['accounts'].items():
                account_value = 0
                account_cost = 0
                account_pnl = 0

                table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
                table.add_column(f"{account['name']}", style="dim", justify="left")
                table.add_column("Amount", justify="right", style="cyan")
                table.add_column("Cost", justify="right", style="cyan")
                table.add_column("Value", justify="right", style="cyan")
                table.add_column("PNL", justify="right", style="cyan")
                table.add_column("PNL %", justify="right", style="cyan")

                for symbol, pos in account['positions'].items():
                    table.add_row(
                        symbol,
                        f"{pos['amount']:.4f}",
                        f"{currency}{pos['mean_price']:,.2f}",
                        f"{currency}{pos['total_value']:,.2f}",
                        f"[green]{currency}{pos['pnl']:,.2f}[/]" if pos['pnl'] >= 0 else f"[red]{currency}{pos['pnl']:,.2f}[/]",
                        f"[green]{pos['pnl_percentage']:+.2f}%[/]" if pos['pnl'] >= 0 else f"[red]{pos['pnl_percentage']:+.2f}%[/]"
                    )

                    account_value += pos['total_value']
                    account_cost += pos['amount'] * pos['mean_price']
                    account_pnl += pos['pnl']

                total_portfolio_value += account_value
                total_cost += account_cost
                total_pnl += account_pnl

                table.add_row(
                    "[bold]Total[/]", "", "",
                    f"[bold]{currency}{account_value:,.2f}[/]",
                    f"[green]{currency}{account_pnl:,.2f}[/]" if account_pnl >= 0 else f"[red]{currency}{account_pnl:,.2f}[/]",
                    f"[green]{(account_pnl / account_cost) * 100:+.2f}%[/]" if account_pnl >= 0 else f"[red]{(account_pnl / account_cost) * 100:+.2f}%[/]"
                )
                self.console.print(table)

    def print_orders(self, portfolio: Dict, exchange: Optional[str] = None, 
                    account: Optional[str] = None, order_id: Optional[str] = None):
        table = Table(show_edge=True, box=None)
        table.add_column("Exchange", style="dim")
        table.add_column("Account", style="dim")
        table.add_column("Market", style="dim")
        table.add_column("Type", style="dim")
        table.add_column("Date", style="dim")
        table.add_column("Amount", justify="right", style="dim")
        table.add_column("Price", justify="right", style="dim")
        table.add_column("Subtotal", justify="right", style="dim")
        table.add_column("Fee", justify="right", style="dim")
        table.add_column("Total", justify="right", style="dim")
        
        currency = portfolio.get('display_currency', '$')
        all_orders = []  # New list to collect all orders
        
        for exch_name, exch_data in portfolio['exchanges'].items():
            if exchange and exchange != exch_name:
                continue
                
            for acc_id, acc_data in exch_data['accounts'].items():
                if account and account != acc_id:
                    continue
                    
                for symbol, pos in acc_data['positions'].items():
                    for order in pos['orders']:
                        if order_id and order['order_id'] != order_id:
                            continue
                        # Collect order info with exchange and account details
                        all_orders.append({
                            'exchange': exch_name,
                            'account': acc_data['name'],
                            'order': order
                        })
        
        # Sort orders by date (newest first)
        all_orders.sort(key=lambda x: x['order']['last_filled'], reverse=True)
        
        # Add sorted orders to table
        for order_info in all_orders:
            order = order_info['order']
            order_style = "green" if "Buy" in order['order_type'] else "red"
            
            table.add_row(
                order_info['exchange'],
                order_info['account'],
                order['pair'],
                f"[{order_style}]{order['order_type']}[/]",
                order['last_filled'],
                f"x{order['amount']:.6f}",
                f"{currency}{order['execution_price']:,.2f}",
                f"{currency}{order['subtotal']:,.2f}",
                f"{currency}{order['fee']:,.2f}",
                f"{currency}{order['total']:,.2f}"
            )
        
        self.console.print("\n[dim]─── Orders Overview ───[/]")
        self.console.print(table)

class PortfolioManagerAgent(Agent):
    """Agent responsible for portfolio management"""
    # Pydantic configuration
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # Declare fields using Pydantic's Field
    config: Dict = Field(default_factory=dict)
    portfolio_path: str = Field(default=str(Path(__file__).parent.parent / 'config' / 'data' / 'portfolio.json'))
    printer: PortfolioPrinter = Field(default_factory=lambda: PortfolioPrinter(Console()))
    portfolio: Portfolio = Field(default_factory=Portfolio)
    coinbase_client: Optional[RESTClient] = Field(default=None)

    def __init__(self, config: Dict, **kwargs):
        super().__init__(
            role="Portfolio Manager and Risk Analyst",
            goal="Analyze portfolio performance, risk, and provide investment recommendations",
            backstory="""You are an experienced portfolio manager and risk analyst with expertise in 
            cryptocurrency markets. Your job is to analyze portfolio composition, assess risk levels, 
            evaluate diversification, and provide actionable recommendations.""",
            allow_delegation=False,
            llm=config.llm,
            verbose=True,
            tools=[],
        )
        self.config = config
        self._load_portfolio()  # Load portfolio immediately
        self._validate_portfolio_structure()  # Ensure all required fields exist
        self._initialize_virtual_exchange()  # Initialize virtual exchange if it doesn't exist        self.session = agentops.start_session(name=self.role)
            
    def _load_portfolio(self, path: Optional[str] = None) -> Portfolio:
        """Load portfolio from file, handling empty or invalid files"""
        if path:
            self.portfolio_path = path

        # Initialize a fresh portfolio if loading fails
        self.portfolio = Portfolio()

        try:
            with open(self.portfolio_path, 'r') as f:
                data = json.load(f)
                
                # Check if file is empty or missing required structure
                if not data or 'exchanges' not in data:
                    console.print("[yellow]Portfolio file is empty or invalid. Initializing a fresh portfolio.[/]")
                    return self.portfolio
                
                # Parse the portfolio data
                self.portfolio = Portfolio.parse_obj(data)
                console.print("[green]Portfolio loaded successfully![/]")
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Handle both missing file and invalid JSON
            console.print(f"[yellow]Error loading portfolio: {e}. Initializing a fresh portfolio.[/]")
        except Exception as e:
            console.print(f"[red]Unexpected error loading portfolio: {e}[/]")
        
        return self.portfolio

    def _validate_portfolio_structure(self) -> None:
        """Ensure portfolio has all required fields with valid types"""
        if not hasattr(self.portfolio, 'exchanges'):
            self.portfolio.exchanges = {}
            
        if not hasattr(self.portfolio, 'estimated_prices'):
            self.portfolio.estimated_prices = {}
            
        if not hasattr(self.portfolio, 'currency_rates'):
            self.portfolio.currency_rates = {
                "EUR/USD": 1.08,
                "USD/EUR": 0.926
            }
            
        if not hasattr(self.portfolio, 'display_currency'):
            self.portfolio.display_currency = '$'
            
        #self._save_portfolio()

    def _save_portfolio(self):
        console.print("Saving portfolio...")
        with open(self.portfolio_path, 'w') as f:
            portfolio_dict = self.portfolio.dict()
            json.dump(portfolio_dict, f, indent=4)

    def _create_exchange(self, name: str) -> Exchange:
        if name not in self.portfolio.exchanges:
            print("create exchange")
            self.portfolio.exchanges[name] = Exchange(name=name)
            self._save_portfolio()
        return self.portfolio.exchanges[name]

    def _create_account(self, exchange_name: str, account_id: str, 
                      account_name: str, account_type: AccountType) -> Account:
        print("create account")
        exchange = self._create_exchange(exchange_name)
        if account_id not in exchange.accounts:
            exchange.accounts[account_id] = Account(
                account_id=account_id,
                name=account_name,
                account_type=account_type
            )
            self._save_portfolio()
        return exchange.accounts[account_id]

    def update_portfolio(self) -> Dict:
        """
        Update the portfolio with the latest CoinGecko prices and recalculate metrics.
        
        Args:
            coingecko_prices (Dict): Latest prices from CoinGecko.
        
        Returns:
            Dict: Updated portfolio data.
        """
        portfolio_dict = self.portfolio.dict()
        coingecko_prices = dt.coingecko_get_price(
            crypto_ids=[BTC, ETH], 
            currency=self.config.display_currency
        )
        # Mapping from portfolio symbols to CoinGecko IDs
        symbol_to_coingecko = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "XRP": "xrp",
            "DOGE": "dogecoin",
            "USDT": "tether",
            "USDC": "usd-coin",
            "BTC/USDT": "bitcoin",
            "ETH/USDT": "ethereum",
            "SOL/USDT": "solana",
            "XRP/USDT": "xrp",
            "DOGE/USDT": "dogecoin",
        }

        # Update portfolio with latest prices and recalculate metrics
        for exchange_name, exchange in portfolio_dict['exchanges'].items():
            for account_id, account in exchange['accounts'].items():
                for symbol, position in account['positions'].items():
                    coingecko_id = symbol_to_coingecko.get(symbol, symbol.lower())
                    current_price = coingecko_prices.get(coingecko_id, {}).get('price', position['mean_price'])

                    # Update position with current price
                    position['current_price'] = current_price
                    position['total_value'] = position['amount'] * current_price
                    position['pnl'] = position['total_value'] - (position['amount'] * position['mean_price'])
                    position['pnl_percentage'] = (position['pnl'] / (position['amount'] * position['mean_price'])) * 100

        return portfolio_dict

    def show_portfolio(self) -> Dict:
        """
        Fetch the latest portfolio data, update it with CoinGecko prices, and display it.
        
        Returns:
            Dict: Updated portfolio data in JSON format.
        """
        updated_portfolio = self.update_portfolio()
        self.printer.print_portfolio(updated_portfolio)
        return updated_portfolio

    def show_orders(self, exchange:  Optional[str] = None, 
                   account: Optional[str] = None, order_id: Optional[str] = None):
        portfolio_dict = self.portfolio.dict()
        self.printer.print_orders(portfolio_dict, exchange, account, order_id)

    def add_transaction(self, exchange: str, account_id: str, symbol: str, 
                   amount: float, price: float, action: Action, fee_rate: float = 0.5) -> None:
        """Add a new transaction to a specific account in an exchange"""
        if exchange not in self.portfolio.exchanges or \
        account_id not in self.portfolio.exchanges[exchange].accounts:
            raise ValueError(f"Invalid exchange or account: {exchange}/{account_id}")

        account = self.portfolio.exchanges[exchange].accounts[account_id]
        
        # Calculate transaction values
        subtotal = amount * price                    # 0.5 * 70000 = 35000
        fee = subtotal * (fee_rate / float('100'))   # 35000 * (0.5/100) = 175
        total = subtotal + fee                       # 35000 + 175 = 35175
        
        # Create the order details
        order = OrderDetails(
            order_id=f"{action.value.lower()}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            pair=symbol,
            order_type=f"Market {action.value.title()}",
            amount=float(amount),
            execution_price=float(price),
            subtotal=float(subtotal),
            fee=float(fee),
            total=float(total),
            last_filled=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        if action.value == Action.SELL:
            if symbol not in account.positions:
                raise ValueError(f"Cannot SELL {symbol}: no position exists")
            current_amount = account.positions[symbol].amount
            if amount > current_amount:
                raise ValueError(f"Cannot SELL {amount} {symbol}: only {float(current_amount)} available")

        # Handle position creation or update
        base_asset = symbol.split('/')[0]
        if base_asset not in account.positions:
            # Create new position (only for BUY)
            print('create new position')
            account.positions[base_asset] = Position(
                amount=float(amount),
                mean_price=float(price),
                subtotal_cost=float(subtotal),  # Subtotal cost (without fees)
                total_cost=float(total),        # Total cost (including fees)
                total_fees=float(fee),          # Total fees
                orders=[order]                  # List of orders
            )
        else:
            print('update position')
            position = account.positions[base_asset]
            current_amount = float(position.amount)
            current_cost = float(position.subtotal_cost)
            current_fees = float(position.total_fees)
            current_total = float(position.total_cost)
            
            if action is Action.BUY: 
                new_amount = float(current_amount) + float(amount)
                new_subtotal_cost = float(current_cost) + float(subtotal)
                new_fees = float(current_fees) + float(fee)
                new_total_cost = float(current_total) + float(total)
                
                position.amount = float(new_amount)
                position.mean_price = float(new_subtotal_cost / new_amount)  # Recalculate mean price
                position.subtotal_cost = float(new_subtotal_cost)
                position.total_cost = float(new_total_cost)
                position.total_fees = float(new_fees)
            else: 
                # For SELL actions, reduce the amount and adjust costs
                new_amount = float(current_amount) - float(amount)
                position.amount = float(new_amount)
                position.subtotal_cost = float(new_amount * position.mean_price)
                position.total_cost = float(new_amount * position.mean_price) + float(position.total_fees)

            # Append the new order to the position's order history
            position.orders.append(order)

        # Save changes immediately
        self._save_portfolio()
        
        # Print confirmation
        self.printer.print_transaction_added(
            action, amount, symbol, price, exchange, account.name
        )

    def _initialize_virtual_exchange(self):
        """Initialize virtual exchange with a default simulation account if it doesn't exist"""
        # Create virtual exchange if it doesn't exist
        if "virtual" not in self.portfolio.exchanges:
            # Create the exchange
            virtual_exchange = Exchange(name="virtual")
            
            # Create a default simulation account
            virtual_account = Account(
                account_id="virtual-1",
                name="Portfolio 1",
                account_type=AccountType.VIRTUAL,
                positions={}
            )
            
            # Add the account to the exchange
            virtual_exchange.accounts["virtual-1"] = virtual_account
            
            # Add the exchange to the portfolio
            self.portfolio.exchanges["virtual"] = virtual_exchange
            
            # Ensure we have default currency rates if not already set
            if not self.portfolio.currency_rates:
                self.portfolio.currency_rates = {
                    "EUR/USD": 1.08,
                    "USD/EUR": 0.926
                }
            
            # Save the updated portfolio
            self._save_portfolio()
            
            # Use rich console for colored output
            self.printer.console.print(
                f"[green]Virtual exchange initialized with account: {virtual_account.name}[/]"
            )

    def delete_transaction(self, exchange: str, account_id: str, order_id: str) -> None:
        """
        Delete a transaction from a specific account in an exchange
        
        Args:
            exchange (str): Exchange name
            account_id (str): Account identifier
            order_id (str): Order ID to delete
        
        Raises:
            ValueError: If exchange, account or order not found
        """
        # Validate exchange and account exist
        if exchange not in self.portfolio.exchanges or \
           account_id not in self.portfolio.exchanges[exchange].accounts:
            raise ValueError(f"Invalid exchange or account: {exchange}/{account_id}")

        account = self.portfolio.exchanges[exchange].accounts[account_id]
        order_found = False
        
        # Search through all positions for the order
        for symbol, position in list(account.positions.items()):
            for order in list(position.orders):
                if order.order_id == order_id:
                    order_found = True
                    # Remove the order
                    position.orders.remove(order)
                    
                    # Recalculate position after removing order
                    if "Buy" in order.order_type:
                        position.amount -= order.amount
                    else:  # Sell
                        position.amount += order.amount
                    
                    # Update position values
                    if position.amount > 0:
                        position.estimated_value_usd = position.amount * position.mean_price
                    else:
                        # Remove position if no amount left
                        del account.positions[symbol]
                    
                    # Save changes
                    self._save_portfolio()
                    
                    # Use printer for output
                    self.printer.print_transaction_deleted(order_id, exchange, account.name)
                    return

        if not order_found:
            raise ValueError(f"Order {order_id} not found in {exchange}/{account_id}")

    def init_coinbase_client(self) -> None:
        """Initialize Coinbase client using environment variables."""
        load_dotenv()
        api_key = os.getenv('COINBASE_API_KEY', '')
        api_secret = os.getenv('COINBASE_API_SECRET', '')
        
        if not api_key or not api_secret:
            self.console.print("[yellow]Coinbase API key and secret not found in environment variables. Skipping Coinbase sync.[/]")
            return
        
        self.coinbase_client = RESTClient(api_key=api_key, api_secret=api_secret)
        console.print("[green]Coinbase client initialized successfully![/]")

    def sync_coinbase(self):
        """Sync Coinbase portfolio data with the portfolio."""
        if not self.coinbase_client:
            console.print("[yellow]Coinbase client not initialized...")
            self.init_coinbase_client() 
        
        console.print("\n[bold]Syncing Coinbase data...[/]")
        
        try:
            response = self.coinbase_client.get_portfolios()
            if not response or not hasattr(response, 'portfolios') or not response.portfolios:
                console.print("[yellow]No portfolios found in Coinbase response.[/]")
                return
            
            portfolios = response.portfolios
            coinbase_exchange = self._create_exchange("coinbase")
            
            for portfolio in portfolios:
                portfolio_id = portfolio.uuid  # Use 'uuid' as the portfolio ID
                portfolio_name = portfolio.name
                
                if not portfolio_id or not portfolio_name:
                    console.print(f"[yellow]Skipping invalid portfolio: {portfolio}[/]")
                    continue
                
                # Fetch portfolio breakdown for the portfolio
                breakdown_response = self.coinbase_client.get_portfolio_breakdown(portfolio_id)
                
                # Check if the breakdown response is valid
                if not breakdown_response or not hasattr(breakdown_response, 'breakdown'):
                    console.print(f"[yellow]No breakdown found for portfolio {portfolio_name}.[/]")
                    continue
                
                breakdown = breakdown_response.breakdown
                
                # Check if spot positions are available in the breakdown
                if not hasattr(breakdown, 'spot_positions') or not breakdown.spot_positions:
                    console.print(f"[yellow]No spot positions found for portfolio {portfolio_name}.[/]")
                    continue
                
                spot_positions = breakdown.spot_positions
                coinbase_account = self._create_account(
                    exchange_name="coinbase",
                    account_id=portfolio_id,
                    account_name=portfolio_name,
                    account_type=AccountType.REAL  # Use the correct enum value
                )
                
                for position in spot_positions:
                    symbol = position.asset  # Use 'asset' for the currency symbol
                    amount = float(position.total_balance_crypto)  # Use 'total_balance_crypto' for the amount
                    
                    # Extract the cost basis value from the dictionary
                    cost_basis = position.cost_basis
                    if isinstance(cost_basis, dict) and 'total_value' in cost_basis:
                        cost_basis_value = float(cost_basis['total_value'])
                    else:
                        cost_basis_value = 0.0  # Default to 0 if cost_basis is not a dictionary or missing 'total_value'
                    
                    # Convert cost basis to USD if it's in EUR
                    if cost_basis.get('currency') == "EUR":
                        cost_basis_value = cost_basis_value * self.portfolio.currency_rates["EUR/USD"]
                    
                    # Update the position for the currency
                    if symbol in coinbase_account.positions:
                        coinbase_account.positions[symbol].amount = amount
                    else:
                        coinbase_account.positions[symbol] = Position(
                            amount=amount,
                            mean_price=float(cost_basis_value) / float(amount),  # Recalculate mean price
                            subtotal_cost=float(cost_basis_value),
                            total_cost=float(cost_basis_value),
                            total_fees=0,
                            orders=[]
                        )
                
                # Save the updated portfolio
                self._save_portfolio()
                console.print("[green]Coinbase data synced successfully![/]")
            
        except Exception as e:
            console.print(f"[red]Error syncing Coinbase data: {e}[/]")
