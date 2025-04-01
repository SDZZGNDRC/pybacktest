import bisect
from copy import copy, deepcopy
from typing import List, Union

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
        '''
        Check the price is equal or not
        '''
        if isinstance(__value, BookLevel):
            return self.price == __value.price
        elif isinstance(__value, float):
            return self.price == __value
        elif isinstance(__value, tuple) and len(__value) == 3:
            return (self.price, self.amount, self.count) == __value
        else:
            raise TypeError(f"Unsupported type({type(__value)}) for comparison: value {__value}")
    
    
    
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
    
    def __deepcopy__(self, memo):
        return BookLevel(self.price, self.amount, self.count)

    def __str__(self) -> str:
        return f'(p: {self.price}, a: {self.amount}, c: {self.count})'
    
    def __repr__(self) -> str:
        return self.__str__()

    def true_eq(self, other) -> bool:
        return self.price == other.price and self.amount == other.amount and self.count == other.count


class Asks:
    def __init__(self, max_depth: int = 400) -> None:
        self._asks: List[BookLevel] = []
        self.max_depth = max_depth
    
    
    def set(self, price: float, amount: float, count: int) -> None:
        # NOTICE: Have been refactored by Claude-3-5-sonnet-20240620 
        new_level = BookLevel(price, amount, count)
        
        if amount == 0:  # Remove the level
            idx = bisect.bisect_left(self._asks, new_level)
            if idx < len(self._asks) and self._asks[idx] == new_level:
                del self._asks[idx]
        else:
            idx = bisect.bisect_left(self._asks, new_level)
            if idx < len(self._asks) and self._asks[idx] == new_level:
                self._asks[idx] = new_level  # Update existing level
            else:
                if idx < self.max_depth:  # Insert new level
                    self._asks.insert(idx, new_level)
                    if len(self._asks) > self.max_depth:
                        self._asks.pop()  # Remove last element if exceeding max_depth

    def __getitem__(self, key) -> Union[BookLevel, List[BookLevel]]:
        if isinstance(key, slice):
            start = key.start if key.start is not None else 0
            stop = key.stop if key.stop is not None else len(self._asks)
            step = key.step if key.step is not None else 1
            return [self._asks[i] for i in range(start, stop, step)]
        elif isinstance(key, int):
            return self._asks[key]
        else:
            raise TypeError("Invalid key type. Key must be an integer or a slice.")
    
    
    def __len__(self) -> int:
        return len(self._asks)
    
    def __eq__(self, other) -> bool:
        # NOTICE: Have been refactored by Claude-3-5-sonnet-20240620
        if not isinstance(other, Asks) or len(self._asks) != len(other._asks):
            return False
        
        return all(self_level.true_eq(other_level) for self_level, other_level in zip(self._asks, other._asks))
    
    def __iter__(self):
        return iter(self._asks)

    def __deepcopy__(self, memo):
        new_asks = Asks(self.max_depth)
        new_asks._asks = deepcopy(self._asks)
        return new_asks
    
    def __str__(self) -> str:
        return str(self._asks)
    
    def __repr__(self) -> str:
        return self.__str__()


class Bids:
    def __init__(self, max_depth: int = 400) -> None:
        self._bids: List[BookLevel] = []
        self.max_depth = max_depth
    
    
    def set(self, price: float, amount: float, count: int) -> None:
        # NOTICE: Have been refactored by Claude-3-5-sonnet-20240620 
        new_level = BookLevel(price, amount, count)
        
        if amount == 0:  # Remove the level
            idx = bisect.bisect_left(self._bids, -price, key=lambda x: -x.price)
            if idx < len(self._bids) and self._bids[idx] == new_level:
                del self._bids[idx]
        else:
            idx = bisect.bisect_left(self._bids, -price, key=lambda x: -x.price)
            if idx < len(self._bids) and self._bids[idx] == new_level:
                self._bids[idx] = new_level  # Update existing level
            else:
                if idx < self.max_depth:  # Insert new level
                    self._bids.insert(idx, new_level)
                    if len(self._bids) > self.max_depth:
                        self._bids.pop()  # Remove last element if exceeding max_depth


    def __getitem__(self, key) -> Union[BookLevel, List[BookLevel]]:
        if isinstance(key, slice):
            start = key.start if key.start is not None else 0
            stop = key.stop if key.stop is not None else len(self._bids)
            step = key.step if key.step is not None else 1
            return [self._bids[i] for i in range(start, stop, step)]
        elif isinstance(key, int):
            return self._bids[key]
        else:
            raise TypeError("Invalid key type. Key must be an integer or a slice.")
    
    
    def __len__(self) -> int:
        return len(self._bids)
    
    
    def __eq__(self, other) -> bool:
        # NOTICE: Have been refactored by Claude-3-5-sonnet-20240620
        if not isinstance(other, Bids) or len(self._bids) != len(other._bids):
            return False
        
        return all(self_level.true_eq(other_level) for self_level, other_level in zip(self._bids, other._bids))


    def __iter__(self):
        return iter(self._bids)
    
    def __deepcopy__(self, memo):
        new_bids = Bids(self.max_depth)
        new_bids._bids = deepcopy(self._bids)
        return new_bids

    def __str__(self) -> str:
        return str(self._bids)
    
    def __repr__(self) -> str:
        return self.__str__()


class BookCore:
    def __init__(self, instId: str, check_instId: bool = True) -> None:
        self.instId = instId
        self.check_instId = check_instId
        self._asks: Asks = Asks()
        self._bids: Bids = Bids()
    
    
    def set(self, row) -> None:
        if self.check_instId and 'instId' in row and (self.instId != row['instId'] and not self.instId == row['instId'] + '-400'):
            row_instId = row['instId']
            raise Exception(f'set {row_instId} row with {self.instId}')
        if row['side'] == 'ask':
            self._asks.set(row['price'], row['size'], row['numOrders'])
        elif row['side'] == 'bid':
            self._bids.set(row['price'], row['size'], row['numOrders'])
        else:
            raise Exception(f'Invalid side: {row["side"]}')

    @property
    def asks(self) -> Asks:
        return deepcopy(self._asks)
    
    @property
    def bids(self) -> Bids:
        return deepcopy(self._bids)
    
    @property
    def depth_asks(self) -> int:
        return len(self._asks)
    
    @property
    def depth_bids(self) -> int:
        return len(self._bids)
    
    def __deepcopy__(self, memo):
        new_bookcore = BookCore(self.instId, self.check_instId)
        new_bookcore._asks = deepcopy(self._asks, memo)
        new_bookcore._bids = deepcopy(self._bids, memo)
        return new_bookcore
        
    
    def __str__(self) -> str:
        return f'BookCore(instId={self.instId}, check_instId={self.check_instId}, asks={str(self.asks)}, bids={str(self.bids)})'
    
    def __repr__(self) -> str:
        return self.__str__()

    def filled(self, depth: int) -> bool:
        return len(self._asks) >= depth and len(self._bids) >= depth


