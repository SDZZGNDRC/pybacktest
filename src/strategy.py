from typing import List

from environment import Environment
from event import Event

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
        pass