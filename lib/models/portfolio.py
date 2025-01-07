from pydantic import BaseModel, RootModel
from datetime import datetime
from typing import Dict, List

class Transaction(BaseModel):
    date: datetime
    action: str
    amount: float
    price: float

class Position(BaseModel):
    amount: float
    mean_price: float
    transactions: List[Transaction] = []

class ExchangePositions(RootModel):
    root: Dict[str, Position]

    def __init__(self, **data):
        super().__init__(root=data.get('root', {}))

class Portfolio(BaseModel):
    positions: Dict[str, Dict[str, Position]] = {}  # key: exchange -> {symbol -> Position}

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 