
import bisect
import glob
import os
from typing import Dict, List, Tuple, Union

import pandas as pd
from src.instrument import Instrument
from src.simTime import SimTime


class BookLevel:
    def __init__(self, price: float, amount: float, count: int):
        self._validate_price(price)
        self._validate_amount(amount)
        self._validate_count(count)
        
        self.price = float(price)
        self.amount = float(amount)
        self.count = int(count)
    
    
    def _validate_price(self, price):
        # if not isinstance(price, float):
        #     raise TypeError("Price must be a float.")
        if price <= 0:
            raise ValueError("Price must be greater than zero.")
    
    
    def _validate_amount(self, amount):
        # if not isinstance(amount, float) and not isinstance(amount, int):
        #     raise TypeError(f"Amount must be a float or an integer but get type {type(amount)}.")
        if amount < 0:
            raise ValueError("Amount must be greater than or equal to zero.")
    
    
    def _validate_count(self, count):
        if count < 0:
            raise ValueError("Count must be greater than or equal to zero.")
    
    
    def __eq__(self, __value) -> bool:
        if isinstance(__value, BookLevel):
            return self.price == __value.price
        elif isinstance(__value, float):
            return self.price == __value
        else:
            raise TypeError("Unsupported type for comparison.")
    
    
    def __repr__(self) -> str:
        return f'BookLevel(price={self.price}, amount={self.amount}, count={self.count})'
    
    
    def __lt__(self, __value) -> bool:
        if isinstance(__value, BookLevel):
            return self.price < __value.price
        elif isinstance(__value, float):
            return self.price < __value
        else:
            raise TypeError("Unsupported type for comparison.")
    
    
    def __gt__(self, __value) -> bool:
        if isinstance(__value, BookLevel):
            return self.price > __value.price
        elif isinstance(__value, float):
            return self.price > __value
        else:
            raise TypeError("Unsupported type for comparison.")

    def true_eq(self, other) -> bool:
        return self.price == other.price and self.amount == other.amount and self.count == other.count


class Asks:
    def __init__(self) -> None:
        self._asks: List[BookLevel] = []
    
    
    def set(self, price: float, amount: float, count: int) -> None:
        new_level = BookLevel(price, amount, count)
        if amount == 0: # remove the level
            if new_level in self._asks:
                self._asks.remove(new_level)
        elif new_level in self._asks: # update the level
            self._asks[self._asks.index(new_level)] = new_level
        else: # add the level
            # Insert the level in the correct position (ascending order)
            bisect.insort(self._asks, new_level)


    def __getitem__(self, index: int) -> BookLevel:
        return self._asks[index]
    
    
    def __len__(self) -> int:
        return len(self._asks)
    
    def __eq__(self, other) -> bool:
        if len(self._asks) != len(other):
            return False
        for i, level in enumerate(self._asks):
            if not level.true_eq(other[i]):
                return False
        
        return True
    
    def __iter__(self):
        return iter(self._asks)


class Bids:
    def __init__(self) -> None:
        self._bids: List[BookLevel] = []
    
    
    def set(self, price: float, amount: float, count: int) -> None:
        new_level = BookLevel(price, amount, count)
        if amount == 0: # remove the level
            if new_level in self._bids:
                self._bids.remove(new_level)
        elif new_level in self._bids: # update the level
            self._bids[self._bids.index(new_level)] = new_level
        else: # add the level
            # Insert the level in the correct position (descending order)
            self._bids.reverse()
            bisect.insort_left(self._bids, new_level)
            self._bids.reverse()


    def __getitem__(self, index: int) -> BookLevel:
        return self._bids[index]
    
    
    def __len__(self) -> int:
        return len(self._bids)
    
    
    def __eq__(self, other) -> bool:
        for i, level in enumerate(self._bids):
            if not level.true_eq(other[i]):
                return False
        
        return True


    def __iter__(self):
        return iter(self._bids)

class Book:
    def __init__(self, instId: str, simTime: SimTime, path: str, max_interval: int = 2000) -> None:
        self.instId = instId
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
        # self._update_index()
        # self.chunked_data = pd.read_parquet(self.index_files[self.current_index])

        self.current_ts = -1
        self.chunked_index = 0
        self._asks: Asks = Asks()
        self._bids: Bids = Bids()
        
        self.update()


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
        
        if self._update_index(): # update the chunked data; reset the book
            self.chunked_data = pd.read_parquet(self.index_files[self.current_index])
            
            # ensure the `action` field is correct in the first row
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
            if row['timestamp'] != self.current_ts:
                self.current_ts = row['timestamp']
            self.chunked_index += 1
        
        self.current_ts = int(self.simTime)


    def __set(self, row: pd.Series) -> None:
        if row['side'] == 'ask':
            self._asks.set(row['price'], row['size'], row['numOrders'])
        elif row['side'] == 'bid':
            self._bids.set(row['price'], row['size'], row['numOrders'])
        else:
            raise Exception(f'Invalid side: {row["side"]}')
        
    
    @property
    def asks(self) -> Asks:
        self.update()
        
        return self._asks
    
    @property
    def bids(self) -> Bids:
        self.update()
        
        return self._bids


    def __getitem__(self, side: str) -> Union[Asks, Bids]:
        if side == 'ask':
            return self.asks
        elif side == 'bid':
            return self.bids
        else:
            raise Exception(f'Invalid side: {side}')


class Books:
    def __init__(self, path: str, simTime: SimTime, max_interval: int = 2000) -> None:
        self.path = path
        self.simTime = simTime
        self.max_interval = max_interval
        
        self._books: Dict[str, Book] = {}
    
    
    def __len__(self) -> int:
        return len(self._books)
    
    
    def __getitem__(self, instId: str) -> Book:
        # TODO: Use Instrument as key instead of instId
        if not isinstance(instId, str) or not isinstance(instId, Instrument):
            raise TypeError("instId must be a string.")
        instId = str(instId)
        if instId not in self._books:
            book_path = os.path.join(self.path, instId)
            self._books[instId] = Book(instId, self.simTime, book_path, self.max_interval)
        
        return self._books[instId]
    