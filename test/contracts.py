import sys
sys.path.insert(0, sys.path[0]+"/../")
from typing import Callable

from src.simTime import SimTime

import pytest
from src.contract import Contract, , ContDirection, ContractStatus

@pytest.fixture
def contract():
    return Contract(
        instId='BTCUSD',
        start=1631040000,  # September 8, 2021 00:00:00
        end=1662576000,  # September 8, 2022 00:00:00
        direction='LONG',
        size=1,
        leverage=10,
    )

def test_contract_creation(contract):
    assert contract.instId == 'BTCUSD'
    assert contract._start == 1631040000
    assert contract._end == 1662576000
    assert contract._direction == 'LONG'
    assert contract._size == 1
    assert contract._leverage == 10
    assert contract._exit_ts == 0.0
    assert contract._status == ContractStatus.INIT
    assert contract._details == []

def test_open_trade(contract):
    contract.open(entry_ts=1631040001, entry_price=50000, entry_num=1)
    assert contract.num == 1
    assert contract.AOP == 50000

def test_close_trade(contract):
    contract.open(entry_ts=1631040001, entry_price=50000, entry_num=1)
    contract.close(close_ts=1662575999, close_price=60000, close_num=1)
    assert contract.num == 0
    assert contract.AOP == 50000

def test_invalid_entry_timestamp(contract):
    with pytest.raises(ValueError):
        contract.open(entry_ts=1631039999, entry_price=50000, entry_num=1)

def test_invalid_close_timestamp(contract):
    contract.open(entry_ts=1631040001, entry_price=50000, entry_num=1)
    with pytest.raises(ValueError):
        contract.close(close_ts=1662576001, close_price=60000, close_num=1)

def test_invalid_close_price(contract):
    contract.open(entry_ts=1631040001, entry_price=50000, entry_num=1)
    with pytest.raises(ValueError):
        contract.close(close_ts=1662575999, close_price=-60000, close_num=1)

def test_invalid_close_number(contract):
    contract.open(entry_ts=1631040001, entry_price=50000, entry_num=1)
    with pytest.raises(ValueError):
        contract.close(close_ts=1662575999, close_price=60000, close_num=-1)

def test_as_dict(contract):
    contract.open(entry_ts=1631040001, entry_price=50000, entry_num=1)
    contract_dict = contract.as_dict()
    assert contract_dict['uuid'] == str(contract.uuid)
    assert contract_dict['instId'] == 'BTCUSD'
    assert contract_dict['start'] == 1631040000
    assert contract_dict['end'] == 1662576000
    assert contract_dict['direction'] == 'LONG'
    assert contract_dict['size'] == 1
    assert contract_dict['leverage'] == 10
    assert contract_dict['_exit_ts'] == 0.0
    assert contract_dict['status'] == 'OPEN'
    assert len(contract_dict['entry_details']) == 1
    assert contract_dict['num'] == 1
    assert contract_dict['AOP'] == 50000

def test_contract_equality(contract):
    contract1 = Contract(
        instId='BTCUSD',
        start=1631040000,
        end=1662576000,
        direction='LONG',
        size=1,
        leverage=10,
    )
    contract2 = Contract(
        instId='BTCUSDT',
        start=1631040000,
        end=1662576000,
        direction='SHORT',
        size=1,
        leverage=10,
    )
    assert contract == contract1
    assert contract != contract2

@pytest.fixture
def ctf_1():
    def f():
        c = Contract(
            'BTC-USDT-231229',
            1686903000972,
            1703836800000,
            ContDirection.LONG,
            0.01,
            10,
        )
        return c
    return f

class TestContract:
    
    def test_case1(self, ctf_1: Callable[[],Contract]):
        ct_1 = ctf_1()
        assert ct_1.STATUS == ContractStatus.INIT
        assert ct_1.num == 0
        with pytest.raises(ZeroDivisionError):
            ct_1.AOP
        with pytest.raises(Exception):
            ct_1.close(1686906000972, 20000.123, 1)
        
        ct_1.open(1686905000972, 25000.123, 2)
        
        assert ct_1.STATUS == ContractStatus.OPEN
        assert ct_1.num == 2
        assert ct_1.AOP == 25000.123
        assert ct_1.direction == ContDirection.LONG
        assert ct_1.leverage == 10
        with pytest.raises(ValueError):
            ct_1.close(1686906000972, 20000.123, 3)
        
        
        ct_1.close(1686906000972, 20000.123, 1)
        
        with pytest.raises(Exception):
            ct_1.ACP
        
        ct_1.close(1686907000972, 22000.123, 1)
        
        assert ct_1.STATUS == ContractStatus.CLOSE
        assert ct_1.num == 0
        assert ct_1.AOP == 25000.123
        assert ct_1.ACP == 21000.123
        
        with pytest.raises(Exception):
            ct_1.open(1686906000972, 20000.123, 1)
            ct_1.close(1686906000972, 20000.123, 1)
    
    def test_case2(self, ctf_1: Callable[[], Contract]):
        ct_1 = ctf_1()
        ct_2 = ctf_1()
        
        ct_1.open(1686905000972, 25000.123, 1)
        ct_2.open(1686904000972, 22000.123, 1)
        ct_3 = ct_1 + ct_2
        
        assert ct_3 == ct_1 and ct_3 == ct_2
        assert ct_3.num == ct_1.num + ct_2.num
        assert ct_3.AOP == 23500.123
        assert ct_3.STATUS == ContractStatus.OPEN
        
        ct_3.close(1686907000972, 26000.123, 1)
        ct_3.close(1686908000972, 20000.123, 1)
        
        assert ct_3.STATUS == ContractStatus.CLOSE
        assert ct_3.num == 0
        assert ct_3.AOP == 23500.123
        assert ct_3.ACP == 23000.123
        
        ct_2.close(1686907000972, 26000.123, 1)
        
        with pytest.raises(Exception):
            ct_4 = ct_1 + ct_2
