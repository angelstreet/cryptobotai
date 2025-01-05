from decimal import Decimal
from typing import Dict, List
import pandas as pd
from datetime import datetime

class TradingSimulator:
    def __init__(self, 
                 initial_balance: Decimal = Decimal('10000'),  # USDC
                 trading_fee: Decimal = Decimal('0.001')):     # 0.1%
        self.balance = initial_balance
        self.positions = {}
        self.trading_fee = trading_fee
        self.trade_history = []
        
    async def execute_trade(self, 
                          symbol: str, 
                          side: str, 
                          amount: Decimal, 
                          price: Decimal) -> Dict:
        fee = amount * price * self.trading_fee
        total = amount * price + fee
        
        if side == 'buy':
            if total > self.balance:
                return {'success': False, 'error': 'Insufficient funds'}
            self.balance -= total
            self.positions[symbol] = self.positions.get(symbol, 0) + amount
        else:  # sell
            if amount > self.positions.get(symbol, 0):
                return {'success': False, 'error': 'Insufficient position'}
            self.balance += total
            self.positions[symbol] -= amount
            
        self.trade_history.append({
            'timestamp': datetime.now(),
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'price': price,
            'fee': fee
        })
        
        return {'success': True, 'balance': self.balance, 'positions': self.positions} 