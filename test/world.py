import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Dict, List

import pandas as pd

sys.path.insert(0, sys.path[0]+"/../")
from src.history import HistLevel
from src.order import Order, orderSide, orderType
from src.environment import Environment
from src.event import Event, CreateEvent
from src.backtest import Backtest
from src.strategy import CustomStrategy, Strategy
from src.world import World

import pytest

def metabacktest(file: Path) -> tuple:
    if not file.is_file():
        raise FileNotFoundError(f"File {file} does not exist.")
    
    with open(file, 'r') as f:
        data = json.load(f)
    
    temp_dir = tempfile.mkdtemp()
    
    df = pd.DataFrame(columns=['instId', 'price', 'size', 'numOrders', 'side', 'timestamp', 'action'])
    instId = list(data['books'].keys())[0]
    start_ts, end_ts = data['bt_period']
    
    slices = list(data['books'].values())[0]['slices']
    len_slices = len(slices)

    for i in range(len_slices):
        ts, asks_bids = list(slices.items())[i]
        timestamp = int(ts)
        if i == 0:
            action = 'snapshot'
        else:
            action = 'update'
        
        for ask in asks_bids['asks']:
            params = ask.split(':')
            price = float(params[0])
            size = float(params[1])
            df.loc[len(df)] = pd.Series({ # type: ignore
                'instId': instId, 
                'price': price, 
                'size': size, 
                'numOrders': 1, 
                'side': 'ask', 
                'timestamp': timestamp, 
                'action': action,
            })
        for bid in asks_bids['bids']:
            params = bid.split(':')
            price = float(params[0])
            size = float(params[1])
            df.loc[len(df)] = pd.Series({ # type: ignore
                'instId': instId, 
                'price': price, 
                'size': size, 
                'numOrders': 1, 
                'side': 'bid', 
                'timestamp': timestamp, 
                'action': action,
            })
    
    path = os.path.join(temp_dir, 'books', instId)
    if not os.path.exists(path):
        os.makedirs(path)
    
    df.to_parquet(os.path.join(path, f'part-0-{start_ts}-{end_ts}.parquet'))

    # strategy
    def eval_func(env: Environment) -> List[Event]:
        insts: List[Dict] = data['insts']
        events = []
        for inst in insts:
            if inst['ts'] == env.simTime:
                event = CreateEvent(int(env.simTime), 'OKX', Order(
                    inst['pair'],
                    orderType.MARKET,
                    inst['side'],
                    env.simTime,
                    inst['value'],
                ))
                events.append(event)
                break
        
        return events

    strategy = CustomStrategy('custom', [instId], eval_func)

    # initial_balance
    initial_balance: Dict[str, float] = {'OKX': data['referredBalance']['0']}

    return temp_dir, strategy, start_ts, end_ts, initial_balance

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
        return events

class TestWorld:
    # def test_case1(self):
    #     world = World(r'E:\out3')
        
    #     strategy = MyStrategy('test', ['1INCH-USDC'])
    #     backtest = Backtest(
    #         strategy,
    #         1689070299902,
    #         1689070343902,
    #         HistLevel.DEBUG,
    #         ['OKX'],
    #     )
        
    #     history = world.run(backtest)
    #     history.save('./out/test_world_case1.json')

    def test_case2(self):
        params = metabacktest(Path(r'D:\Project\metabacktest\testcase.json'))
        
        world = World(params[0], 1000000)
        strategy = params[1]
        backtest = Backtest(
            strategy,
            params[2],
            params[3],
            HistLevel.DEBUG,
            ['OKX'],
            initial_balance=params[4],
        )
        
        history = world.run(backtest)
        history.save('./out/test_world_case2.json')

if __name__ == "__main__":
    pytest.main()
    