import sys
from typing import List

sys.path.insert(0, sys.path[0]+"/../")
from src.history import HistLevel
from src.order import Order, orderSide, orderType
from src.environment import Environment
from src.event import Event, CreateEvent
from src.backtest import Backtest
from src.strategy import Strategy
from src.world import World

import pytest

class MyStrategy(Strategy):
    def __init__(self, name: str, pairs: List[str]) -> None:
        super().__init__(name, pairs, [], False)
    
    
    def eval(self, env: Environment) -> List[Event]:
        events: List[Event] = []
        if env.simTime == 1689070299902:
            order = Order(
                '1INCH-USDC',
                orderType.MARKET,
                orderSide.BUY,
                env.simTime, 
                5,
            )
            events.append(CreateEvent(int(env.simTime), 'OKX', order))
        elif env.simTime == 1689070300902:
            order = Order(
                '1INCH-USDC',
                orderType.MARKET,
                orderSide.SELL,
                env.simTime,
                4.5,
            )
            events.append(CreateEvent(int(env.simTime), 'OKX', order))
        elif env.simTime == 1689070302902:
            order = Order(
                '1INCH-USDC',
                orderType.MARKET,
                orderSide.BUY,
                env.simTime,
                10.123,
            )
            events.append(CreateEvent(int(env.simTime), 'OKX', order))
        elif env.simTime == 1689070310902:
            order = Order(
                '1INCH-USDC',
                orderType.MARKET,
                orderSide.SELL,
                env.simTime,
                9.123,
            )
            events.append(CreateEvent(int(env.simTime), 'OKX', order))
        else:
            print(f'[{env.simTime}] No events')
        if len(events) != 0:
            print(f'[{env.simTime}] {events}')
        return events

class TestWorld:
    def test_case1(self):
        world = World(r'E:\out3')
        
        strategy = MyStrategy('test', ['1INCH-USDC'])
        backtest = Backtest(
            strategy,
            1689070299902,
            1689070343902,
            HistLevel.DEBUG,
            ['OKX'],
        )
        
        history = world.run(backtest)
        history.save('./out/test_world_case1.json')

if __name__ == "__main__":
    pytest.main()
    