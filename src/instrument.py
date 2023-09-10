
from datetime import datetime
from typing import Optional, Union

from src.simTime import SimTime


class Pair:
    def __init__(self,
                base_ccy: str,
                quote_ccy: str,
                ) -> None:
        self._base_ccy = base_ccy
        self._quote_ccy = quote_ccy
    
    def __str__(self) -> str:
        return f'{self.base_ccy}-{self.quote_ccy}'
    
    def __repr__(self) -> str:
        return f'Pair(base_ccy={self.base_ccy}, quote_ccy={self.quote_ccy})'
    
    @property
    def base_ccy(self) -> str:
        return self._base_ccy

    @property
    def quote_ccy(self) -> str:
        return self._quote_ccy

class InstrumentType:
    SPOT = 'SPOT'
    FUTURES = 'FUTURES'
    SWAP = 'SWAP'

class Instrument:
    def __init__(self, 
                pair: Pair,
                instId: str,
                type: str, # SPOT | FUTURES | SWAP
                listTime: Optional[int] = None,
                expTime: Optional[int] = None,
                contract_size: Optional[float] = None,
                tick_size: Optional[float] = None,
                ) -> None:
        self.pair = pair
        self.instId = instId
        self.type = type
        if listTime and listTime <= 0:
            raise ValueError(f'listTime {listTime} should be greater than 0.')
        self._listTime = listTime
        if expTime and expTime <= 0:
            raise ValueError(f'expTime {listTime} should be greater than 0.')
        self._expTime = expTime
        if contract_size and contract_size <= 0:
            raise Exception(f'Invalid contract size: {contract_size}')
        self._contract_size = contract_size
        if tick_size and tick_size <= 0:
            raise Exception(f'Invalid tick size: {tick_size}')
        self._tick_size = tick_size
    
    @property
    def base_ccy(self) -> str:
        return self.pair.base_ccy
    
    @property
    def quote_ccy(self) -> str:
        return self.pair.quote_ccy
    
    @property
    def contract_size(self) -> float:
        if self._contract_size is None:
            raise Exception(f'Contract size is not available for {self.instId}')
        if self.type != InstrumentType.FUTURES:
            raise Exception(f'Contract size is not available for {self.type}')
        if self._contract_size <= 0:
            raise Exception(f'Invalid contract size: {self._contract_size}')
        return self._contract_size
    
    @property
    def tick_size(self) -> float:
        if self._tick_size is None:
            raise Exception(f'Tick size is not available for {self.instId}')
        return self._tick_size
    
    def is_opened(self, close_ts: Union[SimTime, int]) -> bool:
        if self.type == 'FUTURES':
            items = self.instId.split('-')
            if len(items) != 3:
                raise Exception(f'Invalid instId: {self.instId}')
            date = datetime.strptime(items[2], '%y%m%d')
            timestamp_ms = int(date.timestamp() * 1000)
            if timestamp_ms < close_ts:
                return True
            else:
                return False
        else:
            raise Exception(f'Invalid instrument type: {self.type}')
    
    @property
    def start_ts(self) -> int:
        raise NotImplementedError
    
    @property
    def end_ts(self) -> int:
        raise NotImplementedError
    
    def __str__(self) -> str:
        return self.instId

