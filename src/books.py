import glob
import os
from pathlib import Path
from typing import Dict, List, Tuple, Union
import pandas as pd

from src.bookcore import *
from src.instrument import Instrument
from src.simTime import SimTime

class Book:
    def __init__(self, instId: str, simTime: SimTime, path: Path, max_interval: int = 2000, check_instId: bool = True) -> None:
        self.simTime = simTime
        self.path = path
        self.max_interval = max_interval
        
        # initialize the index
        self.index_files: List[str] = glob.glob(os.path.join(self.path, 'part-*-*-*.parquet'))
        if len(self.index_files) == 0:
            t = os.path.join(self.path, 'part-*-*-*.parquet')
            raise Exception(f'No index files found at {t}')
        self.index_timePeriods: List[Tuple[int, int]] = []
        for file in self.index_files:
            start, end = os.path.splitext(os.path.basename(file))[0].split('-')[2:]
            self.index_timePeriods.append((int(start), int(end)))
        
        self.current_index = -1
        # self._update_index()
        # self.chunked_data = pd.read_parquet(self.index_files[self.current_index])

        self.current_ts = -1
        self.chunked_index = 0
        self._core = BookCore(instId, check_instId)
        
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
                
                self._core.set(dict(row))
                
                self.chunked_index += 1
        
            self.current_ts = initial_ts
        
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
                time_interval = abs(row['timestamp'] - self.current_ts)
                raise Exception(f'The time interval {time_interval} between two consecutive rows {(self.current_ts, row["timestamp"])} exceeds the maximum interval {self.max_interval}.')
            
            self._core.set(dict(row))
            if row['timestamp'] != self.current_ts:
                self.current_ts = row['timestamp']
            self.chunked_index += 1
        
        self.current_ts = int(self.simTime)



    
    @property
    def asks(self) -> Asks:
        self.update()
        
        return self._core.asks
    
    @property
    def bids(self) -> Bids:
        self.update()
        
        return self._core.bids
    
    @property
    def core(self) -> BookCore:
        self.update()
        
        return deepcopy(self._core)


    def __getitem__(self, side: str) -> Union[Asks, Bids]:
        if side == 'ask':
            return self.asks
        elif side == 'bid':
            return self.bids
        else:
            raise Exception(f'Invalid side: {side}')



class Books:
    def __init__(self, path: Path, simTime: SimTime, max_interval: int = 10000) -> None:
        self.path = path
        self.simTime = simTime
        self.max_interval = max_interval
        
        self._books: Dict[str, Book] = {}
    
    
    def __len__(self) -> int:
        return len(self._books)
    
    
    def __getitem__(self, inst: Instrument) -> Book:
        instId = inst.instId
        if instId not in self._books:
            book_path = self.path/instId
            self._books[instId] = Book(instId, self.simTime, book_path, self.max_interval)
        
        return self._books[instId]
