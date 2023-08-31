
from src.simTime import SimTime


class Indicator:
    def __init__(self, name: str, simTime: SimTime) -> None:
        self.name = name
        self.simTime = simTime
        self.current_ts = -1
        self._value: float = 0.0
    
    
    def __str__(self) -> str:
        return str(self.value)
    
    
    def __gt__(self, other) -> bool:
        return self.value > float(other)
    
    
    def __ge__(self, other) -> bool:
        return self.value >= float(other)
    
    
    def __lt__(self, other) -> bool:
        return self.value < float(other)
    
    
    def __le__(self, other) -> bool:
        return self.value <= float(other)
    
    
    def __eq__(self, other) -> bool:
        return self.value == float(other)
    
    
    def __ne__(self, other) -> bool:
        return self.value != float(other)
    
    
    @property
    def value(self) -> float:
        if self.current_ts != self.simTime:
            self.current_ts = int(self.simTime)
            self.eval()
        return self._value
    
    
    def eval(self) -> None:
        raise NotImplementedError