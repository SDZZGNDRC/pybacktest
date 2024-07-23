from math import isclose
from distutils import dir_util
import os
from pathlib import Path
import sys
sys.path.insert(0, sys.path[0]+"/../")

import pytest

from src.history import History
from src.instrument import Instrument, InstType, Pair
from src.order import Order, orderAction, orderSide, orderStatus, orderType
from src.positions import PosDirection

from src.simTime import SimTime
from src.exchanges import Exchange

def float_equal(a, b, epsilon=1e-9):
    return abs(a - b) < epsilon

@pytest.fixture
def datadir(tmp_path, request) -> Path:
    filename = request.module.__file__      # the filename of current test file
    test_dir, _ = os.path.splitext(filename)        # remove the extension part

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmp_path))
    return tmp_path

@pytest.fixture
def simTime() -> SimTime:
    return SimTime(1689064733703, 1689521002200)

@pytest.fixture
def exch(datadir: Path, simTime) -> Exchange:
    return Exchange(
        datadir, simTime,
        initial_balance= {
            'USDT': 200
        },
        max_interval=10_000,
        )


# test basic functions
# def test_case1(exch: Exchange, simTime: SimTime) -> None:
#     eval_step = 1000
    
#     inst = Instrument(
#         Pair('BTC','USDT'),
#         'BTC-USDT-230721',
#         InstType.FUTURES,
#         1689064733703, 
#         1689926400000,
#         0.01,
#         0.1,
#     )
#     order = Order(
#         inst,
#         orderType.MARKET,
#         orderSide.BUYLONG,
#         simTime,
#         2,
#         leverage=10,
#         action=orderAction.OPEN
#     )
    
#     assert order.status == orderStatus.OPEN
    
#     exch.add_order(order)
#     exch.eval()
    
#     # open long(buy)
#     # best ask should be (price=30571.1, amount=17)
#     # 30571.1*0.01*2 = 611.422
#     # fee = 0.305711
#     # margin = 611.422 / 10 = 61.1422
#     # total_cost = 61.447911000000005
#     # loan = 611.422 * (1 - 1/10) = 550.2798
#     assert exch.balance['USDT'] == 138.552089
#     assert exch.positions[(inst, PosDirection.BUYLONG, 10)].Loan == 550.2798
#     assert exch.positions[(inst, PosDirection.BUYLONG, 10)].Margin == 61.1422
#     assert exch.positions[(inst, PosDirection.BUYLONG, 10)].OPEN_NUM == 2
#     assert order.status == orderStatus.CLOSED
    
#     simTime.add(3*eval_step)
#     order = Order(
#         inst, 
#         orderType.MARKET,
#         orderSide.BUYLONG,
#         simTime,
#         1,
#         leverage=10,
#         action=orderAction.CLOSE
#     )
#     exch.add_order(order)
#     exch.eval()
    
#     # close long(sell)
#     # best bid should be (price=30567.9, amount=13.0)
#     # (30567.9-30571.1)*0.01*1 = -0.0319999999999709
#     # fee = 0.1528395
#     # repay_margin = 30.5711
#     # get_ccy = 30.5711-0.0319999999999709-0.1528395
#     assert exch.balance['USDT'] == 168.93834950000002
#     assert exch.positions[(inst, PosDirection.BUYLONG, 10)].Loan == 275.1399
#     assert exch.positions[(inst, PosDirection.BUYLONG, 10)].Margin == 30.5711
#     assert exch.positions[(inst, PosDirection.BUYLONG, 10)].OPEN_NUM == 1
#     assert order.status == orderStatus.CLOSED
    
#     simTime.add(240*eval_step)
#     order = Order(
#         inst,
#         orderType.MARKET,
#         orderSide.BUYLONG,
#         simTime,
#         1,
#         leverage=10,
#         action=orderAction.CLOSE
#     )
#     exch.add_order(order)
#     exch.eval()

#     # close long(sell)
#     # best bid should be (price=30574.0, amount=17.0)
#     # (30574.0-30571.1)*0.01*1 = 0.029000000000014552
#     # fee = 0.1528395
#     # repay_margin = 30.5711
#     # get_ccy = 30.5711+0.029000000000014552-0.1528395=30.447260500000016
#     assert isclose(exch.balance['USDT'], 199.38561000000004, rel_tol=1e-5)
#     assert exch.positions[(inst, PosDirection.BUYLONG, 10)].Loan == 0
#     assert exch.positions[(inst, PosDirection.BUYLONG, 10)].Margin == 0
#     assert exch.positions[(inst, PosDirection.BUYLONG, 10)].OPEN_NUM == 0
#     assert order.status == orderStatus.CLOSED
    
#     simTime.add(120*eval_step)
#     order = Order(
#         inst,
#         orderType.MARKET,
#         orderSide.SELLSHORT,
#         simTime,
#         3,
#         leverage=10,
#         action = orderAction.OPEN
#     )
#     exch.add_order(order)
#     exch.eval()

