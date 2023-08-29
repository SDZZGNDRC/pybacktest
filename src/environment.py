
from typing import Dict
from src.exchanges import Exchange
from src.simTime import SimTime


class Environment:
    def __init__(self, path: str, simTime: SimTime) -> None:
        self.simTime = simTime
        self.path = path
        self.exchanges: Dict[str, Exchange] = {}
        self.exchanges['OKX'] = Exchange(path, simTime)
    
    
    def __getitem__(self, _info):
        if _info == 'exchanges':
            return self.exchanges
        else:
            raise KeyError(f'Environment has no attribute {_info}')
    
    
    def __hash__(self) -> int:
        return hash(tuple(self.exchanges.items()))
    
    
    def as_dict(self) -> dict:
        return {
            'simTime': int(self.simTime),
            'exchanges': {k: v.as_dict() for k, v in self.exchanges.items()}
        }
    
    
    def eval(self) -> None:
        for exchange in self.exchanges.values():
            exchange.eval()
