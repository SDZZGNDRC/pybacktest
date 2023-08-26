import sys
sys.path.insert(0, sys.path[0]+"/../")
import os
from random import randint
import shutil
import tempfile

import pandas as pd

from src.simTime import SimTime
from typing import List
import bisect
import pytest

from src.books import Book, BookLevel, Asks, Bids

class TestBookLevel:
    def test_init(self):
        with pytest.raises(TypeError):
            BookLevel('100', 10.0, 1) # type: ignore
        with pytest.raises(ValueError):
            BookLevel(-100.0, 10.0, 1)
        with pytest.raises(TypeError):
            BookLevel(100.0, '10', 1) # type: ignore
        with pytest.raises(ValueError):
            BookLevel(100.0, -10.0, 1)
        with pytest.raises(TypeError):
            BookLevel(100.0, 10.0, '1') # type: ignore
        with pytest.raises(ValueError):
            BookLevel(100.0, 10.0, -1)

        bl = BookLevel(100.0, 10.0, 1)
        assert bl.price == 100.0
        assert bl.amount == 10.0
        assert bl.count == 1

    def test_comparison(self):
        bl1 = BookLevel(100.0, 10.0, 1)
        bl2 = BookLevel(200.0, 20.0, 2)
        assert bl1 < bl2
        assert not bl1 > bl2
        assert not bl1 == bl2

        bl3 = BookLevel(100.0, 20.0, 2)
        assert not bl1 < bl3
        assert not bl1 > bl3
        assert bl1 == bl3

        assert bl1 < 200.0
        assert not bl1 > 200.0
        assert not bl1 == 200.0

        assert not bl1 < 100.0
        assert not bl1 > 100.0
        assert bl1 == 100.0

        with pytest.raises(TypeError):
            bl1 < '200' # type: ignore
        with pytest.raises(TypeError):
            bl1 > '200' # type: ignore
        with pytest.raises(TypeError):
            bl1 == '200' # type: ignore


class TestAsks:
    def test_set(self):
        asks = Asks()
        assert len(asks) == 0

        asks.set(100.0, 10.0, 1)
        assert len(asks) == 1
        assert asks[0].price == 100.0
        assert asks[0].amount == 10.0
        assert asks[0].count == 1

        asks.set(200.0, 20.0, 2)
        assert len(asks) == 2
        assert asks[0].price == 100.0
        assert asks[1].price == 200.0

        asks.set(150.0, 15.0, 1)
        assert len(asks) == 3
        assert asks[0].price == 100.0
        assert asks[1].price == 150.0
        assert asks[2].price == 200.0

        asks.set(150.0, 0, 0)
        assert len(asks) == 2
        assert asks[0].price == 100.0
        assert asks[1].price == 200.0

        asks.set(100.0, 20.0, 2)
        assert len(asks) == 2
        assert asks[0].price == 100.0
        assert asks[0].amount == 20.0
        assert asks[0].count == 2


class TestBids:
    def test_set(self):
        bids = Bids()
        assert len(bids) == 0

        bids.set(100.0, 10.0, 1)
        assert len(bids) == 1
        assert bids[0].price == 100.0
        assert bids[0].amount == 10.0
        assert bids[0].count == 1

        bids.set(200.0, 20.0, 2)
        assert len(bids) == 2
        assert bids[0].price == 200.0
        assert bids[1].price == 100.0

        bids.set(150.0, 15.0, 1)
        assert len(bids) == 3
        assert bids[0].price == 200.0
        assert bids[1].price == 150.0
        assert bids[2].price == 100.0

        bids.set(150.0, 0, 0)
        assert len(bids) == 2
        assert bids[0].price == 200.0
        assert bids[1].price == 100.0

        bids.set(200.0, 30.0, 3)
        assert len(bids) == 2
        assert bids[0].price == 200.0
        assert bids[0].amount == 30.0
        assert bids[0].count == 3

# def build_book_update(df: pd.DataFrame) -> pd.DataFrame:
#     next_timestamp = df['timestamp'].max() + randint(10, 500)
#     new_df = pd.DataFrame()
    

