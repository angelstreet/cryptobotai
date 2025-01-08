from typing import Dict, Any, Optional
from lib.utils.display import print_risk_analysis
from lib.agents.agent import Agent
from lib.models.portfolio import Portfolio, Position, OrderDetails
from rich.console import Console
import json
from datetime import datetime

console = Console()

class PortfolioManagerAgent(Agent):
    def __init__(self, config, data_analyst=None):
        super().__init__(config)
        self.debug = False
        self.portfolio_file = 'portfolio.json'
        self.portfolio = self._load_portfolio()
        self.data_analyst = data_analyst

    def set_debug(self, debug: bool):
        self.debug = debug

    def set_portfolio_file(self, filepath: str):
        """Set portfolio file path"""
        self.portfolio_file = filepath
        self.portfolio = self._load_portfolio()

    def _load_portfolio(self) -> Portfolio:
        """Load portfolio from file"""
        try:
            with open(self.portfolio_file, 'r') as f:
                data = json.load(f)
                return Portfolio.parse_obj(data)
        except FileNotFoundError:
            return Portfolio()

    def _save_portfolio(self):
        """Save portfolio to file"""
        with open(self.portfolio_file, 'w') as f:
            portfolio_dict = self.portfolio.model_dump(mode='json')
            json.dump(portfolio_dict, f, indent=4)

    def get_position(self, symbol: str) -> Optional[Position]:
        """Get current position for symbol"""
        return self.portfolio.positions.get(symbol)

    def update_position(self, symbol: str, action: str, amount: float, price: float):
        """Update portfolio position after a trade"""
        # Create new trade
        trade = OrderDetails(
            order_id=f"{action.lower()}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            pair=f"{symbol.split('/')[0]}-EUR",
            order_type=f"Market {action.title()}",
            status="Filled",
            last_filled=datetime.now(),
            amount=amount,
            execution_price=price,
            subtotal=amount * price,
            fee=amount * price * 0.001,  # 0.1% fee
            total=amount * price * 1.001
        )
        
        if symbol not in self.portfolio.positions:
            if action == 'BUY':
                self.portfolio.positions[symbol] = Position(
                    amount=amount,
                    mean_price=price,
                    cost_eur=trade.total,
                    value_eur=trade.subtotal,
                    orders=[trade]
                )
        else:
            position = self.portfolio.positions[symbol]
            if action == 'BUY':
                # Update mean price and totals
                total_value = (position.amount * position.mean_price) + (amount * price)
                new_amount = position.amount + amount
                position.mean_price = total_value / new_amount
                position.amount = new_amount
                position.cost_eur += trade.total
                position.value_eur = position.amount * price
            elif action == 'SELL':
                position.amount = max(0.0, position.amount - amount)
                if position.amount == 0:
                    del self.portfolio.positions[symbol]
                    return
                position.value_eur = position.amount * price
                
            position.orders.append(trade)
            
        self._save_portfolio()

    def evaluate_trade(self, trade_suggestion: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate trade suggestion against risk parameters"""
        if self.debug:
            print_risk_analysis(trade_suggestion, market_data)
            
        return trade_suggestion

    def print_portfolio(self):
        """Print current portfolio status"""
        from lib.utils.display import print_portfolio
        portfolio_dict = self.portfolio.dict()
        # Add current prices and rates from data analyst
        portfolio_dict['estimated_prices'] = self.data_analyst.estimated_prices
        portfolio_dict['currency_rates'] = self.data_analyst.currency_rates
        print_portfolio(portfolio_dict)

    def print_orders(self, order_id: Optional[str] = None):
        """Print orders overview or specific order details"""
        from lib.utils.display import print_orders_compact, print_order_details
        
        if order_id:
            # Find and print specific order
            for pos in self.portfolio.positions.values():
                for order in pos.orders:
                    if order.order_id == order_id:
                        print_order_details(order.dict())
                        return
            console.print(f"Order {order_id} not found")
        else:
            # Print compact overview
            print_orders_compact(self.portfolio.dict())

    def set_exchange(self, exchange: str):
        """Set exchange for portfolio"""
        self.portfolio.exchange = exchange 

    def update_market_data(self, market_data: Dict[str, Any]):
        """Update portfolio with latest market data"""
        if 'currency_rates' in market_data:
            self.portfolio.currency_rates = market_data['currency_rates']
        
        # Update estimated prices
        symbol = market_data['symbol']
        self.portfolio.estimated_prices[symbol] = market_data['price']
        
        self._save_portfolio()

    def convert_currency(self, amount: float, from_currency: str = 'USD', to_currency: str = None) -> float:
        """Convert amount between currencies"""
        if not to_currency or from_currency == to_currency:
            return amount
        return amount * self.data_analyst.get_currency_rate(from_currency, to_currency) 

    def set_data_analyst(self, data_analyst):
        """Set data analyst reference"""
        self.data_analyst = data_analyst 