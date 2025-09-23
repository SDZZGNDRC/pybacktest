import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Dict, List
import pandas as pd

from pybacktest.instrument import Instrument, Pair, InstType
from pybacktest.history import HistLevel
from pybacktest.order import Order, orderSide, orderType
from pybacktest.environment import Environment
from pybacktest.event import Event, CreateEvent
from pybacktest.backtest import Backtest
from pybacktest.strategy import CustomStrategy, Strategy
from pybacktest.world import World

import pytest

TEST_DIR = Path(os.path.abspath(__file__)).parent

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
                # 创建Instrument对象
                pair_parts = inst['pair'].split('-')
                if len(pair_parts) != 2:
                    raise ValueError(f"Invalid pair format: {inst['pair']}")
                
                instrument = Instrument(
                    Pair(pair_parts[0], pair_parts[1]),
                    inst['pair'],
                    InstType.SPOT,
                    0,  # listTime
                    9999999999999,  # expTime (一个很大的值，表示永不过期)
                    1.0,  # contract_size
                    0.0001  # tick_size
                )
                
                event = CreateEvent(int(env.simTime), 'OKX', Order(
                    instrument,
                    orderType.MARKET,
                    orderSide(inst['side']),
                    env.simTime,
                    inst['value'],
                ))
                events.append(event)
                break
        
        return events

    strategy = CustomStrategy('custom', [instId], eval_func)

    # initial_balance
    initial_balance: Dict[str, float] = {'OKX': data['referredBalance']['0']}

    ref = data['referredBalance']

    return temp_dir, strategy, start_ts, end_ts, initial_balance, ref

class MyStrategy(Strategy):
    def __init__(self, name: str, pairs: List[str]) -> None:
        super().__init__(name, pairs, [], False)
        self.inst = Instrument(Pair('1INCH', 'USDC'), '1INCH-USDC', 'SPOT')
    
    
    def eval(self, env: Environment) -> List[Event]:
        events: List[Event] = []
        if env.simTime == 1689070299902:
            order = Order(
                self.inst,
                orderType.MARKET,
                orderSide.BUYLONG,
                env.simTime, 
                5,
            )
            events.append(CreateEvent(int(env.simTime), 'OKX', order))
        elif env.simTime == 1689070300902:
            order = Order(
                self.inst,
                orderType.MARKET,
                orderSide.SELLSHORT,
                env.simTime,
                4.5,
            )
            events.append(CreateEvent(int(env.simTime), 'OKX', order))
        elif env.simTime == 1689070302902:
            order = Order(
                self.inst,
                orderType.MARKET,
                orderSide.BUYLONG,
                env.simTime,
                10.123,
            )
            events.append(CreateEvent(int(env.simTime), 'OKX', order))
        elif env.simTime == 1689070310902:
            order = Order(
                self.inst,
                orderType.MARKET,
                orderSide.SELLSHORT,
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
        tmp_dir, strategy, start_ts, end_ts, initial_balance, ref = metabacktest(TEST_DIR/Path('./metabacktest/testcase.json'))
        
        world = World(tmp_dir, 1000000)
        backtest = Backtest(
            strategy,
            start_ts,
            end_ts,
            HistLevel.DEBUG,
            ['OKX'],
            initial_balance=initial_balance,
        )
        
        history = world.run(backtest)
        history.save('./out/test_world_case2.json')
        
        # Verify
        assert len(ref) == len(history)
        ref_balances = list(ref.items())
        for i in range(len(ref)):
            for k in ref_balances[i][1].keys():
                assert abs(ref_balances[i][1][k] - history[i]['exchanges']['OKX']['balance'][k])/ref_balances[i][1][k] < 0.000001
        
        shutil.rmtree(tmp_dir)

if __name__ == "__main__":
    pytest.main()
    