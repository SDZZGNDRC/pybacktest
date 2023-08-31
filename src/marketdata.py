import os

from src.books import Books

class MarketData:
    def __init__(self, simTime, path, max_interval: int = 2000):
        self.simTime = simTime
        self.path = path
        self.books = Books(os.path.join(path, 'books'), simTime, max_interval)
    
    
    def __getitem__(self, data_type: str):
        if data_type == 'books':
            return self.books
        else:
            raise Exception(f'Invalid data type: {data_type}')
