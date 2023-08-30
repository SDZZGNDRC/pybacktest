import sys
from typing import List

sys.path.insert(0, sys.path[0]+"/../")
from src.environment import Environment
from src.event import Event
from src.backtest import Backtest
from src.strategy import Strategy
from src.world import World

import pytest

class TestStrategy(Strategy):
    def __init__(self, name: str, pairs: List[str]) -> None:
        super().__init__(name, pairs, [], False)
    
    
    def eval(self, env: Environment) -> List[Event]:
        
        return []

class TestWorld:
    def test_case1(self):
        world = World(r'E:\out3')
        
        

if __name__ == "__main__":
    pytest.main()
    