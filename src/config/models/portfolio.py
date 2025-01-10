# src/config/models/portfolio.py
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto

class OrderType(Enum):
    """Enumeration of possible order types"""
    MARKET_BUY = auto()
    MARKET_SELL = auto()
    LIMIT_BUY = auto()
    LIMIT_SELL = auto()

class OrderStatus(Enum):
    """Enumeration of possible order statuses"""
    FILLED = auto()
    CANCELLED = auto()

@dataclass
class OrderDetails:
    """
    Represents the details of a single trade order
    """
    order_id: str
    pair: str
    order_type: OrderType
    status: OrderStatus
    last_filled: datetime
    amount: float
    execution_price: float
    subtotal: float
    fee: Optional[float] = None
    total: float = field(init=False)

    def __post_init__(self):
        """
        Calculate total after initialization
        """
        self.total = self.subtotal + (self.fee or 0)

@dataclass
class Position:
    """
    Represents a trading position for a specific asset
    """
    amount: float = 0.0
    mean_price: float = 0.0
    pending_buy: float = 0.0
    pending_sell: float = 0.0
    cost_eur: float = 0.0
    value_eur: float = 0.0
    orders: List[OrderDetails] = field(default_factory=list)

@dataclass
class Portfolio:
    """
    Represents a complete portfolio with positions and pricing information
    """
    exchange: str = ''
    positions: Dict[str, Position] = field(default_factory=dict)
    estimated_prices: Dict[str, float] = field(default_factory=dict)
    display_currency: str = '$'
    currency_rates: Dict[str, float] = field(default_factory=dict)

class PortfolioType(Enum):
    """
    Enumeration of portfolio types
    """
    LIVE = 'live'
    VIRTUAL = 'virtual'