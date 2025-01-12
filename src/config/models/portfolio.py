from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class Action(Enum):
    BUY = "BUY"
    SELL = "SELL"

class AccountType(Enum):
    REAL = "REAL"
    VIRTUAL = "VIRTUAL"

@dataclass
class OrderDetails:
    order_id: str
    pair: str
    order_type: str
    amount: float
    execution_price: float
    status: str = 'Filled'
    last_filled: datetime = field(default_factory=datetime.now)
    fee: float = 0.0
    subtotal: float = 0.0
    total: float = 0.0

    def __post_init__(self):
        if self.total == 0.0:
            self.total = self.subtotal + self.fee

@dataclass
class Position:
    amount: float = 0.0
    mean_price: float = 0.0
    pending_buy: float = 0.0
    pending_sell: float = 0.0
    estimated_cost_usd: float = 0.0
    estimated_value_usd: float = 0.0
    orders: List[OrderDetails] = field(default_factory=list)

@dataclass
class Account:
    account_id: str
    name: str
    account_type: AccountType
    positions: Dict[str, Position] = field(default_factory=dict)
    
    def dict(self):
        return {
            'account_id': self.account_id,
            'name': self.name,
            'account_type': self.account_type.value,
            'positions': {
                symbol: {
                    'amount': pos.amount,
                    'mean_price': pos.mean_price,
                    'pending_buy': pos.pending_buy,
                    'pending_sell': pos.pending_sell,
                    'estimated_cost_usd': pos.estimated_cost_usd,
                    'estimated_value_usd': pos.estimated_value_usd,
                    'orders': [
                        {
                            'order_id': order.order_id,
                            'pair': order.pair,
                            'order_type': order.order_type,
                            'status': order.status,
                            'last_filled': order.last_filled.isoformat(),
                            'amount': order.amount,
                            'execution_price': order.execution_price,
                            'subtotal': order.subtotal,
                            'fee': order.fee,
                            'total': order.total
                        } for order in pos.orders
                    ]
                } for symbol, pos in self.positions.items()
            }
        }

@dataclass
class Exchange:
    name: str
    accounts: Dict[str, Account] = field(default_factory=dict)
    
    def dict(self):
        return {
            'name': self.name,
            'accounts': {
                account_id: account.dict()
                for account_id, account in self.accounts.items()
            }
        }

@dataclass
class Portfolio:
    exchanges: Dict[str, Exchange] = field(default_factory=dict)
    estimated_prices: Dict[str, float] = field(default_factory=dict)
    display_currency: str = '$'
    currency_rates: Dict[str, float] = field(default_factory=dict)

    def dict(self):
        return {
            'exchanges': {
                exchange_name: exchange.dict()
                for exchange_name, exchange in self.exchanges.items()
            },
            'estimated_prices': self.estimated_prices,
            'display_currency': self.display_currency,
            'currency_rates': self.currency_rates
        }

    @classmethod
    def parse_obj(cls, data: dict) -> 'Portfolio':
        portfolio = cls(
            display_currency=data.get('display_currency', '$'),
            estimated_prices=data.get('estimated_prices', {}),
            currency_rates=data.get('currency_rates', {})
        )
        
        for exchange_name, exchange_data in data.get('exchanges', {}).items():
            exchange = Exchange(name=exchange_name)
            
            for account_id, account_data in exchange_data.get('accounts', {}).items():
                account = Account(
                    account_id=account_data['account_id'],
                    name=account_data['name'],
                    account_type=AccountType(account_data['account_type'])
                )
                
                for symbol, pos_data in account_data.get('positions', {}).items():
                    orders = []
                    for order_data in pos_data.get('orders', []):
                        order = OrderDetails(
                            order_id=order_data['order_id'],
                            pair=order_data['pair'],
                            order_type=order_data['order_type'],
                            status=order_data['status'],
                            last_filled=datetime.fromisoformat(order_data['last_filled']),
                            amount=order_data['amount'],
                            execution_price=order_data['execution_price'],
                            subtotal=order_data['subtotal'],
                            fee=order_data.get('fee', 0.0),
                            total=order_data.get('total', 0.0)
                        )
                        orders.append(order)
                    
                    account.positions[symbol] = Position(
                        amount=pos_data['amount'],
                        mean_price=pos_data['mean_price'],
                        pending_buy=pos_data.get('pending_buy', 0.0),
                        pending_sell=pos_data.get('pending_sell', 0.0),
                        estimated_cost_usd=pos_data['estimated_cost_usd'],
                        estimated_value_usd=pos_data['estimated_value_usd'],
                        orders=orders
                    )
                
                exchange.accounts[account_id] = account
            
            portfolio.exchanges[exchange_name] = exchange
        
        return portfolio