#     # open short(sell)
#     # best bid should be (price=30580.8, amount=7.0)
#     # 30580.8*0.01*3 = 917.424
#     # fee = 0.458712
#     # margin = 917.424 / 10 = 91.7424
#     # total_cost = 92.201112
#     # loan = 917.424 * (1 - 1/10) = 825.6816
#     assert isclose(exch.balance['USDT'], 107.18449800000003, rel_tol=1e-5)
#     assert isclose(exch.positions[(inst, PosDirection.SELLSHORT, 10)].Loan, 825.6816, rel_tol=1e-5)
#     assert exch.positions[(inst, PosDirection.SELLSHORT, 10)].Margin == 91.7424
#     assert exch.positions[(inst, PosDirection.SELLSHORT, 10)].OPEN_NUM == 3
#     assert order.status == orderStatus.CLOSED
    
#     simTime.add(600*eval_step)
#     order = Order(
#         inst,
#         orderType.MARKET,
#         orderSide.SELLSHORT,
#         simTime,
#         1,
#         leverage=10,
#         action=orderAction.CLOSE
#     )
#     exch.add_order(order)
#     exch.eval()

#     # close short(buy)
#     # best ask should be (price=30550.5, amount=7.0)
#     # (30580.8*0.01 - 30550.5*0.01)*1 = 0.30299999999999727
#     # fee = 0.1527525
#     # get_ccy = 30.5808+0.30299999999999727 - 0.1527525 = 30.7310475
#     assert isclose(exch.balance['USDT'], 137.91554550000004, rel_tol=1e-5)
#     assert exch.positions[(inst, PosDirection.SELLSHORT, 10)].Loan == 550.4544
#     assert exch.positions[(inst, PosDirection.SELLSHORT, 10)].Margin == 61.1616
#     assert exch.positions[(inst, PosDirection.SELLSHORT, 10)].OPEN_NUM == 2
#     assert order.status == orderStatus.CLOSED

#     simTime.add(1440*eval_step)
#     order = Order(
#         inst,
#         orderType.MARKET,
#         orderSide.SELLSHORT,
#         simTime,
#         1,
#         leverage=10,
#         action=orderAction.CLOSE
#     )
#     exch.add_order(order)
#     exch.eval()

#     # best ask should be (price=30489.3, amount=7.0)
#     # (30580.8*0.01 - 30489.3*0.01)*1 = 0.9150000000000205
#     # fee = 0.15244649999999998
#     # get_ccy = 30.5808+0.9150000000000205-0.15244649999999998 = 31.34335350000002
#     assert isclose(exch.balance['USDT'], 169.25889900000004, rel_tol=1e-5)
#     assert exch.positions[(inst, PosDirection.SELLSHORT, 10)].Loan == 275.2272
#     assert exch.positions[(inst, PosDirection.SELLSHORT, 10)].Margin == 30.5808
#     assert exch.positions[(inst, PosDirection.SELLSHORT, 10)].OPEN_NUM == 1
#     assert order.status == orderStatus.CLOSED

#     simTime.add(240*eval_step)
#     order = Order(
#         inst,
#         orderType.MARKET,
#         orderSide.SELLSHORT,
#         simTime,
#         1,
#         leverage=10,
#         action=orderAction.CLOSE
#     )
#     exch.add_order(order)
#     exch.eval()

#     # best ask should be (price=30432.3, amount=7.0)
#     # (30580.8*0.01 - 30432.3*0.01)*1 = 1.4850000000000136
#     # fee = 0.1521615
#     # get_ccy = 30.5808+1.4850000000000136-0.1521615 = 31.913638500000012
#     assert isclose(exch.balance['USDT'], 201.17253750000006, rel_tol=1e-5)
#     assert exch.positions[(inst, PosDirection.SELLSHORT, 10)].Loan == 0
#     assert exch.positions[(inst, PosDirection.SELLSHORT, 10)].Margin == 0
#     assert exch.positions[(inst, PosDirection.SELLSHORT, 10)].OPEN_NUM == 0
#     assert order.status == orderStatus.CLOSED

# test liquidation mechanism
# def test_case2(datadir: Path) -> None:
#     eval_step = 1000
#     simTime = SimTime(0, 628000)
#     exch = Exchange(
#         datadir, simTime,
#         initial_balance= {
#             'USDT': 200
#         },
#         max_interval=10_000_000,
#         )
#     inst = Instrument(
#         Pair('TEST','USDT'),
#         'TEST-USDT',
#         InstType.FUTURES,
#         0, # 1689064733703
#         628000,
#         0.1,
#         0.1,
#     )
#     order = Order(      # open at 0
#         inst,
#         orderType.MARKET,
#         orderSide.SELLSHORT,
#         simTime,
#         2,
#         leverage=10,
#         action=orderAction.OPEN
#     )
#     hist = History('DEBUG')
#     hist.snapshot(exch)
#     exch.add_order(order)
#     hist.snapshot(exch)
#     exch.eval()
#     while simTime < 160000:
#         hist.snapshot(exch)
#         simTime.add(eval_step)
#         exch.eval()
    
#     order = Order(      # open at 160000
#         inst,
#         orderType.MARKET,
#         orderSide.BUYLONG,
#         simTime,
#         2,
#         leverage=10,
#         action=orderAction.OPEN
#     )
#     hist.snapshot(exch)
#     exch.add_order(order)
#     hist.snapshot(exch)
#     exch.eval()
    
