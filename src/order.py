from typing import List, Union
import uuid

from simTime import SimTime
from src.instrument import Instrument

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
    
    
    def as_dict(self) -> dict:
        return {
            'ts': self.ts,
            'price': self.price,
            'amount': self.amount,
            'fee': self.fee,
        }
    
    
    def __hash__(self) -> int:
        return hash((self.ts, self.price, self.amount, self.fee))

class Order:
    def __init__(self,
                instrument: Instrument, orderType: str, 
                side: str, ts: Union[SimTime, int], 
                amount: float, price: float = 0, 
                leverage: int = 1,
                ) -> None:
        self.uuid = uuid.uuid4()
        self.instrument = instrument
        self.orderType = orderType
        self.side = side
        self.ts = int(ts) # The timestamp when the order is created
        self.simTime = ts # The simulation time
        self.price = price
        self.leverage = leverage # Only for futures|swap
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
        return self.instrument.base_ccy
    
    @property
    def quote_ccy(self) -> str:
        return self.instrument.quote_ccy
    
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

    def __hash__(self) -> int:
        return hash((self.status, tuple(self.detail)))

    def as_dict(self) -> dict:
        return {
            'uuid': str(self.uuid),
            'instrument': str(self.instrument),
            'orderType': self.orderType,
            'side': self.side,
            'ts': self.ts,
            'simTime': int(self.simTime),
            'price': self.price,
            'amount': self.amount,
            'status': self.status,
            'detail': [d.as_dict() for d in self.detail],
        }
