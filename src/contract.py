
from enum import Enum
import uuid
from uuid import UUID
from src.instrument import Instrument


class ContRole(Enum):
    SELLER = 'SELLER'
    BUYER = 'BUYER'
    def __str__(self) -> str:
        return self.value

class ContStatus(Enum):
    OPEN = 'OPEN'
    CLOSE = 'CLOSE'
    def __str__(self) -> str:
        return self.value


class Contract:
    def __init__(self, 
                inst: Instrument, 
                role: ContRole, 
                ) -> None:
        self._uuid = uuid.uuid4()
        self.inst = inst
        
        self.status = ContStatus.OPEN
        self.role = role
        
        
    
    def close(self) -> None:
        self.status = ContStatus.CLOSE
    
    @property
    def uuid(self) -> UUID:
        return self._uuid
    
    
    def as_dict(self) -> dict:
        return {
            'uuid': str(self._uuid),
            'instId': self.inst.as_dict(),
            'role': str(self.role),
            'status': str(self.status),
        }
    
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Contract) and self.inst == other.inst:
                return True
        
        return False
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash((self.uuid, self.status))

