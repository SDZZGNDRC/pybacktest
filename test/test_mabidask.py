from pathlib import Path
import sys
sys.path.insert(0, sys.path[0]+"/../")

import pandas as pd

from src.simTime import SimTime
import pytest

from src.mabidask import mabidask
from src.books import Book

class TestMabidask:
    def test_case1(self):
        simTime = SimTime(0, 62000)
        _mabidask = mabidask('TEST-USDT', simTime, Path(r'D:\Project\pybacktest\test\test_exchanges\books\TEST-USDT'), window=1, max_interval=2000)
        
        # 0
        assert _mabidask.now == 1000.0
        
        # 1000
        simTime.set(1000)
        assert _mabidask.now == 1010.0
        
        # 2000
        simTime.set(2000)
        assert _mabidask.now == 1019.9
        
        # 3000
        simTime.set(3000)
        assert _mabidask.now == 1029.6

        # 4000
        simTime.set(4000)
        assert _mabidask.now == 1038.9


    def test_case2(self):
        simTime = SimTime(0, 62000)
        _mabidask = mabidask('TEST-USDT', simTime, Path(r'D:\Project\pybacktest\test\test_exchanges\books\TEST-USDT'), window=2, max_interval=2000)
        
        # 0
        assert _mabidask.now == 1000.0
        
        # 1000
        simTime.set(1000)
        assert _mabidask.now == 1005.0
        
        # 2000
        simTime.set(2000)
        assert _mabidask.now == 1014.95
        
        # 3000
        simTime.set(3000)
        assert _mabidask.now == 1024.75

        # 4000
        simTime.set(4000)
        assert _mabidask.now == 1034.25