#     while simTime < 627000:
#         hist.snapshot(exch)
#         simTime.add(1*eval_step)
#         exch.eval()
#     hist.snapshot(exch)
#     hist.save('./out/test_case2.json')

# test spot trading
def test_case3(datadir: Path) -> None:
    eval_step = 1000
    original_USDT = 200000
    simTime = SimTime(0, 999000)
    exch = Exchange(
        datadir, simTime,
        initial_balance= {
            'USDT': original_USDT
        },
        max_interval=10_000,
        )
    inst = Instrument(
        Pair('TRIANGLE', 'USDT'),
        'TRIANGLE-USDT',
        InstType.SPOT,
        0,
        999000,
        0.1,
        0.1,
    )
    # Test begin
    
    # ts: 0 | 901.0:899.0
    order = Order(
        inst,
        orderType.MARKET,
        orderSide.BUYLONG,
        simTime,
        amount=0.1,
        action=orderAction.OPEN
    )
    hist = History('DEBUG')
    hist.snapshot(exch)
    exch.add_order(order)
    hist.snapshot(exch)
    exch.eval()
    hist.snapshot(exch)
    correct_balance_USDT = original_USDT - 901.0 * 0.1
    correct_balance_TRIANGLE = 0.1 * (1 - 0.0010)
    assert exch.balance['USDT'] == correct_balance_USDT
    assert exch.balance['TRIANGLE'] == correct_balance_TRIANGLE
    
    # ts: 177000 | 1088.4:1086.4
    simTime.set(177000)
    hist.snapshot(exch)
    order = Order(
        inst,
        orderType.MARKET,
        orderSide.SELLSHORT,
        simTime,
        amount=0.1 * (1 - 0.0010),
    )
    exch.add_order(order)
    hist.snapshot(exch)
    exch.eval()
    hist.snapshot(exch)
    correct_balance_USDT += 1086.4 * (0.1 * (1 - 0.0010)) * (1 - 0.0010)
    correct_balance_TRIANGLE = 0.0
    assert exch.balance['USDT'] == correct_balance_USDT
    assert exch.balance['TRIANGLE'] == correct_balance_TRIANGLE
    
    # ts: 277000 | 968.3:966.3
    simTime.set(277000)
    hist.snapshot(exch)
    order = Order(
        inst,
        orderType.MARKET,
        orderSide.BUYLONG,
        simTime,
        amount=0.1,
    )
    exch.add_order(order)
    hist.snapshot(exch)
    exch.eval()
    hist.snapshot(exch)
    correct_balance_USDT -= 968.3 * 0.1
    correct_balance_TRIANGLE = 0.1 * (1 - 0.0010)
    assert exch.balance['USDT'] == correct_balance_USDT
    assert exch.balance['TRIANGLE'] == correct_balance_TRIANGLE
    
    # ts: 377000 | 953.9:951.9
    simTime.set(377000)
    hist.snapshot(exch)
    order = Order(
        inst,
        orderType.MARKET,
        orderSide.SELLSHORT,
        simTime,
        amount=0.1 * (1 - 0.0010),
    )
    exch.add_order(order)
    hist.snapshot(exch)
    exch.eval()
    hist.snapshot(exch)
    correct_balance_USDT += 951.9 * (0.1 * (1 - 0.0010)) * (1 - 0.0010)
    correct_balance_TRIANGLE = 0.0
    assert exch.balance['USDT'] == correct_balance_USDT
    assert exch.balance['TRIANGLE'] == correct_balance_TRIANGLE
    
    # ts: 477000 | 1074:1072
    simTime.set(477000)
    hist.snapshot(exch)
    order = Order(
        inst,
        orderType.MARKET,
        orderSide.BUYLONG,
        simTime,
        amount=5,
    )
    exch.add_order(order)
    hist.snapshot(exch)
    exch.eval()
    hist.snapshot(exch)
    correct_balance_USDT -= (1074 + 1075 + 1076 + 1077 + 1078) * 1
    correct_balance_TRIANGLE = 5 * (1 - 0.0010)
    assert exch.balance['USDT'] == correct_balance_USDT
    assert exch.balance['TRIANGLE'] == correct_balance_TRIANGLE
    
    # ts: 677000 | 914.2:912.2
    simTime.set(677000)
    hist.snapshot(exch)
    order = Order(
        inst,
        orderType.MARKET,
        orderSide.SELLSHORT,
        simTime,
        amount=5 * (1 - 0.0010),
    )
    exch.add_order(order)
    hist.snapshot(exch)
    exch.eval()
    hist.snapshot(exch)
    correct_balance_USDT += (912.2 + 911.2 + 910.2 + 909.2 + 908.2) * 1 * (1 - 0.0010) * (1 - 0.0010)
    correct_balance_TRIANGLE = 0.0
    assert float_equal(exch.balance['USDT'], correct_balance_USDT, 1e-2)
    assert exch.balance['TRIANGLE'] == correct_balance_TRIANGLE
    
    # hist.save('./out/test_case3.json')


