from typing import List
import uuid

from simTime import SimTime

class orderType:
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'

class orderStatus:
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    CANCELED = 'CANCELED'
    INSUFFICIENT = 'INSUFFICIENT'

class orderSide:
    BUY = 'BUY'
    SELL = 'SELL'

class TransDetail:
    def __init__(self,
                ts: int, price: float,
                amount: float, fee: float,
                ) -> None:
        self.ts = ts
        self.price = price
        self.amount = amount
        self.fee = fee

class Order:
    def __init__(self,
                pair: str, orderType: str, 
                side: str, ts: SimTime, 
                price: float, amount: float, 
                ) -> None:
        self.uuid = uuid.uuid4()
        self.pair = pair
        self.orderType = orderType
        self.side = side
        self.ts = int(ts) # The timestamp when the order is created
        self.simTime = ts # The simulation time
        self.price = price
        self.amount = amount
        self.status = orderStatus.OPEN
        self.detail: List[TransDetail] = []
    
    @property
    def ATP(self) -> float:
        if self.status != orderStatus.CLOSED:
            raise Exception('Order is not closed')
        return sum([d.amount * d.price for d in self.detail]) / sum([d.amount for d in self.detail])
    
    @property
    def fee(self) -> float:
        if self.status != orderStatus.CLOSED:
            raise Exception('Order is not closed')
        return sum([d.fee for d in self.detail])
    
    @property
    def leftAmount(self) -> float:
        # The amount that has not been executed
        return self.amount - sum([d.amount for d in self.detail])
    
    @property
    def base_ccy(self) -> str:
        s = self.pair.split('-')
        if len(s) != 2:
            raise Exception('Invalid pair')
        return s[0]
    
    @property
    def quote_ccy(self) -> str:
        s = self.pair.split('-')
        if len(s) != 2:
            raise Exception('Invalid pair')
        return s[1]
    
    def exe(self, price: float, amount: float, fee: float) -> None:
        if self.status != orderStatus.OPEN:
            raise Exception('Order is not open')
        if self.leftAmount < amount:
            raise Exception('Amount exceeds the left amount')
        self.detail.append(
            TransDetail(
                ts = int(self.simTime),
                price = price,
                amount = amount,
                fee = fee,
            )
        )
        if self.leftAmount == 0: # TODO: Consider the precision
            self.status = orderStatus.CLOSED
        
    def insufficient(self) -> None:
        self.status = orderStatus.INSUFFICIENT
