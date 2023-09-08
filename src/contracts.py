
from typing import Dict, List
import uuid

class ContractAction:
    OPEN = 'OPEN'
    CLOSE = 'CLOSE'

class TradeDetail:
    def __init__(self,
                action: str,
                ts: int,
                price: float,
                num: int,
                ) -> None:
        self.ts = ts
        
        if action not in ['Open', 'Close', 'OPEN', 'CLOSE']:
            raise ValueError("invalid action.")
        self.action = str(action).upper()
        
        if price <= 0:
            raise ValueError("price must be greater than zero.")
        self.price = price
        if num <= 0:
            raise ValueError("num must be greater than zero.")
        self.num = num
        
    
    def as_dict(self) -> dict:
        return {
            "action": self.action,
            "ts": self.ts,
            "price": self.price,
            "num": self.num,
        }

class Contract:
    
    def __init__(self, 
                instId: str, 
                start: int, 
                end: int, 
                direction: str, 
                size: int,
                leverage: int, 
                margin: float,
                ) -> None:
        self.uuid = uuid.uuid4()
        self.instId = str(instId)

        if start <= 0 or end <= 0:
            raise ValueError("Timestamp must be greater than zero.")
        if start >= end:
            raise ValueError("Start timestamp must be less than end timestamp.")
        self._start = int(start)
        self._end = int(end)
        
        
        self._direction = str(direction)

        if size <= 0:
            raise ValueError("Entry timestamp must be greater than zero.")
        self._size = float(size)
        
        if not isinstance(leverage, int):
            raise TypeError("Leverage must be an integer.")
        if leverage <= 0:
            raise ValueError("Leverage must be greater than zero.")
        self._leverage = leverage
        
        if margin < 0:
            raise ValueError("Margin must be greater than or equal to zero.")
        self._margin = float(margin)

        self._exit_ts: float = 0.0
        self._status = 'OPEN'
        self._details: List[TradeDetail] = []
    
    def open(self, entry_ts: int, entry_price: float, entry_num: int):
        if entry_ts <= 0:
            raise ValueError("Entry timestamp must be greater than zero.")
        if entry_ts < self._start or entry_ts >= self._end:
            raise ValueError("Entry timestamp must be between start and end timestamps.")
        
        self._details.append(TradeDetail(ContractAction.OPEN, entry_ts, entry_price, entry_num))
    
    def close(self, close_ts: int, close_price: float, close_num: int):
        if close_ts <= 0:
            raise ValueError("Close timestamp must be greater than zero.")
        if close_ts < self._start or close_ts > self._end:
            raise ValueError("Close timestamp must be between start and end timestamps.")
        if close_price <= 0:
            raise ValueError("Close price must be greater than zero.")
        
        close_num = int(close_num)
        if close_num <= 0:
            raise ValueError("Close number must be greater than zero.")
        
        self._details.append(TradeDetail(ContractAction.CLOSE, close_ts, close_price, close_num))
        
        
    @property
    def num(self) -> int:
        return sum([e.num if e.action == ContractAction.OPEN else -1*e.num for e in self._details])
    
    # Average Open Price
    @property
    def AOP(self) -> float:
        open_details = [e for e in self._details if e.action == ContractAction.OPEN]
        return sum([d.price*d.num for d in open_details])/sum([d.num for d in open_details])
    
    
    def as_dict(self) -> dict:
        return {
            'uuid': str(self.uuid),
            'instId': self.instId,
            'start': self._start,
            'end': self._end,
            'direction': self._direction,
            'size': self._size,
            'leverage': self._leverage,
            'margin': self._margin,
            '_exit_ts': self._exit_ts,
            'status': self._status,
            'entry_details': self._details,
            
            # property
            'num': self.num,
            'AOP': self.AOP,
        }
    
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Contract):
            if other.instId == self.instId:
                return True
        
        return False
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    

class Contracts:
    def __init__(self) -> None:
        self._contracts: Dict[str, Contract] = {}
    
    
    def __getitem__(self, key: str):
        key = str(key)
        if key in self._contracts:
            return self._contracts[key]
        else:
            raise ValueError(f"key {key} is not in self._contracts.")
    
    
    def __setitem__(self, key: str, contract: Contract):
        if not isinstance(contract, Contract):
            raise TypeError("new item must be Contract Type.")
        key = str(key)
        self._contracts[key] = contract
    
    
    def __len__(self) -> int:
        return len(self._contracts)
