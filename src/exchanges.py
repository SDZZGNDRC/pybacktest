
from typing import Dict, List
from src.marketdata import MarketData
from src.order import Order
from src.simTime import SimTime

class Balance:
    def __init__(self) -> None:
        self._balance: Dict[str, float] = {}
    
    
    def __getitem__(self, ccy: str) -> float:
        if isinstance(ccy, str):
            raise TypeError("Currency must be a string.")
        
        if ccy not in self._balance:
            self._balance[ccy] = 0
        return self._balance[ccy]
    
    
    def __setitem__(self, ccy: str, value: float) -> None:
        if isinstance(ccy, str):
            raise TypeError("Currency must be a string.")
        
        if value < 0:
            raise ValueError("Balance must be greater than or equal to zero.")
        
        self._balance[ccy] = float(value)
    
    def __contains__(self, ccy: str) -> bool:
        return ccy in self._balance


class Exchange:
    def __init__(self, data_path: str, simTime: SimTime) -> None:
        self.marketData = MarketData(simTime, data_path)
        self.orders: List[Order] = []
        self.balance: Balance = Balance()
        self.transaction_fee = {
            'MarketOrder': {
                'MAKER': 0.0008,
                'TAKER': 0.0010,
            }
        }
    
    
    def eval(self) -> None:
        if len(self.orders) == 0:
            return
        
        for order in self.orders:
            if order.status == 'OPEN':
                self.__execute(order)
    
    
    def __execute(self, order: Order):
        if order.orderType == 'LIMIT':
            self.__execute_limit_order(order)
        elif order.orderType == 'MARKET':
            self.__execute_market_order(order)
        else:
            raise Exception(f'Unsupported order type: {order.orderType}')
    
    
    def __execute_limit_order(self, order: Order):
        raise NotImplementedError()
    
    
    def __execute_market_order(self, order: Order):
        fee_rate = self.transaction_fee['MarketOrder']['TAKER']
        
        if order.side == 'BUY':
            for bl in self.marketData['books'][order.pair]['asks']:
                if order.leftAmount == 0:
                    break
                
                exec_amount = min(order.leftAmount, bl.amount)
                cost = bl.price * exec_amount
                if cost > self.balance[order.quote_ccy]:
                    order.insufficient()
                    break
                
                self.balance[order.quote_ccy] -= cost
                self.balance[order.base_ccy] += exec_amount * (1 - fee_rate)
                order.exe(bl.price, exec_amount, exec_amount * fee_rate)
        elif order.side == 'SELL':
            for bl in self.marketData['books'][order.pair]['bids']:
                if order.leftAmount == 0:
                    break
                quote_amount = bl.price * bl.amount
                exec_amount = min(order.leftAmount, quote_amount)
                cost = exec_amount / bl.price
                if cost > self.balance[order.base_ccy]:
                    order.insufficient()
                    break
                
                self.balance[order.base_ccy] -= cost
                self.balance[order.quote_ccy] += exec_amount * (1 - fee_rate)
                order.exe(bl.price, exec_amount, exec_amount * fee_rate)
        else:
            raise Exception(f'Unsupported order side: {order.side}')
        
