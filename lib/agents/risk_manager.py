from typing import Dict, Any, Optional
from lib.utils.display import print_risk_analysis
from lib.agents.agent import Agent
from lib.models.portfolio import Portfolio, Position, Transaction
import json
from datetime import datetime

class RiskManagerAgent(Agent):
    def __init__(self, config):
        super().__init__(config)
        self.debug = False
        self.portfolio_file = 'portfolio.json'
        self.portfolio = self._load_portfolio()

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
            # Convert portfolio to dict and handle datetime serialization
            portfolio_dict = self.portfolio.dict(
                json_encoders={
                    datetime: lambda dt: dt.isoformat()
                }
            )
            json.dump(portfolio_dict, f, indent=4)

    def get_position(self, exchange: str, symbol: str) -> Optional[Position]:
        """Get current position for symbol"""
        key = f"{exchange}:{symbol}"
        return self.portfolio.positions.get(key)

    def update_position(self, exchange: str, symbol: str, action: str, 
                       amount: float, price: float) -> None:
        """Update portfolio position after a trade"""
        if exchange not in self.portfolio.positions:
            self.portfolio.positions[exchange] = {}
            
        positions = self.portfolio.positions[exchange]
        
        # Create new transaction
        transaction = Transaction(
            date=datetime.now(),
            action=action,
            amount=amount,
            price=price
        )
        
        if symbol not in positions:
            if action == 'BUY':
                positions[symbol] = Position(
                    amount=amount,
                    mean_price=price,
                    transactions=[transaction]
                )
        else:
            position = positions[symbol]
            if action == 'BUY':
                # Update mean price
                total_value = (position.amount * position.mean_price) + (amount * price)
                new_amount = position.amount + amount
                position.mean_price = total_value / new_amount
                position.amount = new_amount
            elif action == 'SELL':
                position.amount = max(0.0, position.amount - amount)
                if position.amount == 0:
                    del positions[symbol]
                    return
                
            position.transactions.append(transaction)
            
        self._save_portfolio()

    def evaluate_trade(self, trade_suggestion: Dict[str, Any], 
                      market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate trade suggestion against risk parameters"""
        if self.debug:
            print_risk_analysis(trade_suggestion, market_data)
            
        # If trade approved, update portfolio
        if trade_suggestion['action'] != 'HOLD':
            self.update_position(
                exchange=market_data['exchange'],
                symbol=market_data['symbol'],
                action=trade_suggestion['action'],
                amount=trade_suggestion['amount'],
                price=market_data['price']
            )
            
        return trade_suggestion 

    def print_portfolio(self):
        """Print current portfolio status"""
        from lib.utils.display import print_portfolio
        print_portfolio(self.portfolio.dict()) 

    def print_transactions(self, exchange: str, symbol: str):
        """Print transaction history for a specific symbol"""
        from lib.utils.display import print_transactions
        print_transactions(self.portfolio.dict(), exchange, symbol) 