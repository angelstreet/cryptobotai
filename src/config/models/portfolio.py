from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional, Literal

class OrderDetails(BaseModel):
    order_id: str
    pair: str
    order_type: Literal['Market Buy', 'Market Sell', 'Limit Buy', 'Limit Sell']
    status: Literal['Filled', 'Cancelled']
    last_filled: datetime
    amount: float
    execution_price: float
    subtotal: float
    fee: Optional[float] = None
    total: float

class Position(BaseModel):
    amount: float
    mean_price: float
    pending_buy: float = 0.0
    pending_sell: float = 0.0
    cost_eur: float
    value_eur: float
    orders: List[OrderDetails] = []

class Portfolio(BaseModel):
    exchange: str
    positions: Dict[str, Position] = {}
    estimated_prices: Dict[str, float] = {}
    display_currency: str = '$'  # Default to USD
    currency_rates: Dict[str, float] = {}  # Exchange rates for currency conversion
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 