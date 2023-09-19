import os
from pathlib import Path
from typing import Literal, Union
from src.IdxPrice import IdxPrices

from src.books import Books
from src.markprices import MarkPrices
from src.simTime import SimTime

class MarketData:
    def __init__(self, simTime: SimTime, path: Path, max_interval: int = 2000):
        self.simTime = simTime
        self.path = path
        self._books = Books(os.path.join(path, 'books'), simTime, max_interval)
        self._markPrices = MarkPrices(path/'markprices', simTime, max_interval)
        self._idxPxs = IdxPrices(path/'indexprices', simTime, max_interval)
    
    
    def __getitem__(self, data_type: Literal['books', 'markprices', 'indexprices']) -> Union[Books, MarkPrices, IdxPrices]:
        if data_type == 'books':
            return self._books
        elif data_type == 'markprices':
            return self._markPrices
        elif data_type == 'indexprices':
            return self._idxPxs
        else:
            raise Exception(f'Invalid data type: {data_type}')
