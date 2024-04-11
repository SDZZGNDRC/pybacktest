import sys

sys.path.insert(0, sys.path[0]+"/../")
import pytest
from src.order import Order, orderType, orderSide, orderStatus
from src.instrument import Instrument, InstType, Pair
from src.simTime import SimTime

def test_order_init():
    simTime = SimTime(0, 100)
    pair = Pair('BTC', 'USDT')
    instrument = Instrument(pair, 'USDT', InstType.SPOT)
    order_type = orderType.LIMIT
    side = orderSide.BUYLONG
    price = 10000.0
    amount = 1.0
    order = Order(instrument, order_type, side, simTime, price, amount)

    assert order.inst == instrument
    assert order.orderType == order_type
    assert order.side == side
    assert int(order.simTime) == 0
    assert order.price == price
    assert order.amount == amount
    assert order.status == orderStatus.OPEN
    assert len(order.detail) == 0

def test_order_ATP_exception():
    simTime = SimTime(0, 100)
    pair = Pair('BTC', 'USDT')
    instrument = Instrument(pair, 'USDT', InstType.SPOT)
    order_type = orderType.LIMIT
    side = orderSide.BUYLONG
    price = 10000.0
    amount = 1.0
    order = Order(instrument, order_type, side, simTime, price, amount)

    with pytest.raises(Exception):
        order.ATP

def test_order_fee_exception():
    simTime = SimTime(0, 100)
    pair = Pair('BTC', 'USDT')
    instrument = Instrument(pair, 'USDT', InstType.SPOT)
    order_type = orderType.LIMIT
    side = orderSide.BUYLONG
    price = 10000.0
    amount = 1.0
    order = Order(instrument, order_type, side, simTime, price, amount)

    with pytest.raises(Exception):
        order.fee

def test_order_exe():
    simTime = SimTime(0, 100)
    pair = Pair('BTC', 'USDT')
    instrument = Instrument(pair, 'USDT', InstType.SPOT)
    order_type = orderType.LIMIT
    side = orderSide.BUYLONG
    price = 10000.0
    amount = 1.0
    order = Order(instrument, order_type, side, simTime, price, amount)

    order.exe(10000.0, 0.5, 0.001)
    assert len(order.detail) == 1
    assert order.leftAmount == 0.5
    assert order.status == orderStatus.OPEN

    order.exe(10000.0, 0.5, 0.001)
    assert len(order.detail) == 2
    assert order.leftAmount == 0.0
    assert order.status == orderStatus.CLOSED

def test_order_exe_exception():
    simTime = SimTime(0, 100)
    pair = Pair('BTC', 'USDT')
    instrument = Instrument(pair, 'USDT', InstType.SPOT)
    order_type = orderType.LIMIT
    side = orderSide.BUYLONG
    price = 10000.0
    amount = 1.0
    order = Order(instrument, order_type, side, simTime, price, amount)

    with pytest.raises(Exception):
        order.exe(10000.0, 1.1, 0.001)

def test_order_ATP_fee_after_close():
    simTime = SimTime(0, 100)
    pair = Pair('BTC', 'USDT')
    instrument = Instrument(pair, 'USDT', InstType.SPOT)
    order_type = orderType.LIMIT
    side = orderSide.BUYLONG
    price = 10000.0
    amount = 1.0
    order = Order(instrument, order_type, side, simTime, price, amount)

    order.exe(10000.0, 0.5, 0.001)
    order.exe(10000.0, 0.5, 0.001)
    assert order.ATP == 10000.0
    assert order.fee == 0.002