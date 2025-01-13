from typing import Dict, Optional
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
            self.console.print(f"[bold]{exchange_name}[/]")
            
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
        table.add_column("Subtotal", justify="right", style="dim")
        table.add_column("Fee", justify="right", style="dim")
        table.add_column("Total", justify="right", style="dim")
        
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
                            f"{currency}{order['execution_price']:,.2f}",
                            f"{currency}{order['subtotal']:,.2f}",
                            f"{currency}{order['fee']:,.2f}",
                            f"{currency}{order['total']:,.2f}"
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
        if symbol not in account.positions:
            # Create new position (only for BUY)
            account.positions[symbol] = Position(
                amount=float(amount),
                mean_price=float(price),
                estimated_cost_usd=float(total),
                estimated_value_usd=float(subtotal),
                orders=[order]
            )
        else:
            position = account.positions[symbol]
            current_amount = float(position.amount)
            current_cost = float(position.estimated_cost_usd)
            
            if action is Action.BUY: 
                new_amount = float(current_amount) + float(amount)
                new_cost = float(current_cost) + float(total)
                
                position.amount = float(new_amount)
                position.mean_price = float(new_cost / new_amount)
                position.estimated_cost_usd = float(new_cost)
                position.estimated_value_usd = float(new_amount * price)
            else: 
                new_amount = float(current_amount) - float(amount)
                position.amount = float(new_amount)
                position.estimated_cost_usd = float(new_amount * float(position.mean_price))
                position.estimated_value_usd = float(new_amount * float(price))

            position.orders.append(order)

        # Save changes immediately
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