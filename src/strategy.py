from typing import Callable, List

from src.environment import Environment
from src.event import Event

class Strategy:
    def __init__(self, 
                name: str,
                pairs: List[str],
                indicators: List[str],
                stateful: bool = False,
                ) -> None:
        self.name = name
        self.pairs = pairs
        self.indicators = indicators
        self.stateful = stateful
    
    
    def eval(self, env: Environment) -> List[Event]:
        raise NotImplementedError

class CustomStrategy(Strategy):
    def __init__(self, 
                name: str,
                pairs: List[str],
                eval_func: Callable[[Environment], List[Event]],
                ) -> None:
        super().__init__(name, pairs, [], False)
        self.eval_func = eval_func
    
    
    def eval(self, env: Environment) -> List[Event]:
        return self.eval_func(env)
    