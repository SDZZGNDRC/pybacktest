
from collections import deque
import glob
import os
from pathlib import Path
from typing import Deque, Dict, List, Tuple

import pandas as pd
from src.instrument import Instrument
from src.simTime import SimTime
from books import Asks, Bids


class mabidask:
    def __init__(self, instId: str, simTime: SimTime, path: Path, window: int = 1, max_interval: int = 2000) -> None:
        self.instId = instId
        self.simTime = simTime
        self.path = path
        self.window = window
        self._hist: Deque[float] = deque(maxlen=window)
        self.max_interval = max_interval
        
        if window > 1: 
            # ! NOTICE: There is a bug where the `window` parameter is bigger than 1. 
            raise Exception('The window parameter is not supported yet.')
        
        # initialize the index
        self.index_files: List[str] = glob.glob(str(self.path/'part-*-*-*.parquet'))
        if len(self.index_files) == 0:
            raise Exception('No index files found.')
        self.index_timePeriods: List[Tuple[int, int]] = []
        for file in self.index_files:
            start, end = os.path.splitext(os.path.basename(file))[0].split('-')[2:]
            self.index_timePeriods.append((int(start), int(end)))
        
        self.current_index = -1
        # self._update_index()
        # self.chunked_data = pd.read_parquet(self.index_files[self.current_index])

        self.current_ts = -1
        self.chunked_index = 0
        self._asks: Asks = Asks()
        self._bids: Bids = Bids()
        
        self.update()


    def _update_index(self) -> bool:
        for i, (start, end) in enumerate(self.index_timePeriods):
            if start <= self.simTime <= end:
                if self.current_index != i:
                    self.current_index = i
                    return True
        
        if self.current_index == -1:
            raise Exception(f'Can not find a chunk files for the simTime {int(self.simTime)}')
        
        return False


    def update(self):
        if self.current_ts == self.simTime:
            return
        
        if self._update_index(): # update the chunked data; reset the book
            self.chunked_data = pd.read_parquet(self.index_files[self.current_index])
            
            # ensure the `action` field is correct in the first row
            # NOTICE: MUST ensure that each chunked data file have a snapshot at the beginning.
            if self.chunked_data.iloc[0]['action'] != 'snapshot':
                raise Exception('The first row of the chunked data must be a snapshot.')
            
            initial_ts: int = self.chunked_data.iloc[0]['timestamp']
            
            # load snapshot; iterate through each row and update the book
            self.chunked_index = 0
            for _, row in self.chunked_data.iterrows():
                if row['action'] != 'snapshot' or row['timestamp'] != initial_ts: # finish loading the snapshot
                    break
                
                self.__set(row)
                
                self.chunked_index += 1
        
            self.current_ts = initial_ts
            self._hist.append((self._asks[0].price + self._bids[0].price) / 2)
        
        if self.simTime < self.current_ts:
            raise Exception('Current chunked data is ahead of the simulation time.')
        
        # iterate through each row and update the book until the simulation time is reached
        while self.simTime >= self.current_ts:
            if self.chunked_index >= len(self.chunked_data):
                break
            row = self.chunked_data.iloc[self.chunked_index]
            if row['timestamp'] > self.simTime:
                break

            if abs(row['timestamp'] - self.current_ts) > self.max_interval and self.current_ts != -1:
                raise Exception(f'The time interval between two consecutive rows {(row["timestamp"], self.current_ts)} exceeds the maximum interval.')
            
            self.__set(row)
            if row['timestamp'] != self.current_ts and len(self._asks)!=0 and len(self._bids)!=0:
                self.current_ts = row['timestamp']
                self._hist.append((self._asks[0].price + self._bids[0].price) / 2)
            self.chunked_index += 1
        self._hist.append((self._asks[0].price + self._bids[0].price) / 2)
        self.current_ts = int(self.simTime)


    def __set(self, row: pd.Series) -> None:
        if row['side'] == 'ask':
            self._asks.set(row['price'], row['size'], row['numOrders'])
        elif row['side'] == 'bid':
            self._bids.set(row['price'], row['size'], row['numOrders'])
        else:
            raise Exception(f'Invalid side: {row["side"]}')
        

    @property
    def now(self) -> float:
        self.update()

        return sum(self._hist) / len(self._hist)

    def __add__(self, other) -> float:
        return self.now + float(other)
    
    def __sub__(self, other) -> float:
        return self.now - float(other)

    def __rsub__(self, other) -> float:
        return float(other) - self.now
    
    def __mul__(self, other) -> float:
        return self.now * float(other)

    def __rmul__(self, other) -> float:
        return float(other) * self.now

    def __truediv__(self, other) -> float:
        return self.now / float(other)

    def __rtruediv__(self, other) -> float:
        return float(other) / self.now
    
    def __float__(self) -> float:
        return self.now

    def __str__(self) -> str:
        return str(self.now)

    def __lt__(self, other) -> bool:
        return self.now < float(other)

    def __le__(self, other) -> bool:
        return self.now <= float(other)

    def __eq__(self, other) -> bool:
        return self.now == float(other)

    def __ne__(self, other) -> bool:
        return self.now != float(other)

    def __ge__(self, other) -> bool:
        return self.now >= float(other)


class MABidAsks:
    def __init__(self, path: Path, simTime: SimTime, max_interval: int = 10000) -> None:
        self.path = path
        self.simTime = simTime
        self.max_interval = max_interval
        
        self._mabidasks: Dict[str, mabidask] = {}
    
    
    def __len__(self) -> int:
        return len(self._mabidasks)
    
    
    def __getitem__(self, inst: Instrument) -> mabidask:
        instId = inst.instId
        if instId not in self._mabidasks:
            book_path = self.path / instId
            self._mabidasks[instId] = mabidask(instId, self.simTime, book_path, max_interval=self.max_interval)
        
        return self._mabidasks[instId]
