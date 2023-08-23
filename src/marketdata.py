import pandas as pd
from datetime import datetime

class MarketData:
    def __init__(self, simTime, path):
        self.simTime = simTime
        self.path = path
        self.books = None
        self.load_books()

    def load_books(self):
        try:
            # Load the order book data lazily from parquet files
            self.books = pd.read_parquet(self.path)
        except Exception as e:
            raise Exception(f"Failed to load order book data: {str(e)}")

    def update(self):
        # Update the market data to the current simulation time
        self.load_books()

    def __getitem__(self, key):
        if key == 'books':
            return self.books
        else:
            raise KeyError(f"Invalid key: {key}")

    def get_best_ask_price(self, symbol):
        if self.books is None:
            raise Exception("Order book data is not loaded")
        
        if symbol not in self.books.columns:
            raise KeyError(f"Symbol '{symbol}' not found in order book data")
        
        asks = self.books[symbol]['asks']
        if asks.empty:
            raise Exception(f"No ask prices available for symbol '{symbol}'")
        
        return asks.iloc[0]

    def get_best_bid_price(self, symbol, start_date=None, end_date=None):
        if self.books is None:
            raise Exception("Order book data is not loaded")
        
        if symbol not in self.books.columns:
            raise KeyError(f"Symbol '{symbol}' not found in order book data")
        
        bids = self.books[symbol]['bids']
        if bids.empty:
            raise Exception(f"No bid prices available for symbol '{symbol}'")
        
        if start_date is not None and end_date is not None:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            bids = bids.loc[start_date:end_date]
        
        return bids.iloc[0]
