
import glob
import os
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from src.instrument import Instrument
from src.simTime import SimTime


class MarkPrice:
    def __init__(self, inst: Instrument, simTime: SimTime, path: Path, max_interval: int = 2000) -> None:
        self.inst = inst
        self.simTime = simTime
        self.path = path
        self.max_interval = max_interval
        
        # initialize the index
        self.index_files: List[str] = glob.glob(os.path.join(self.path, 'part-*-*-*.parquet'))
        if len(self.index_files) == 0:
            raise Exception('No index files found.')
        self.index_timePeriods: List[Tuple[int, int]] = []
        for file in self.index_files:
            start, end = os.path.splitext(os.path.basename(file))[0].split('-')[2:]
            self.index_timePeriods.append((int(start), int(end)))
        
        self.current_index = -1
        
        
        self.current_ts = -1
        self.chunked_index = 0
        self._markPx: float = 0.0
        
        self.update()
        
        temp_row = self.chunked_data.iloc[0]
        self._instType = temp_row['instType']
        self._instId = temp_row['instId']


    def _update_index(self) -> bool:
        for i, (start, end) in enumerate(self.index_timePeriods):
            if self.simTime >= start and self.simTime <= end:
                if self.current_index != i:
                    self.current_index = i
                    return True
        
        if self.current_index == -1:
            raise Exception(f'Can not find a chunk files for the simTime {int(self.simTime)}')
        
        return False


    def update(self):
        if self.current_ts == self.simTime:
            return
        
        if self._update_index():
            self.chunked_data = pd.read_parquet(self.index_files[self.current_index])

        if self.simTime < self.current_ts:
            raise Exception('Current chunked data is ahead of the simulation time.')
        
        # Find the row with a timestamp that is not greater than and closest to simTime
        index = self.chunked_data['timestamp'].searchsorted(int(self.simTime), side='right')
        if index == 0:
            raise Exception(f'Current chunked data has no data point with a timestamp smaller than current simTime {int(self.simTime)}')
        closest_row = self.chunked_data.iloc[index - 1]
        
        if self.simTime - closest_row['timestamp'] > self.max_interval:
            raise Exception(f'The time interval between two consecutive rows {(closest_row["timestamp"], int(self.simTime))} exceeds the maximum interval.')
        
        self.__set(closest_row)
        self.current_ts = int(self.simTime)


    def __set(self, row: pd.Series) -> None:
        if pd.notnull(row['markPx']):
            self._markPx = float(row['markPx'])
        else:
            ts = row['timestamp']
            raise Exception(f'the markPx is null at ts {ts}')


    @property
    def now(self) -> float:
        self.update()
        return self._markPx


    @property
    def instType(self) -> str:
        return self._instType


    @property
    def instId(self) -> str:
        return self._instId


    def __add__(self, other) -> float:
        self.update()
        return self._markPx + float(other)


    def __sub__(self, other) -> float:
        self.update()
        return self._markPx - float(other)


    def __rsub__(self, other) -> float:
        self.update()
        return float(other) - self._markPx


    def __mul__(self, other) -> float:
        self.update()
        return self._markPx * float(other)


    def __rmul__(self, other) -> float:
        self.update()
        return float(other) / self._markPx


    def __truediv__(self, other) -> float:
        self.update()
        return self._markPx / float(other)


    def __rtruediv__(self, other) -> float:
        self.update()
        return float(other) / self._markPx


    def __float__(self) -> float:
        self.update()
        return float(self._markPx)


    def __str__(self) -> str:
        self.update()
        return str(self._markPx)


    def __lt__(self, other) -> bool:
        self.update()
        return self._markPx < float(other)


    def __le__(self, other) -> bool:
        self.update()
        return self._markPx <= float(other)


    def __eq__(self, other) -> bool:
        self.update()
        return self._markPx == float(other)


    def __ne__(self, other) -> bool:
        return self.__eq__(other)


    def __ge__(self, other) -> bool:
        self.update()
        return self._markPx >= float(other)



class MarkPrices:
    def __init__(self, path: Path, simTime: SimTime, max_interval: int = 10000) -> None:
        self._path = path
        self._simTime = simTime
        self._max_interval = max_interval
        
        self._markPrices: Dict[str, MarkPrice] = {}
    
    
    def __getitem__(self, inst: Instrument) -> MarkPrice:
        instId = inst.instId
        if instId not in self._markPrices:
            markPrice_path = self._path / instId
            self._markPrices[instId] = MarkPrice(
                inst, 
                self._simTime, 
                markPrice_path, 
                self._max_interval,
            )
        
        return self._markPrices[instId]
