
from typing import Callable, Dict, List, Optional
import uuid

from src.simTime import SimTime

class ContractAction:
    OPEN = 'OPEN'
    CLOSE = 'CLOSE'

class ContractStatus:
    INIT = 'INIT'
    OPEN = 'OPEN'
    CLOSE = 'CLOSE'

class ContractDirection:
    LONG = 'LONG'
    SHORT = 'SHORT'

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
        
    
    def __hash__(self) -> int:
        return hash((self.action, self.ts, self.price, self.num))
    
    def as_dict(self) -> dict:
        return {
            "action": self.action,
            "ts": self.ts,
            "price": self.price,
            "num": self.num,
        }

class Contract:
    # FIXME: Need to enhance support for margin.
    def __init__(self, 
                instId: str, 
                start: int, 
                end: int, 
                direction: str, 
                size: float,
                leverage: int, 
                
                init_ts: Optional[int] = None,
                init_price: Optional[float] = None,
                init_num: Optional[int] = None,
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
        

        self._exit_ts: float = 0.0
        self._details: List[TradeDetail] = []
        self._margin = 0.0
        
        self._status = ContractStatus.INIT
        
        # init entry
        if None not in [init_ts, init_price, init_num]:
            self.open(init_ts, init_price, init_num) # type: ignore
    
    def open(self, entry_ts: int, entry_price: float, entry_num: int):
        if self.STATUS == ContractStatus.CLOSE:
            raise Exception("Can not call a closed contract.")
        
        if entry_ts <= 0:
            raise ValueError("Entry timestamp must be greater than zero.")
        if entry_ts < self._start or entry_ts >= self._end:
            raise ValueError("Entry timestamp must be between start and end timestamps.")
        
        self._details.append(TradeDetail(ContractAction.OPEN, entry_ts, entry_price, entry_num))
        
        if self.STATUS == ContractStatus.INIT:
            self._status = ContractStatus.OPEN
    
    def close(self, close_ts: int, close_price: float, close_num: int):
        if self.STATUS == ContractStatus.INIT:
            raise Exception('Can not call close() for a init contract.')
        if self.STATUS == ContractStatus.CLOSE:
            raise Exception("Can not call a closed contract.")
        
        if close_ts <= 0:
            raise ValueError("Close timestamp must be greater than zero.")
        if close_ts < self._start or close_ts > self._end:
            raise ValueError("Close timestamp must be between start and end timestamps.")
        if close_price <= 0:
            raise ValueError("Close price must be greater than zero.")
        
        close_num = int(close_num)
        if close_num <= 0:
            raise ValueError("Close number must be greater than zero.")
        if self.num - close_num < 0:
            raise ValueError(f"close_num {close_num} can not be greater than num {self.num}")
        self._details.append(TradeDetail(ContractAction.CLOSE, close_ts, close_price, close_num))

        if self.STATUS == ContractStatus.OPEN and self.num == 0:
            self._status = ContractStatus.CLOSE
        
    @property
    def num(self) -> int:
        return sum([e.num if e.action == ContractAction.OPEN else -1*e.num for e in self._details])
    
    # Average Open Price
    @property
    def AOP(self) -> float:
        open_details = [e for e in self._details if e.action == ContractAction.OPEN]
        return sum([d.price*d.num for d in open_details])/sum([d.num for d in open_details])
    
    # Average Close Price
    @property
    def ACP(self) -> float:
        if self.STATUS != ContractStatus.CLOSE:
            raise Exception("Only closed contracts have ACP.")
        close_details = [e for e in self._details if e.action == ContractAction.CLOSE]
        return sum([d.price*d.num for d in close_details])/sum([d.num for d in close_details])
    
    @property
    def STATUS(self) -> str:
        return self._status
    
    @property
    def direction(self) -> str:
        return self._direction.upper()
    
    @property
    def leverage(self) -> int:
        return self._leverage
    
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
            if other.instId == self.instId and \
               other._direction == self._direction and \
               other._leverage == self._leverage:
                return True
        
        return False
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __iadd__(self, other):
        if not isinstance(other, Contract):
            raise TypeError("__iadd__ method should receive param of Contract type")
        if self.STATUS == ContractStatus.CLOSE or other.STATUS == ContractStatus.CLOSE:
            raise Exception("closed contract can not support iadd operation")
        if not self == other:
            raise Exception("Only the same-type contracts support add operation")
        self._margin += other._margin
        self._details.extend(other._details)
        self._details.sort(key=lambda d: d.ts)
        
        if self.STATUS == ContractStatus.INIT:
            self._status = ContractStatus.OPEN
    
    def __add__(self, other):
        if not isinstance(other, Contract):
            raise TypeError("__add__ method should receive param of Contract type")
        if self.STATUS == ContractStatus.CLOSE or other.STATUS == ContractStatus.CLOSE:
            raise Exception("closed contract can not support add operation")
        if not self == other:
            raise Exception("Only the same-type contracts support add operation")
        
        new_contract = Contract(
            self.instId,
            self._start,
            self._end,
            self._direction,
            self._size,
            self._leverage,
        )
        new_contract._details = self._details + other._details
        new_contract._details.sort(key=lambda d: d.ts)
        if new_contract.num > 0:
            new_contract._status = ContractStatus.OPEN
        
        return new_contract
    
    def __hash__(self) -> int:
        return hash((self.uuid, tuple(self._details)))
    
    def __len__(self) -> int:
        return self.num

class Contracts:
    def __init__(self, simTime: SimTime) -> None:
        self._contracts: List[Contract] = []    
        if not isinstance(simTime, SimTime):
            raise TypeError("Contracts.__init__ receives SimTime param")
        self.simTime = simTime
    
    def open(self, c: Contract) -> None:
        if c.STATUS == ContractStatus.CLOSE:
            raise Exception("Can not add a closed contract.")
        same_c = list(filter(lambda cont: cont == c, self._contracts))
        if same_c:
            if len(same_c) > 1:
                raise Exception(f'There multiple contracts of the same type')
            else:
                same_c = same_c[0]
            if same_c.STATUS == ContractStatus.CLOSE:
                self._contracts.remove(same_c)
                self._contracts.append(c)
            else:
                same_c += c
        else:
            self._contracts.append(c)
    
    def close(self, instId: str, direct: str, leverage: int, price: float, num: int) -> bool:
        filter_func: Callable[[Contract], bool] = lambda c: c.instId == instId and \
                                                            c.direction == direct and \
                                                            c.leverage == leverage
        target_c = list(filter(filter_func, self._contracts))
        if len(target_c) > 1:
            raise Exception(f"There multiple contracts with the type")
        else:
            tc = target_c[0]
        if tc.num < num:
            return False
        
        tc.close(int(self.simTime), price, num)
        return True
    
    
    def closeBYuuid(self, uuid: uuid.UUID, price: float, num: int) -> None:
        target_c = list(filter(lambda c: c.uuid == uuid, self._contracts))
        if len(target_c) > 1:
            raise Exception(f"There multiple contracts with the same uuid {uuid.hex}")
        else:
            target_c = target_c[0]
        target_c.close(int(self.simTime), price, num)
    
    def __len__(self) -> int:
        return sum([c.num for c in self._contracts])
    
    def __hash__(self) -> int:
        return hash(tuple(self._contracts))
    
    def as_dict(self) -> dict:
        return {
            'simTime': int(self.simTime),
            'contracts': [
                c.as_dict() for c in self._contracts
            ]
        }

