import sys
sys.path.insert(0, sys.path[0]+"/../")

import pytest
from src.contracts import Contract, ContractAction

@pytest.fixture
def contract():
    return Contract(
        instId='BTCUSD',
        start=1631040000,  # September 8, 2021 00:00:00
        end=1662576000,  # September 8, 2022 00:00:00
        direction='LONG',
        size=1,
        leverage=10,
        margin=1000
    )

def test_contract_creation(contract):
    assert contract.instId == 'BTCUSD'
    assert contract._start == 1631040000
    assert contract._end == 1662576000
    assert contract._direction == 'LONG'
    assert contract._size == 1
    assert contract._leverage == 10
    assert contract._margin == 1000
    assert contract._exit_ts == 0.0
    assert contract._status == 'OPEN'
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
    assert contract_dict['margin'] == 1000
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
        margin=1000
    )
    contract2 = Contract(
        instId='BTCUSDT',
        start=1631040000,
        end=1662576000,
        direction='SHORT',
        size=1,
        leverage=10,
        margin=1000
    )
    assert contract == contract1
    assert contract != contract2
