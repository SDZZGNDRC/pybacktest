
from typing import Dict
from src.exchanges import Exchange
from src.simTime import SimTime


class Environment:
    def __init__(self, path: str, simTime: SimTime, max_interval: int = 2000, initial_balance: Dict[str, Dict[str, float]] = {'OKX': {'USDT': 1000, 'USDC': 1000}}) -> None:
        self.simTime = simTime
        self.path = path
        self.exchanges: Dict[str, Exchange] = {}
        self.max_interval = max_interval
        if 'OKX' in initial_balance:
            self.exchanges['OKX'] = Exchange(path, simTime, initial_balance=initial_balance['OKX'], max_interval=max_interval)
        else:
            self.exchanges['OKX'] = Exchange(path, simTime, max_interval=max_interval)
    
    
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
