from enum import Enum
from typing import List, Optional
import uuid

from .simTime import SimTime
from .instrument import Instrument

class orderType(Enum):
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    def __str__(self) -> str:
        return self.value

class orderStatus(Enum):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    CANCELED = 'CANCELED'
    INSUFFICIENT = 'INSUFFICIENT'
    def __str__(self) -> str:
        return self.value

class orderSide(Enum):
    BUYLONG = 'BUYLONG'
    SELLSHORT = 'SELLSHORT'
    def __str__(self) -> str:
        return self.value

class orderAction(Enum):
    OPEN = 'OPEN'
    CLOSE = 'CLOSE'
    def __str__(self) -> str:
        return self.value

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
                inst: Instrument, ordType: orderType,
                side: orderSide, simTime: SimTime,
                price: float = 0.0, amount: float = 0.0,
                leverage: int = 1, action: Optional[orderAction] = None
                ) -> None:
        self.uuid = uuid.uuid4()
        if not isinstance(inst, Instrument):
            raise TypeError(f"arg `inst` should have type `Instrument`, but have type {type(inst)}")
        if not isinstance(ordType, orderType):
            raise TypeError(f"arg `orderType` should have type `orderType`, but have type {type(orderType)}")
        if not isinstance(side, orderSide):
            raise TypeError(f"arg `side` should have type `orderSide`, but have type {type(side)}")
        if not isinstance(simTime, SimTime):
            raise TypeError(f"arg `simTime` should have type `SimTime`, but have type {type(simTime)}")
        # 允许可以转换为float的类型
        try:
            price = float(price)
        except (TypeError, ValueError):
            raise TypeError(f"arg `price` should be convertible to `float`, but have type {type(price)}")
        
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise TypeError(f"arg `amount` should be convertible to `float`, but have type {type(amount)}")
        if not isinstance(leverage, int):
            raise TypeError(f"arg `leverage` should have type `int`, but have type {type(leverage)}")
        if action is not None and not isinstance(action, orderAction):
            raise TypeError(f"arg `action` should have type `Optional[orderAction]`, but have type {type(action)}")
        self.inst = inst
        self.orderType = ordType
        self.side = side
        self.create_ts = int(simTime) # The timestamp when the order is created
        self.simTime = simTime # The simulation time
        self.price = price
        self.leverage = leverage # Only for futures|swap
        self.action = action # OPEN|CLOSE; Only for futures|swap
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
        return self.inst.base_ccy
    
    @property
    def quote_ccy(self) -> str:
        return self.inst.quote_ccy
    
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

    def __str__(self) -> str:
        return f'Order({self.uuid}, {self.inst}, {self.orderType}, {self.side}, {self.price}, {self.amount}, {self.leverage}, {self.action}, {self.status})'

    def as_dict(self) -> dict:
        return {
            'uuid': str(self.uuid),
            'instrument': str(self.inst),
            'orderType': str(self.orderType),
            'side': str(self.side),
            'ts': self.create_ts,
            'simTime': int(self.simTime),
            'price': self.price,
            'amount': self.amount,
            'leverage': self.leverage,
            'action': str(self.action),
            'status': str(self.status),
            'detail': [d.as_dict() for d in self.detail],
        }
