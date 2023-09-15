from distutils import dir_util
import os
from pathlib import Path
import sys

import pytest
from src.instrument import Instrument, InstrumentType, Pair
from src.order import Order, orderAction, orderSide, orderStatus, orderType

sys.path.insert(0, sys.path[0]+"/../")
from src.simTime import SimTime
from src.exchanges import Exchange


@pytest.fixture
def datadir(tmp_path, request) -> Path:
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmp_path))
    return tmp_path

@pytest.fixture
def simTime() -> SimTime:
    return SimTime(1687423745407, 1687506650903)

@pytest.fixture
def exch(datadir: Path, simTime) -> Exchange:
    return Exchange(
        str(datadir), simTime,
        initial_balance= {
            'USDT': 200
        }
        )


class TestExchange:
    
    def test_case1(self, exch: Exchange, simTime: SimTime) -> None:
        eval_step = 1000
        
        inst = Instrument(
            Pair('BTC','USDT'),
            'BTC-USDT-230721',
            InstrumentType.FUTURES,
            1689064733703, 
            1689926400000,
            0.01,
            0.1,
        )
        order = Order(
            inst,
            orderType.MARKET,
            orderSide.LONG,
            simTime,
            2,
            leverage=10,
            action=orderAction.OPEN
        )
        
        assert order.status == orderStatus.OPEN
        
        exch.add_order(order)
        exch.eval()
        
        # open long(buy)
        # best ask should be (price=30571.1, amount=17)
        # 30571.1*0.01*2 = 611.422
        # fee = 0.305711
        # margin = 611.422 / 10 = 61.1422
        # total_cost = 61.447911000000005
        # borrow = 611.422 * (1 - 1/10) = 550.2798
        assert exch.balance['USDT'] == 138.552089
        assert exch.borrow['USDT'] == 550.2798
        assert len(exch.contracts) == 2
        assert order.status == orderStatus.CLOSED
        
        simTime.add(3*eval_step)
        order = Order(
            inst, 
            orderType.MARKET,
            orderSide.LONG,
            simTime,
            1,
            leverage=10,
            action=orderAction.CLOSE
        )
        exch.add_order(order)
        exch.eval()
        
        # close long(sell)
        # best bid should be (price=30567.9, amount=13.0)
        # 30567.9*0.01*1 = 305.679
        # fee = 0.1528395
        # repay = 305.679
        assert exch.balance['USDT'] == 138.552089
        assert exch.borrow['USDT'] == 244.6008
        assert len(exch.contracts) == 1
        assert order.status == orderStatus.CLOSED
        
        simTime.add(240*eval_step)
        order = Order(
            inst,
            orderType.MARKET,
            orderSide.LONG,
            simTime,
            1,
            leverage=10,
            action=orderAction.CLOSE
        )
        exch.add_order(order)
        exch.eval()

        # close long(sell)
        # best bid should be (price=30574.0, amount=17.0)
        # 30574.0*0.01*1 = 305.74
        # fee = 0.15287
        # repay = 244.6008
        # get_ccy = 61.1392
        assert exch.balance['USDT'] == 199.691289
        assert exch.borrow['USDT'] == 0
        assert len(exch.contracts) == 0
        assert order.status == orderStatus.CLOSED
        
        simTime.add(120*eval_step)
        order = Order(
            inst,
            orderType.MARKET,
            orderSide.SHORT,
            simTime,
            3,
            leverage=10,
            action = orderAction.OPEN
        )
        exch.add_order(order)
        exch.eval()

        # open short(sell)
        # best bid should be (price=30580.8, amount=7.0)
        # 30580.8*0.01*3 = 917.424
        # fee = 0.458712
        # margin = 917.424 / 10 = 91.7424
        # total_cost = 92.201112
        # borrow = 917.424 * (1 - 1/10) = 825.6816
        assert exch.balance['USDT'] == 107.49017700000002
        assert exch.borrow['USDT'] == 825.6816
        assert len(exch.contracts) == 3
        assert order.status == orderStatus.CLOSED
        
        simTime.add(600*eval_step)
        order = Order(
            inst,
            orderType.MARKET,
            orderSide.SHORT,
            simTime,
            1,
            leverage=10,
            action=orderAction.CLOSE
        )
        exch.add_order(order)
        exch.eval()

        # close short(buy)
        # best ask should be (price=30550.5, amount=7.0)
        # 30550.5*0.01*1 = 305.505
        # fee = 0.1527525
        # repay = 305.505
        # get_ccy = 0
        assert exch.balance['USDT'] == 107.49017700000002
        assert exch.borrow['USDT'] == 520.1766
        assert len(exch.contracts) == 2
        assert order.status == orderStatus.CLOSED

        simTime.add(1440*eval_step)
        order = Order(
            inst,
            orderType.MARKET,
            orderSide.SHORT,
            simTime,
            1,
            leverage=10,
            action=orderAction.CLOSE
        )
        exch.add_order(order)
        exch.eval()

        # best ask should be (price=30489.3, amount=7.0)
        # 30489.3*0.01*1 = 304.893
        # fee = 0.15244649999999998
        # repay = 304.893
        # get_ccy = 0
        assert exch.balance['USDT'] == 107.49017700000002
        assert exch.borrow['USDT'] == 215.28360000000004
        assert len(exch.contracts) == 1
        assert order.status == orderStatus.CLOSED

        simTime.add(240*eval_step)
        order = Order(
            inst,
            orderType.MARKET,
            orderSide.SHORT,
            simTime,
            1,
            leverage=10,
            action=orderAction.CLOSE
        )
        exch.add_order(order)
        exch.eval()

        # best ask should be (price=30432.3, amount=7.0)
        # 30432.3*0.01*1 = 304.323
        # fee = 0.1521615
        # repay = 215.28360000000004
        # get_ccy = 89.03939999999994
        assert exch.balance['USDT'] == 196.52957699999996
        assert exch.borrow['USDT'] == 215.28360000000004
        assert len(exch.contracts) == 0
        assert order.status == orderStatus.CLOSED

        
        raise NotImplementedError
