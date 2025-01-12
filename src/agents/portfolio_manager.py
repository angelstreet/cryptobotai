from typing import Dict, Optional
from pydantic import Field, ConfigDict
from rich.console import Console
from rich.table import Table
from datetime import datetime
from pathlib import Path
import json

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

    def print_portfolio(self, portfolio: Dict):
        self.console.print("\n[dim]─── Portfolio Overview ───[/]")
        
        currency = portfolio.get('display_currency', '$')
        total_portfolio_value = 0
        
        for exchange_name, exchange in portfolio['exchanges'].items():
            self.console.print(f"\n[bold]{exchange_name}[/]")
            
            for account_id, account in exchange['accounts'].items():
                account_value = 0
                
                table = Table(show_edge=True, box=None)
                table.add_column(f"{account['name']}", style="dim")
                table.add_column("Amount", justify="right", style="dim")
                table.add_column("Price", justify="right", style="dim")
                table.add_column("Value", justify="right", style="dim")
                
                for symbol, pos in account['positions'].items():
                    current_price = portfolio['estimated_prices'].get(symbol, pos['mean_price'])
                    value = pos['amount'] * current_price
                    account_value += value
                    
                    table.add_row(
                        symbol.split('/')[0],
                        f"{pos['amount']:.4f}",
                        f"{currency}{current_price:,.2f}",
                        f"{currency}{value:,.2f}"
                    )
                
                total_portfolio_value += account_value
                table.add_row(
                    "[bold]Total[/]", "", "",
                    f"[bold]{currency}{account_value:,.2f}[/]"
                )
                self.console.print(table)
        
        self.console.print(f"\n[bold]Total Portfolio Value: {currency}{total_portfolio_value:,.2f}[/]")

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
        
        currency = portfolio.get('display_currency', '$')
        
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
                            
                        order_style = "green" if "Buy" in order['order_type'] else "red"
                        table.add_row(
                            exch_name,
                            acc_data['name'],
                            order['pair'],
                            f"[{order_style}]{order['order_type']}[/]",
                            order['last_filled'],
                            f"{order['amount']:.8f}",
                            f"{currency}{order['execution_price']:.2f}"
                        )
        
        self.console.print("\n[dim]─── Orders Overview ───[/]")
        self.console.print(table)

class PortfolioManagerAgent:
    """Agent responsible for portfolio management"""
    def __init__(self, config):
        self.portfolio_path = str(Path(__file__).parent.parent / 'config' / 'data' / 'portfolio.json')
        self.printer = PortfolioPrinter(Console())
        
        self.portfolio = self._load_portfolio()  # Load portfolio immediately
        self.validate_portfolio_structure()  # Ensure all required fields exist
        self.initialize_virtual_exchange()  # Initialize virtual exchange if it doesn't exist

    def _load_portfolio(self, path: Optional[str] = None) -> Portfolio:
        """Load portfolio from file, handling empty or invalid files"""
        if path:
            self.portfolio_path = path
        try:
            with open(self.portfolio_path, 'r') as f:
                data = json.load(f)
                
                # Check if file is empty or missing required structure
                if not data or 'exchanges' not in data:
                    # Return fresh portfolio
                    return Portfolio()
                
                return Portfolio.parse_obj(data)
                
        except (FileNotFoundError, json.JSONDecodeError):
            # Handle both missing file and invalid JSON
            return Portfolio()
        except Exception as e:
            print(f"[red]Error loading portfolio: {str(e)}[/red]")
            return Portfolio()

    def validate_portfolio_structure(self) -> None:
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
            
        self._save_portfolio()

    def _save_portfolio(self):
        with open(self.portfolio_path, 'w') as f:
            portfolio_dict = self.portfolio.dict()
            json.dump(portfolio_dict, f, indent=4)

    def create_exchange(self, name: str) -> Exchange:
        if name not in self.portfolio.exchanges:
            self.portfolio.exchanges[name] = Exchange(name=name)
            self._save_portfolio()
        return self.portfolio.exchanges[name]

    def create_account(self, exchange_name: str, account_id: str, 
                      account_name: str, account_type: AccountType) -> Account:
        exchange = self.create_exchange(exchange_name)
        if account_id not in exchange.accounts:
            exchange.accounts[account_id] = Account(
                account_id=account_id,
                name=account_name,
                account_type=account_type
            )
            self._save_portfolio()
        return exchange.accounts[account_id]

    def show_portfolio(self):
        """Display portfolio overview"""
        portfolio_dict = self.portfolio.dict()  # Now self.portfolio is a Portfolio instance
        self.printer.print_portfolio(portfolio_dict)

    def show_orders(self, exchange: Optional[str] = None, 
                   account: Optional[str] = None, order_id: Optional[str] = None):
        portfolio_dict = self.portfolio.dict()
        self.printer.print_orders(portfolio_dict, exchange, account, order_id)

    def add_transaction(self, exchange: str, account_id: str, symbol: str, 
                    amount: float, price: float, action: Action, fee_rate: float = 0.5) -> None:
        """
        Add a new transaction to a specific account in an exchange
        
        Args:
            exchange (str): Exchange name
            account_id (str): Account identifier
            symbol (str): Trading pair symbol
            amount (float): Transaction amount
            price (float): Execution price
            action (Action): BUY or SELL action
            fee_rate (float, optional): Fee rate as decimal. Defaults to 0.5 (0.5%)
        """
        if exchange not in self.portfolio.exchanges or \
           account_id not in self.portfolio.exchanges[exchange].accounts:
            raise ValueError(f"Invalid exchange or account: {exchange}/{account_id}")

        account = self.portfolio.exchanges[exchange].accounts[account_id]
        
        # Calculate transaction values
        subtotal = amount * price
        fee = subtotal * fee_rate
        total = subtotal + fee
        
        # Create the order details
        order = OrderDetails(
            order_id=f"{action.value.lower()}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            pair=symbol,
            order_type=f"Market {action.value.title()}",
            amount=amount,
            execution_price=price,
            subtotal=subtotal,
            fee=fee,  # Using calculated fee
            total=total  # Using calculated total
        )

        # Handle position creation or update
        if symbol not in account.positions:
            # Create new position
            position = Position(
                amount=amount,
                mean_price=price,
                estimated_cost_usd=amount * price,  # Changed from cost_eur
                estimated_value_usd=amount * price,  # Changed from value_eur
                orders=[order]
            )
            account.positions[symbol] = position
        else:
            # Update existing position
            position = account.positions[symbol]
            old_amount = position.amount
            old_cost = old_amount * position.mean_price

            if action == Action.BUY:
                # Update amount and recalculate mean price for buys
                new_amount = old_amount + amount
                new_cost = old_cost + (amount * price)
                position.amount = new_amount
                position.mean_price = new_cost / new_amount if new_amount > 0 else price
            else:  # SELL
                # Update amount for sells
                position.amount = max(0.0, old_amount - amount)
                
            # Update position value
            position.estimated_value_usd = position.amount * price  # Changed from value_eur
            
            # Append the order to the position's order history
            position.orders.append(order)
            
            # Remove position if amount is 0
            if position.amount == 0:
                del account.positions[symbol]

        # Save changes
        self._save_portfolio()
        
        # Print confirmation
        self.printer.print_transaction_added(
            action, amount, symbol, price, exchange, account.name
        )

    def initialize_virtual_exchange(self):
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
            print(f"[green]Virtual exchange initialized with account: {virtual_account.name}[/]")