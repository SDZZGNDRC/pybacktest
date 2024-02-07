import sys
sys.path.insert(0, sys.path[0]+"/../")
import os
import shutil
import tempfile

import pandas as pd

from src.simTime import SimTime
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
        
        clear_book(path)
    
    
    def test_update(self):
        path = setup_book()
        st = SimTime(1687420840901, 1687420841201)
        book = Book('1INCH-USDT-SWAP', st, path)
        
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
        
        clear_book(path)
    
    
    def test_case(self):
        simTime = SimTime(1689070299902, 1689070343202) # 1689070748602
        book = Book('1INCH-USDC', simTime, r'D:\Project\pybacktest\test\test_books\books\1INCH-USDC', 10000)
        
        correct_asks = Asks()
        correct_asks.set(0.3076, 961.1742, 2)
        correct_asks.set(0.3097, 2168.9626, 1)
        correct_asks.set(0.3077, 4156.5571, 5)
        correct_asks.set(0.3078, 4047.8924, 2)
        correct_asks.set(0.308, 7288.5126, 2)
        correct_asks.set(0.3081, 16569.1202, 2)
        correct_asks.set(0.3082, 1853.9185, 2)
        correct_asks.set(0.3084, 353.9112, 1)
        correct_asks.set(0.3085, 1423.6948, 1)
        correct_asks.set(0.3086, 735.8448, 1)
        correct_asks.set(0.3087, 332.0725, 1)
        correct_asks.set(0.3088, 1423.6948, 1)
        correct_asks.set(0.3089, 3613.207, 1)
        correct_asks.set(0.3092, 4.9594, 2)
        correct_asks.set(0.3095, 3251.5038, 1)
        correct_asks.set(0.3096, 133.9724, 1)
        correct_asks.set(0.3101, 0.424, 1)
        correct_asks.set(0.3158, 0.4152, 1)
        correct_asks.set(0.3104, 3251.5038, 1)
        correct_asks.set(0.3105, 728.5941, 1)
        correct_asks.set(0.3111, 0.4228, 1)
        correct_asks.set(0.3114, 2285.2819, 2)
        correct_asks.set(0.312, 40650.8267, 2)
        correct_asks.set(0.3123, 69.7093, 1)
        correct_asks.set(0.313, 0.4189, 1)
        correct_asks.set(0.3132, 725.2219, 1)
        correct_asks.set(0.3135, 4.5341, 1)
        correct_asks.set(0.3139, 0.4177, 1)
        correct_asks.set(0.3141, 3251.5038, 1)
        correct_asks.set(0.3149, 0.4164, 1)
        correct_asks.set(0.4114, 6.25, 1)
        correct_asks.set(0.316, 0.1, 1)
        correct_asks.set(0.3169, 0.1, 1)
        correct_asks.set(0.3358, 4.5341, 1)
        correct_asks.set(0.3267, 1643.0187, 2)
        correct_asks.set(0.3177, 0.4127, 1)
        correct_asks.set(0.3178, 4.5341, 1)
        correct_asks.set(0.3187, 0.4114, 1)
        correct_asks.set(0.3196, 0.4103, 1)
        correct_asks.set(0.32, 4.5341, 1)
        correct_asks.set(0.3206, 0.409, 1)
        correct_asks.set(0.3216, 0.4077, 1)
        correct_asks.set(0.3222, 4.5341, 1)
        correct_asks.set(0.3226, 0.4064, 1)
        correct_asks.set(0.3234, 1055.4181, 1)
        correct_asks.set(0.3235, 0.4053, 1)
        correct_asks.set(0.3245, 4.9382, 2)
        correct_asks.set(0.3255, 0.4028, 1)
        correct_asks.set(0.3151, 3.4013, 1)
        correct_asks.set(0.3265, 0.4016, 1)
        correct_asks.set(0.3168, 0.4139, 1)
        correct_asks.set(0.3284, 0.3993, 1)
        correct_asks.set(0.3289, 4.5341, 1)
        correct_asks.set(0.3294, 0.398, 1)
        correct_asks.set(0.33, 1103.8105, 1)
        correct_asks.set(0.3304, 0.3968, 1)
        correct_asks.set(0.3312, 4.5341, 1)
        correct_asks.set(0.3314, 0.3956, 1)
        correct_asks.set(0.3324, 0.3945, 1)
        correct_asks.set(0.3333, 1020.0127, 1)
        correct_asks.set(0.3334, 0.3933, 1)
        correct_asks.set(0.3335, 4.5341, 1)
        correct_asks.set(0.3344, 0.3921, 1)
        correct_asks.set(0.3355, 0.3908, 1)
        correct_asks.set(0.3275, 0.4004, 1)
        correct_asks.set(0.3157, 4.5341, 1)
        correct_asks.set(0.3365, 0.3896, 1)
        correct_asks.set(0.3367, 1362.9887, 1)
        correct_asks.set(0.3708, 6.25, 1)
        correct_asks.set(0.3697, 4.5341, 1)
        correct_asks.set(0.3385, 0.3873, 1)
        correct_asks.set(0.3401, 1419.8667, 1)
        correct_asks.set(0.3404, 4.5341, 1)
        correct_asks.set(0.3428, 4.5341, 1)
        correct_asks.set(0.3436, 1486.1905, 1)
        correct_asks.set(0.3451, 4.5341, 1)
        correct_asks.set(0.3471, 1203.2135, 1)
        correct_asks.set(0.3475, 4.5341, 1)
        correct_asks.set(0.3499, 4.5341, 1)
        correct_asks.set(0.3506, 904.3091, 1)
        correct_asks.set(0.352, 6.25, 1)
        correct_asks.set(0.3523, 4.5341, 1)
        correct_asks.set(0.3711, 0.9563, 1)
        correct_asks.set(0.354, 6.25, 1)
        correct_asks.set(0.3547, 4.5341, 1)
        correct_asks.set(0.3561, 6.25, 1)
        correct_asks.set(0.3572, 4.5341, 1)
        correct_asks.set(0.3578, 1450.0177, 1)
        correct_asks.set(0.3581, 6.25, 1)
        correct_asks.set(0.3596, 4.5341, 1)
        correct_asks.set(0.3602, 6.25, 1)
        correct_asks.set(0.3614, 1679.3368, 1)
        correct_asks.set(0.3621, 4.5341, 1)
        correct_asks.set(0.3623, 6.25, 1)
        correct_asks.set(0.3644, 6.25, 1)
        correct_asks.set(0.3646, 4.5341, 1)
        correct_asks.set(0.3665, 6.25, 1)
        correct_asks.set(0.3671, 4.5341, 1)
        correct_asks.set(0.3542, 951.7777, 1)
        correct_asks.set(0.4126, 4.5309, 1)
        correct_asks.set(0.3722, 4.5341, 1)
        correct_asks.set(0.409, 6.25, 1)
        correct_asks.set(0.3375, 0.3885, 1)
        correct_asks.set(0.3905, 10.7809, 2)
        correct_asks.set(0.3729, 6.25, 1)
        correct_asks.set(0.3748, 4.5341, 1)
        correct_asks.set(0.3751, 6.25, 1)
        correct_asks.set(0.3772, 6.25, 1)
        correct_asks.set(0.3774, 4.5341, 1)
        correct_asks.set(0.3794, 6.25, 1)
        correct_asks.set(0.38, 4.5341, 1)
        correct_asks.set(0.3816, 6.25, 1)
        correct_asks.set(0.3826, 4.5341, 1)
        correct_asks.set(0.3838, 6.25, 1)
        correct_asks.set(0.3852, 4.5341, 1)
        correct_asks.set(0.3861, 6.25, 1)
        correct_asks.set(0.4098, 4.5309, 1)
        correct_asks.set(0.4876, 2.7297, 2)
        correct_asks.set(0.3928, 6.25, 1)
        correct_asks.set(0.3381, 4.5341, 1)
        correct_asks.set(0.3932, 4.5309, 1)
        correct_asks.set(0.3951, 6.25, 1)
        correct_asks.set(0.3959, 4.5309, 1)
        correct_asks.set(0.3974, 6.25, 1)
        correct_asks.set(0.3987, 4.5309, 1)
        correct_asks.set(0.3997, 6.25, 1)
        correct_asks.set(0.4014, 4.5309, 1)
        correct_asks.set(0.402, 6.25, 1)
        correct_asks.set(0.4042, 4.5309, 1)
        correct_asks.set(0.4043, 6.25, 1)
        correct_asks.set(0.4067, 6.25, 1)
        correct_asks.set(0.407, 4.5309, 1)
        correct_asks.set(0.3883, 6.25, 1)
        correct_asks.set(0.3686, 6.25, 1)
        correct_asks.set(0.3879, 4.5309, 1)
        correct_asks.set(0.472, 0.3001, 1)
        correct_asks.set(0.427, 4.5309, 1)
        correct_asks.set(0.4162, 6.25, 1)
        correct_asks.set(0.4183, 4.5309, 1)
        correct_asks.set(0.4186, 6.25, 1)
        correct_asks.set(0.4199, 0.2093, 1)
        correct_asks.set(0.421, 6.4593, 2)
        correct_asks.set(0.4212, 4.5309, 1)
        correct_asks.set(0.4221, 1.1656, 2)
        correct_asks.set(0.4232, 0.2093, 1)
        correct_asks.set(0.4234, 6.25, 1)
        correct_asks.set(0.4241, 4.5309, 1)
        correct_asks.set(0.4243, 0.2093, 1)
        correct_asks.set(0.4254, 0.2093, 1)
        correct_asks.set(0.4573, 4.5309, 1)
        correct_asks.set(0.4266, 0.2093, 1)
        correct_asks.set(0.4277, 0.2093, 1)
        correct_asks.set(0.4368, 0.2093, 1)
        correct_asks.set(0.4284, 6.25, 1)
        correct_asks.set(0.4288, 0.2093, 1)
        correct_asks.set(0.4299, 4.5309, 1)
        correct_asks.set(0.43, 0.2093, 1)
        correct_asks.set(0.4308, 6.25, 1)
        correct_asks.set(0.4311, 0.2093, 1)
        correct_asks.set(0.4322, 0.2093, 1)
        correct_asks.set(0.4329, 4.5309, 1)
        correct_asks.set(0.4333, 6.25, 1)
        correct_asks.set(0.4334, 0.2093, 1)
        correct_asks.set(0.4345, 0.2093, 1)
        correct_asks.set(0.4357, 0.2093, 1)
        correct_asks.set(0.438, 0.2093, 1)
        correct_asks.set(0.4259, 6.25, 1)
        correct_asks.set(0.4389, 4.5309, 1)
        correct_asks.set(0.4569, 0.2093, 1)
        correct_asks.set(0.4392, 0.2093, 1)
        correct_asks.set(0.4403, 0.2093, 1)
        correct_asks.set(0.4409, 6.25, 1)
        correct_asks.set(0.4415, 0.2093, 1)
        correct_asks.set(0.4419, 4.5309, 1)
        correct_asks.set(0.4474, 0.2093, 1)
        correct_asks.set(0.4384, 6.25, 1)
        correct_asks.set(0.4435, 6.25, 1)
        correct_asks.set(0.4438, 0.2093, 1)
        correct_asks.set(0.4444, 24.7524, 1)
        correct_asks.set(0.4449, 4.5309, 1)
        correct_asks.set(0.445, 0.2093, 1)
        correct_asks.set(0.446, 6.25, 1)
        correct_asks.set(0.4462, 0.2093, 1)
        correct_asks.set(0.4358, 6.25, 1)
        correct_asks.set(0.4427, 0.2093, 1)
        correct_asks.set(0.448, 4.5309, 1)
        correct_asks.set(0.4486, 6.25, 1)
        correct_asks.set(0.4497, 0.2093, 1)
        correct_asks.set(0.4509, 0.2093, 1)
        correct_asks.set(0.4511, 4.5309, 1)
        correct_asks.set(0.4512, 6.25, 1)
        correct_asks.set(0.4521, 0.5094, 2)
        correct_asks.set(0.4533, 0.5094, 2)
        correct_asks.set(0.4538, 6.25, 1)
        correct_asks.set(0.4542, 4.5309, 1)
        correct_asks.set(0.4545, 0.5094, 2)
        correct_asks.set(0.4557, 0.2093, 1)
        correct_asks.set(0.4558, 0.3001, 1)
        correct_asks.set(0.4564, 6.25, 1)
        correct_asks.set(0.4485, 0.2093, 1)
        correct_asks.set(0.4359, 4.5309, 1)
        correct_asks.set(0.457, 0.3001, 1)
        correct_asks.set(0.4668, 4.5309, 1)
        correct_asks.set(0.4655, 0.2093, 1)
        correct_asks.set(0.4591, 6.25, 1)
        correct_asks.set(0.4594, 0.2093, 1)
        correct_asks.set(0.4595, 0.3001, 1)
        correct_asks.set(0.4605, 4.5309, 1)
        correct_asks.set(0.4606, 0.2093, 1)
        correct_asks.set(0.4607, 0.3001, 1)
        correct_asks.set(0.4618, 6.4593, 2)
        correct_asks.set(0.462, 0.3001, 1)
        correct_asks.set(0.463, 0.2093, 1)
        correct_asks.set(0.4632, 0.3001, 1)
        correct_asks.set(0.4636, 4.5309, 1)
        correct_asks.set(0.4642, 0.2093, 1)
        correct_asks.set(0.4644, 6.25, 1)
        correct_asks.set(0.4582, 0.3001, 1)
        correct_asks.set(0.4645, 0.3001, 1)
        correct_asks.set(0.4725, 6.25, 1)
        correct_asks.set(0.4667, 0.2093, 1)
        correct_asks.set(0.4138, 6.25, 1)
        correct_asks.set(0.467, 0.3001, 1)
        correct_asks.set(0.4671, 6.25, 1)
        correct_asks.set(0.4679, 0.2093, 1)
        correct_asks.set(0.4682, 0.3001, 1)
        correct_asks.set(0.4692, 0.2093, 1)
        correct_asks.set(0.4695, 0.3001, 1)
        correct_asks.set(0.4698, 6.25, 1)
        correct_asks.set(0.4701, 4.5309, 1)
        correct_asks.set(0.4704, 0.2093, 1)
        correct_asks.set(0.4708, 0.3001, 1)
        correct_asks.set(0.4717, 0.2093, 1)
        correct_asks.set(0.4657, 0.3001, 1)
        correct_asks.set(0.4154, 4.5309, 1)
        correct_asks.set(0.4729, 0.2093, 1)
        correct_asks.set(0.4869, 0.2093, 1)
        correct_asks.set(0.4581, 0.2093, 1)
        correct_asks.set(0.4808, 6.25, 1)
        correct_asks.set(0.4742, 0.2093, 1)
        correct_asks.set(0.4746, 0.3001, 1)
        correct_asks.set(0.4753, 6.25, 1)
        correct_asks.set(0.4754, 0.2093, 1)
        correct_asks.set(0.4759, 0.3001, 1)
        correct_asks.set(0.4766, 4.5309, 1)
        correct_asks.set(0.4767, 0.2093, 1)
        correct_asks.set(0.4772, 0.3001, 1)
        correct_asks.set(0.4779, 0.2093, 1)
        correct_asks.set(0.478, 6.25, 1)
        correct_asks.set(0.4785, 0.3001, 1)
        correct_asks.set(0.4792, 0.2093, 1)
        correct_asks.set(0.4733, 4.831, 2)
        correct_asks.set(0.4798, 4.831, 2)
        correct_asks.set(0.4811, 0.3001, 1)
        correct_asks.set(0.473, 0.9563, 1)
        correct_asks.set(0.4812, 1.274, 1)
        correct_asks.set(0.4817, 0.2093, 1)
        correct_asks.set(0.4824, 0.3001, 1)
        correct_asks.set(0.483, 0.2093, 1)
        correct_asks.set(0.4831, 4.5309, 1)
        correct_asks.set(0.4836, 6.25, 1)
        correct_asks.set(0.4837, 0.3001, 1)
        correct_asks.set(0.485, 0.3001, 1)
        correct_asks.set(0.4856, 0.2093, 1)
        correct_asks.set(0.4863, 0.3001, 1)
        correct_asks.set(0.4864, 6.25, 1)
        correct_asks.set(0.4865, 4.5309, 1)
        correct_asks.set(0.4805, 0.2093, 1)
        correct_asks.set(0.4875, 1.274, 1)
        correct_asks.set(0.4843, 0.2093, 1)
        correct_asks.set(0.4882, 0.2093, 1)
        correct_asks.set(0.4892, 6.25, 1)
        correct_asks.set(0.4894, 0.2093, 1)
        correct_asks.set(0.4898, 4.5309, 1)
        correct_asks.set(0.4903, 0.3001, 1)
        correct_asks.set(0.4907, 0.2093, 1)
        correct_asks.set(0.4916, 0.3001, 1)
        correct_asks.set(0.492, 6.4593, 2)
        correct_asks.set(0.4929, 0.3001, 1)
        correct_asks.set(0.4932, 4.5309, 1)
        correct_asks.set(0.4933, 0.2093, 1)
        correct_asks.set(0.4937, 1.274, 1)
        correct_asks.set(0.4942, 0.3001, 1)
        correct_asks.set(0.4946, 0.2093, 1)
        correct_asks.set(0.4949, 6.25, 1)
        correct_asks.set(0.496, 0.2093, 1)
        correct_asks.set(0.5012, 0.2093, 1)
        correct_asks.set(0.4966, 4.5309, 1)
        correct_asks.set(0.4967, 0.1624, 1)
        correct_asks.set(0.4969, 0.3001, 1)
        correct_asks.set(0.4973, 0.2093, 1)
        correct_asks.set(0.4978, 0.7257, 1)
        correct_asks.set(0.498, 0.1624, 1)
        correct_asks.set(0.4983, 0.3001, 1)
        correct_asks.set(0.4986, 0.2093, 1)
        correct_asks.set(0.4993, 0.1624, 1)
        correct_asks.set(0.4996, 0.3001, 1)
        correct_asks.set(0.4999, 0.2093, 1)
        correct_asks.set(0.5, 5.8049, 2)
        correct_asks.set(0.5006, 6.4124, 2)
        correct_asks.set(0.4956, 0.3001, 1)
        correct_asks.set(0.5019, 0.1624, 1)
        correct_asks.set(0.5026, 0.2093, 1)
        correct_asks.set(0.5033, 0.1624, 1)
        correct_asks.set(0.5035, 10.7809, 2)
        correct_asks.set(0.5037, 0.3001, 1)
        correct_asks.set(0.5039, 0.2093, 1)
        correct_asks.set(0.5046, 0.1624, 1)
        correct_asks.set(0.505, 0.3001, 1)
        correct_asks.set(0.5052, 0.2093, 1)
        correct_asks.set(0.5059, 0.1624, 1)
        correct_asks.set(0.5062, 1.274, 1)
        correct_asks.set(0.5064, 0.3001, 1)
        correct_asks.set(0.5065, 6.25, 1)
        correct_asks.set(0.5066, 0.2093, 1)
        correct_asks.set(0.5069, 4.5309, 1)
        correct_asks.set(0.5073, 0.1624, 1)
        correct_asks.set(0.501, 0.3001, 1)
        correct_asks.set(0.5079, 0.2093, 1)
        correct_asks.set(0.508, 20, 1)
        correct_asks.set(0.5092, 0.5094, 2)
        correct_asks.set(0.5094, 6.25, 1)
        correct_asks.set(0.51, 0.1624, 1)
        correct_asks.set(0.5104, 4.5309, 1)
        correct_asks.set(0.5105, 0.3001, 1)
        correct_asks.set(0.5106, 0.2093, 1)
        correct_asks.set(0.5113, 0.1624, 1)
        correct_asks.set(0.5119, 0.5094, 2)
        correct_asks.set(0.5123, 6.25, 1)
        correct_asks.set(0.5125, 1.274, 1)
        correct_asks.set(0.5127, 0.1624, 1)
        correct_asks.set(0.5133, 0.5094, 2)
        correct_asks.set(0.5023, 0.3001, 1)
        correct_asks.set(0.5139, 4.5309, 1)
        correct_asks.set(0.514, 0.1624, 1)
        correct_asks.set(0.5147, 0.5094, 2)
        correct_asks.set(0.5259, 0.3001, 1)
        correct_asks.set(0.5154, 0.1624, 1)
        correct_asks.set(0.516, 0.2093, 1)
        correct_asks.set(0.5161, 0.3001, 1)
        correct_asks.set(0.5167, 0.1624, 1)
        correct_asks.set(0.5174, 0.2093, 1)
        correct_asks.set(0.5175, 4.831, 2)
        correct_asks.set(0.5181, 0.1624, 1)
        correct_asks.set(0.5183, 6.25, 1)
        correct_asks.set(0.5187, 1.274, 1)
        correct_asks.set(0.5188, 0.2093, 1)
        correct_asks.set(0.5189, 0.3001, 1)
        correct_asks.set(0.5195, 0.1624, 1)
        correct_asks.set(0.5201, 0.2093, 1)
        correct_asks.set(0.5264, 0.1624, 1)
        correct_asks.set(0.5203, 0.3001, 1)
        correct_asks.set(0.521, 4.5309, 1)
        correct_asks.set(0.5213, 6.25, 1)
        correct_asks.set(0.5215, 0.2093, 1)
        correct_asks.set(0.5217, 0.3001, 1)
        correct_asks.set(0.5222, 0.1624, 1)
        correct_asks.set(0.5229, 0.2093, 1)
        correct_asks.set(0.5231, 0.3001, 1)
        correct_asks.set(0.5236, 0.1624, 1)
        correct_asks.set(0.524, 0.9563, 1)
        correct_asks.set(0.5243, 6.4593, 2)
        correct_asks.set(0.5245, 0.3001, 1)
        correct_asks.set(0.5246, 4.5309, 1)
        correct_asks.set(0.525, 1.4364, 2)
        correct_asks.set(0.5257, 0.2093, 1)
        correct_asks.set(0.5209, 0.1624, 1)
        correct_asks.set(0.5078, 0.3001, 1)
        correct_asks.set(0.5271, 0.2093, 1)
        correct_asks.set(0.5327, 0.2093, 1)
        correct_asks.set(0.5278, 0.1624, 1)
        correct_asks.set(0.5282, 4.5309, 1)
        correct_asks.set(0.5283, 2.4296, 1)
        correct_asks.set(0.5284, 0.2093, 1)
        correct_asks.set(0.5288, 0.3001, 1)
        correct_asks.set(0.5292, 0.1624, 1)
        correct_asks.set(0.5298, 0.2093, 1)
        correct_asks.set(0.5302, 0.3001, 1)
        correct_asks.set(0.5304, 6.25, 1)
        correct_asks.set(0.5306, 0.1624, 1)
        correct_asks.set(0.5312, 1.4833, 2)
        correct_asks.set(0.5317, 0.3001, 1)
        correct_asks.set(0.5319, 4.5309, 1)
        correct_asks.set(0.5274, 6.5501, 2)
        correct_asks.set(0.532, 0.1624, 1)
        correct_asks.set(0.5153, 6.25, 1)
        correct_asks.set(0.5334, 0.1624, 1)
        correct_asks.set(0.5335, 6.25, 1)
        correct_asks.set(0.5341, 0.2093, 1)
        correct_asks.set(0.5345, 0.3001, 1)
        correct_asks.set(0.5348, 0.1624, 1)
        correct_asks.set(0.5355, 4.7402, 2)
        correct_asks.set(0.536, 0.3001, 1)
        correct_asks.set(0.5362, 0.1624, 1)
        correct_asks.set(0.5366, 6.25, 1)
        correct_asks.set(0.5369, 0.2093, 1)
        correct_asks.set(0.5374, 0.3001, 1)
        correct_asks.set(0.5331, 0.3001, 1)
        correct_asks.set(0.4889, 0.3001, 1)
        correct_asks.set(0.5086, 0.1624, 1)
        
        correct_bids = Bids()
        correct_bids.set(0.3071, 4239.1799, 3)
        correct_bids.set(0.2946, 0.4451, 1)
        correct_bids.set(0.3072, 986.4314, 2)
        correct_bids.set(0.3074, 813.6847, 2)
        correct_bids.set(0.3073, 813.3614, 1)
        correct_bids.set(0.3068, 1125.3244, 1)
        correct_bids.set(0.3039, 728.5941, 1)
        correct_bids.set(0.3067, 1423.6948, 1)
        correct_bids.set(0.3066, 1423.6948, 1)
        correct_bids.set(0.3065, 366.5812, 1)
        correct_bids.set(0.3064, 3613.6349, 2)
        correct_bids.set(0.3063, 794.3689, 1)
        correct_bids.set(0.3062, 389.4503, 1)
        correct_bids.set(0.3059, 340.1745, 1)
        correct_bids.set(0.3057, 2168.9626, 1)
        correct_bids.set(0.3055, 0.4292, 1)
        correct_bids.set(0.3054, 3979.5694, 2)
        correct_bids.set(0.305, 4.5341, 1)
        correct_bids.set(0.307, 7350.1556, 2)
        correct_bids.set(0.3045, 3250.9753, 1)
        correct_bids.set(0.3069, 17927.6153, 4)
        correct_bids.set(0.3043, 135.0225, 1)
        correct_bids.set(0.2989, 0.1, 1)
        correct_bids.set(0.3036, 3250.9753, 1)
        correct_bids.set(0.3033, 40597.5966, 1)
        correct_bids.set(0.3029, 4.5341, 1)
        correct_bids.set(0.3028, 0.433, 1)
        correct_bids.set(0.3026, 3250.9753, 1)
        correct_bids.set(0.3024, 358.337, 1)
        correct_bids.set(0.3018, 0.4344, 1)
        correct_bids.set(0.3017, 3250.9753, 1)
        correct_bids.set(0.301, 358.337, 1)
        correct_bids.set(0.3009, 4.9698, 2)
        correct_bids.set(0.3008, 374.3518, 1)
        correct_bids.set(0.3, 0.437, 1)
        correct_bids.set(0.2999, 58.8004, 1)
        correct_bids.set(0.3037, 0.4317, 1)
        correct_bids.set(0.2991, 0.4384, 1)
        correct_bids.set(0.2988, 4.5341, 1)
        correct_bids.set(0.2816, 0.4656, 1)
        correct_bids.set(0.2894, 0.4531, 1)
        correct_bids.set(0.2973, 0.441, 1)
        correct_bids.set(0.2968, 4.5341, 1)
        correct_bids.set(0.2964, 0.4424, 1)
        correct_bids.set(0.2955, 0.4437, 1)
        correct_bids.set(0.2947, 4.5341, 1)
        correct_bids.set(0.2938, 0.4463, 1)
        correct_bids.set(0.293, 1155.0635, 1)
        correct_bids.set(0.2929, 1552.4379, 2)
        correct_bids.set(0.2927, 4.5341, 1)
        correct_bids.set(0.292, 0.449, 1)
        correct_bids.set(0.2911, 0.4504, 1)
        correct_bids.set(0.2907, 4.5341, 1)
        correct_bids.set(0.2902, 0.4518, 1)
        correct_bids.set(0.298, 0.1, 1)
        correct_bids.set(0.2899, 1715.8394, 1)
        correct_bids.set(0.2982, 0.4397, 1)
        correct_bids.set(0.2885, 0.4545, 1)
        correct_bids.set(0.2876, 0.4559, 1)
        correct_bids.set(0.287, 1990.2931, 1)
        correct_bids.set(0.2868, 0.4572, 1)
        correct_bids.set(0.2867, 4.5341, 1)
        correct_bids.set(0.2859, 0.4586, 1)
        correct_bids.set(0.285, 50.46, 2)
        correct_bids.set(0.2848, 4.5341, 1)
        correct_bids.set(0.2842, 0.4613, 1)
        correct_bids.set(0.2841, 1549.5467, 1)
        correct_bids.set(0.2833, 0.4628, 1)
        correct_bids.set(0.2828, 4.5341, 1)
        correct_bids.set(0.2825, 0.4641, 1)
        correct_bids.set(0.2887, 4.5341, 1)
        correct_bids.set(0.2812, 2175.9532, 1)
        correct_bids.set(0.3046, 0.4305, 1)
        correct_bids.set(0.2808, 0.4669, 1)
        correct_bids.set(0.2667, 0.4916, 1)
        correct_bids.set(0.2791, 0.4698, 1)
        correct_bids.set(0.279, 4.5341, 1)
        correct_bids.set(0.2783, 1701.69, 1)
        correct_bids.set(0.2782, 0.4713, 1)
        correct_bids.set(0.2774, 0.4727, 1)
        correct_bids.set(0.2771, 4.5341, 1)
        correct_bids.set(0.2766, 0.474, 1)
        correct_bids.set(0.2757, 0.4756, 1)
        correct_bids.set(0.2755, 1632.1115, 1)
        correct_bids.set(0.2752, 4.5341, 1)
        correct_bids.set(0.275, 549.0909, 1)
        correct_bids.set(0.2749, 0.477, 1)
        correct_bids.set(0.2741, 0.4783, 1)
        correct_bids.set(0.2659, 5.0272, 2)
        correct_bids.set(0.2733, 4.5341, 1)
        correct_bids.set(0.2727, 1816.5104, 1)
        correct_bids.set(0.2809, 4.5341, 1)
        correct_bids.set(0.2716, 0.4827, 1)
        correct_bids.set(0.2714, 4.5341, 1)
        correct_bids.set(0.2708, 0.4842, 1)
        correct_bids.set(0.27, 0.4856, 1)
        correct_bids.set(0.2699, 1198.1297, 1)
        correct_bids.set(0.2696, 4.5341, 1)
        correct_bids.set(0.2692, 0.487, 1)
        correct_bids.set(0.2683, 0.4887, 1)
        correct_bids.set(0.2679, 1289.1069, 1)
        correct_bids.set(0.2677, 4.5341, 1)
        correct_bids.set(0.2675, 0.4901, 1)
        correct_bids.set(0.2672, 2176.0295, 1)
        correct_bids.set(0.2732, 0.4799, 1)
        correct_bids.set(0.2651, 0.4946, 1)
        correct_bids.set(0.2724, 0.4813, 1)
        correct_bids.set(0.0003, 1666.6666, 1)
        correct_bids.set(0.2572, 0.5098, 1)
        correct_bids.set(0.2643, 0.4961, 1)
        correct_bids.set(0.2641, 4.5341, 1)
        correct_bids.set(0.2635, 0.4976, 1)
        correct_bids.set(0.2627, 0.4991, 1)
        correct_bids.set(0.2623, 4.5341, 1)
        correct_bids.set(0.2619, 0.5006, 1)
        correct_bids.set(0.2618, 1966.1834, 1)
        correct_bids.set(0.2612, 0.502, 1)
        correct_bids.set(0.2605, 4.5341, 1)
        correct_bids.set(0.2604, 0.5035, 1)
        correct_bids.set(0.2596, 0.5051, 1)
        correct_bids.set(0.2588, 0.5066, 1)
        correct_bids.set(0.2587, 4.5341, 1)
        correct_bids.set(0.2569, 4.5341, 1)
        correct_bids.set(0.258, 0.5082, 1)
        correct_bids.set(0.24, 20.8333, 1)
        correct_bids.set(0.2565, 0.5112, 1)
        correct_bids.set(0.2557, 0.5128, 1)
        correct_bids.set(0.2552, 4.5341, 1)
        correct_bids.set(0.2534, 4.5341, 1)
        correct_bids.set(0.2517, 4.5341, 1)
        correct_bids.set(0.25, 4.5341, 1)
        correct_bids.set(0.245, 1, 1)
        correct_bids.set(0.2645, 2332.6352, 1)
        correct_bids.set(0.2799, 0.4684, 1)
        correct_bids.set(0.221, 500, 1)
        correct_bids.set(0.2, 1002, 2)
        correct_bids.set(0.1809, 525.1545, 1)
        correct_bids.set(0.15, 6.6, 1)
        correct_bids.set(0.121, 4133.3625, 1)
        
        assert correct_asks == book.asks
        assert correct_bids == book.bids
        assert book.current_ts == 1689070299902
        
        simTime.set(1689070301302)
        correct_bids.set(0.3069, 17199.0212, 3)
        correct_bids.set(0.3071, 4967.774, 4)
        correct_bids.set(0.307, 8475.48, 3)
        correct_bids.set(0.3068, 0, 0)

        assert correct_asks == book.asks
        assert correct_bids == book.bids
        assert book.current_ts == 1689070301302
        
        simTime.set(1689070303702)
        correct_asks.set(0.3077, 4322.415, 6)
        correct_asks.set(0.3077, 2697.1443, 5)
        correct_asks.set(0.3078, 5672.6705, 3)
        
        assert correct_asks == book.asks
        assert correct_bids == book.bids
        assert book.current_ts == 1689070303702
        
        simTime.set(1689070307402)
        correct_asks.set(0.3076, 1773.9196, 3)
        correct_asks.set(0.3077, 1884.6428, 4)

        assert correct_asks == book.asks
        assert correct_bids == book.bids
        assert book.current_ts == 1689070307402

    def test_case2(self):
        simTime = SimTime(0, 628000)
        book = Book('TEST-USDT', simTime, r'D:\Project\pybacktest\test\test_exchanges\books\TEST-USDT')
        
        # 0
        assert book.asks[0] == (1001, 1, 1)
        assert book.asks[1] == (1002, 1, 1)
        assert book.asks[2] == (1003, 1, 1)
        assert book.asks[3] == (1004, 1, 1)
        assert book.asks[4] == (1005, 1, 1)
        
        assert book.bids[0] == (999, 1, 1)
        assert book.bids[1] == (998, 1, 1)
        assert book.bids[2] == (997, 1, 1)
        assert book.bids[3] == (996, 1, 1)
        assert book.bids[4] == (995, 1, 1)
        
        # 1000
        simTime.set(1000)
        assert book.asks[0] == (1002, 1, 1)
        assert book.asks[1] == (1003, 1, 1)
        assert book.asks[2] == (1004, 1, 1)
        assert book.asks[3] == (1005, 1, 1)
        assert book.asks[4] == (1006, 1, 1)
        
        assert book.bids[0] == (1000, 1, 1)
        assert book.bids[1] == ( 999, 1, 1)
        assert book.bids[2] == ( 998, 1, 1)
        assert book.bids[3] == ( 997, 1, 1)
        assert book.bids[4] == ( 996, 1, 1)
        
        # 2000
        simTime.set(2000)
        assert book.asks[0] == (1003, 1, 1)
        assert book.asks[1] == (1004, 1, 1)
        assert book.asks[2] == (1005, 1, 1)
        assert book.asks[3] == (1006, 1, 1)
        assert book.asks[4] == (1007, 1, 1)
        
        assert book.bids[0] == (1001, 1, 1)
        assert book.bids[1] == (1000, 1, 1)
        assert book.bids[2] == ( 999, 1, 1)
        assert book.bids[3] == ( 998, 1, 1)
        assert book.bids[4] == ( 997, 1, 1)
        
        # 3000
        simTime.set(3000)
        assert book.asks[0] == (1004, 1, 1)
        assert book.asks[1] == (1005, 1, 1)
        assert book.asks[2] == (1006, 1, 1)
        assert book.asks[3] == (1007, 1, 1)
        assert book.asks[4] == (1008, 1, 1)
        
        assert book.bids[0] == (1002, 1, 1)
        assert book.bids[1] == (1001, 1, 1)
        assert book.bids[2] == (1000, 1, 1)
        assert book.bids[3] == ( 999, 1, 1)
        assert book.bids[4] == ( 998, 1, 1)
        
        # 4000
        simTime.set(4000)
        assert book.asks[0] == (1005, 1, 1)
        assert book.asks[1] == (1006, 1, 1)
        assert book.asks[2] == (1007, 1, 1)
        assert book.asks[3] == (1008, 1, 1)
        assert book.asks[4] == (1009, 1, 1)
        
        assert book.bids[0] == (1003, 1, 1)
        assert book.bids[1] == (1002, 1, 1)
        assert book.bids[2] == (1001, 1, 1)
        assert book.bids[3] == (1000, 1, 1)
        assert book.bids[4] == ( 999, 1, 1)
        
        # 16000
        simTime.set(16000)
        assert book.asks[0] == (1016.9, 1, 1)
        assert book.asks[1] == (1017.9, 1, 1)
        assert book.asks[2] == (1018.9, 1, 1)
        assert book.asks[3] == (1019.9, 1, 1)
        assert book.asks[4] == (1020.9, 1, 1)
        
        assert book.bids[0] == (1014.9, 1, 1)
        assert book.bids[1] == (1013.9, 1, 1)
        assert book.bids[2] == (1012.9, 1, 1)
        assert book.bids[3] == (1011.9, 1, 1)
        assert book.bids[4] == (1010.9, 1, 1)

if __name__ == "__main__":
    pytest.main()