def setup_book() -> str:
    temp_dir = tempfile.mkdtemp()
    
    df = pd.DataFrame()

    # snapshot
    df['price'] = [100.0, 105.0, 110.0, 115.0, 120.0, 125.0, 130.0, 135.0, 140.0, 145.0, 90.0, 85.0, 80.0, 75.0, 70.0, 65.0, 60.0, 55.0, 50.0, 45.0]
    df['size'] = [83.0, 19.0, 63.0, 10.0, 10.0, 53.0, 43.0, 47.0, 60.0, 47.0, 50.0, 39.0, 94.0, 59.0, 16.0, 54.0, 67.0, 60.0, 79.0, 27.0]
    df['numOrders'] = [1,3,2,9,10,8,8,6,3,5,1,4,6,5,5,2,3,5,8,3]
    df['side'] = ['ask' for _ in range(len(df['price'])//2)] + \
                    ['bid' for _ in range(len(df['price'])//2)]
    df['timestamp'] = 1687420840901
    df['action'] = 'snapshot'
    
    # update: 1687420841101
    new_df = pd.DataFrame()
    new_df['price'] = [100.0, 110.0, 140.0] + [85.0, 70.0, 55.0] # randomly choose some rows to update
    new_df['size'] = [69.0, 0, 70.0] + [17.0, 0, 37.0] # generate random size
    new_df['numOrders'] = [5, 2, 7] + [6, 4, 8] # generate random numOrders
    new_df['side'] = ['ask', 'ask', 'ask'] + ['bid', 'bid', 'bid']
    new_df['timestamp'] = 1687420841101 # next_timestamp should be larger than the previous timestamp
    new_df['action'] = 'update'
    df = pd.concat([df, new_df], ignore_index=True)
    
    # update: 1687420841201
    new_df = pd.DataFrame()
    new_df['price'] = [120.0, 130.0] + [60.0, 45.0]  # randomly choose some rows to update
    new_df['size'] = [92.0, 50.0] + [22.0, 78.0]  # generate random size
    new_df['numOrders'] = [3, 9] + [5, 7]  # generate random numOrders
    new_df['side'] = ['ask', 'ask'] + ['bid', 'bid']
    new_df['timestamp'] = 1687420841201  # next_timestamp should be larger than the previous timestamp
    new_df['action'] = 'update'
    df = pd.concat([df, new_df], ignore_index=True)
    
    df['instId'] = '1INCH-USDT-SWAP'
    
    filename = 'part-0-1687420840901-1687420841201.parquet'
    filepath = os.path.join(temp_dir, filename)
    df.to_parquet(filepath, index=False)
    return temp_dir

def clear_book(path: str) -> None:
    shutil.rmtree(path)


class TestBook:
    def test_init(self):
        path = setup_book()
        st = SimTime(1687420840901, 1687420841201)
        book = Book('1INCH-USDT-SWAP', st, path)

        correct_asks = Asks()
        correct_asks.set(100.0, 83.0, 1)
        correct_asks.set(105.0, 19.0, 3)
        correct_asks.set(110.0, 63.0, 2)
        correct_asks.set(115.0, 10.0, 9)
        correct_asks.set(120.0, 10.0, 10)
        correct_asks.set(125.0, 53.0, 8)
        correct_asks.set(130.0, 43.0, 8)
        correct_asks.set(135.0, 47.0, 6)
        correct_asks.set(140.0, 60.0, 3)
        correct_asks.set(145.0, 47.0, 5)
        
        assert book.current_ts == 1687420840901
        assert book.asks == correct_asks
        
        correct_bids = Bids()
        correct_bids.set(90.0, 50.0, 1)
        correct_bids.set(85.0, 39.0, 4)
        correct_bids.set(80.0, 94.0, 6)
        correct_bids.set(75.0, 59.0, 5)
        correct_bids.set(70.0, 16.0, 5)
        correct_bids.set(65.0, 54.0, 2)
        correct_bids.set(60.0, 67.0, 3)
        correct_bids.set(55.0, 60.0, 5)
        correct_bids.set(50.0, 79.0, 8)
        correct_bids.set(45.0, 27.0, 3)
        
        assert book.bids == correct_bids
        
        st.set(1687420841101)
        correct_asks = Asks()
        correct_asks.set(100.0, 69.0, 5)
        correct_asks.set(105.0, 19.0, 3)
        correct_asks.set(115.0, 10.0, 9)
        correct_asks.set(120.0, 10.0, 10)
        correct_asks.set(125.0, 53.0, 8)
        correct_asks.set(130.0, 43.0, 8)
        correct_asks.set(135.0, 47.0, 6)
        correct_asks.set(140.0, 70.0, 7)
        correct_asks.set(145.0, 47.0, 5)
        assert book.asks == correct_asks
        assert book.current_ts == 1687420841101
        
        correct_bids = Bids()
        correct_bids.set(90.0, 50.0, 1)
        correct_bids.set(85.0, 17.0, 6)
        correct_bids.set(80.0, 94.0, 6)
        correct_bids.set(75.0, 59.0, 5)
        correct_bids.set(65.0, 54.0, 2)
        correct_bids.set(60.0, 67.0, 3)
        correct_bids.set(55.0, 37.0, 8)
        correct_bids.set(50.0, 79.0, 8)
        correct_bids.set(45.0, 27.0, 3)
        
        assert book.bids == correct_bids
        
        
        st.set(1687420841201)
        correct_asks = Asks()
        correct_asks.set(100.0, 69.0, 5)
        correct_asks.set(105.0, 19.0, 3)
        correct_asks.set(115.0, 10.0, 9)
        correct_asks.set(120.0, 92.0, 3)
        correct_asks.set(125.0, 53.0, 8)
        correct_asks.set(130.0, 50.0, 9)
        correct_asks.set(135.0, 47.0, 6)
        correct_asks.set(140.0, 70.0, 7)
        correct_asks.set(145.0, 47.0, 5)
        assert book.asks == correct_asks
        assert book.current_ts == 1687420841201
        
        correct_bids = Bids()
        correct_bids.set(90.0, 50.0, 1)
        correct_bids.set(85.0, 17.0, 6)
        correct_bids.set(80.0, 94.0, 6)
        correct_bids.set(75.0, 59.0, 5)
        correct_bids.set(65.0, 54.0, 2)
        correct_bids.set(60.0, 22.0, 5)
        correct_bids.set(55.0, 37.0, 8)
        correct_bids.set(50.0, 79.0, 8)
        correct_bids.set(45.0, 78.0, 7)
        
        assert book.bids == correct_bids
        
if __name__ == "__main__":
    pytest.main()
