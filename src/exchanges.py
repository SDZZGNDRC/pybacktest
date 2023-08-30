
from typing import Dict, List
from src.marketdata import MarketData
from src.order import Order
from src.simTime import SimTime

class Balance:
    def __init__(self, initial_balance: Dict[str, float]) -> None:
        self._balance: Dict[str, float] = {}
        for ccy, value in initial_balance.items():
            self[ccy] = value
    
    
    def __getitem__(self, ccy: str) -> float:
        if not isinstance(ccy, str):
            raise TypeError("Currency must be a string.")
        
        if ccy not in self._balance:
            self._balance[ccy] = 0
        return self._balance[ccy]
    
    
    def __setitem__(self, ccy: str, value: float) -> None:
        if not isinstance(ccy, str):
            raise TypeError("Currency must be a string.")
        
        if value < 0:
            raise ValueError("Balance must be greater than or equal to zero.")
        
        self._balance[ccy] = float(value)
    
    def __contains__(self, ccy: str) -> bool:
        return ccy in self._balance

    def __hash__(self) -> int:
        return hash(tuple(self._balance.items()))

    def as_dict(self) -> dict:
        return self._balance.copy()


class Exchange:
    def __init__(self, data_path: str, simTime: SimTime, initial_balance: Dict[str, float] = {'USDT': 100, 'USDC': 100}) -> None:
        self.marketData = MarketData(simTime, data_path)
        self.orders: List[Order] = []
        self.balance: Balance = Balance(initial_balance)
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
    
    
    def add_order(self, order: Order) -> None:
        if order.status != 'OPEN':
            raise Exception(f'Order status must be OPEN, not {order.status}')
        
        self.orders.append(order)
    
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
            for bl in self.marketData['books'][order.pair]['ask']:
                if order.leftAmount == 0:
                    break
                
                exec_amount = min(order.leftAmount, bl.amount)
                cost = bl.price * exec_amount
                if cost > self.balance[order.quote_ccy]:
                    order.insufficient()
                    print(f'[{self.marketData.simTime}] Insufficient balance: {self.balance[order.quote_ccy]} < {cost}')
                    break
                
                self.balance[order.quote_ccy] -= cost
                self.balance[order.base_ccy] += exec_amount * (1 - fee_rate)
                order.exe(bl.price, exec_amount, exec_amount * fee_rate)
        elif order.side == 'SELL':
            for bl in self.marketData['books'][order.pair]['bid']:
                if order.leftAmount == 0:
                    break
                exec_amount = min(order.leftAmount, bl.amount)
                if exec_amount > self.balance[order.base_ccy]:
                    order.insufficient()
                    print(f'[{self.marketData.simTime}] Insufficient balance: {self.balance[order.base_ccy]} < {exec_amount}')
                    break
                
                self.balance[order.base_ccy] -= exec_amount
                get_amount = exec_amount * bl.price
                print(f'get_amount: {get_amount}')
                self.balance[order.quote_ccy] += get_amount * (1 - fee_rate)
                print(f'balance: {self.balance[order.quote_ccy]}')
                order.exe(bl.price, exec_amount, get_amount * fee_rate)
        else:
            raise Exception(f'Unsupported order side: {order.side}')
        

    def __hash__(self) -> int:
        return hash((tuple(self.orders), self.balance))
    
    def as_dict(self) -> dict:
        return {
            'orders': [o.as_dict() for o in self.orders],
            'balance': self.balance.as_dict(),
        }
