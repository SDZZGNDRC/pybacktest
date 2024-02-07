import bisect
from typing import List

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
        elif isinstance(__value, list):
            return [self.price, self.amount, self.count] == __value
        elif isinstance(__value, tuple):
            return (self.price, self.amount, self.count) == __value
        else:
            raise TypeError(f"Unsupported type({type(__value)}) for comparison.")
    
    
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

class BookCore:
    def __init__(self, instId: str, check_instId: bool = True) -> None:
        self.instId = instId
        self.check_instId = check_instId
        self.asks: Asks = Asks()
        self.bids: Bids = Bids()
    
    
    def set(self, row: dict) -> None:
        if self.check_instId and 'instId' in row and self.instId != row['instId']:
            row_instId = row['instId']
            raise Exception(f'set {row_instId} row with {self.instId}')
        if row['side'] == 'ask':
            self.asks.set(row['price'], row['size'], row['numOrders'])
        elif row['side'] == 'bid':
            self.bids.set(row['price'], row['size'], row['numOrders'])
        else:
            raise Exception(f'Invalid side: {row["side"]}')
        