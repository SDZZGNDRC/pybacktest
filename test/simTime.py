import sys
sys.path.insert(0, sys.path[0]+"/../")

import pytest
from src.simTime import SimTime

def test_simTime_creation():
    # Test valid creation
    sim = SimTime(0, 10)
    assert int(sim) == 0
    assert float(sim) == 0.0

    # Test invalid start and end times
    with pytest.raises(ValueError):
        SimTime("0", 10) # type: ignore
    with pytest.raises(ValueError):
        SimTime(10, 0)
    with pytest.raises(ValueError):
        SimTime(10, 10)

def test_simTime_set():
    sim = SimTime(0, 10)

    # Test valid set
    sim.set(5)
    assert int(sim) == 5
    assert float(sim) == 5.0

    # Test invalid timestamp
    with pytest.raises(ValueError):
        sim.set("5") # type: ignore
    with pytest.raises(ValueError):
        sim.set(11)

def test_simTime_str():
    sim = SimTime(0, 10)
    assert str(sim) == "0"

    sim.set(5)
    assert str(sim) == "5"

def test_simTime_conversion():
    sim = SimTime(0, 10)
    assert int(sim) == 0
    assert float(sim) == 0.0

    sim.set(5)
    assert int(sim) == 5
    assert float(sim) == 5.0
