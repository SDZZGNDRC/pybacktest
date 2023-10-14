from typing import Dict, List, Literal, Tuple, Union
from enum import Enum
from uuid import UUID

from loguru import logger

from src.contract import ContStatus, Contract, ContRole
from src.instrument import Instrument
from src.mabidask import mabidask
from src.marketdata import MarketData
from src.markprices import MarkPrice
from src.order import Order, orderSide

class PosDirection(Enum):
    BUYLONG = 'BUYLONG'
    SELLSHORT = 'SELLSHORT'

class PosAction(Enum):
    OPEN = 'OPEN'
    CLOSE = 'CLOSE'

class PosStatus(Enum):
    INIT = 'INIT'
    OPEN = 'OPEN'
    CLOSE = 'CLOSE'

class Position:
    def __init__(self,
                inst: Instrument, 
                leverage: int,
                direction: PosDirection,
                marketData: MarketData,
                mmr: float,
                fee_rate: float,
                ) -> None:
        
        # NOTICE: ONLY support USDT(C)-based futures trading so far.
        if inst.quote_ccy not in ['USDT', 'USDC']:
            raise Exception('ONLY support USDT(C)-based futures trading so far')
        
        self._inst = inst
        if leverage <= 0:
            raise ValueError("Leverage must be greater than zero.")
        self._leverage = leverage
        self._direct = direction
        # self._marketData = marketData
        try:
            self._mkPx = marketData['markprices'][inst]
        except Exception as e:
            if 'No index files found' in str(e):
                logger.debug(f'No data files for markprice {inst}, use mabidask instead')
                self._mkPx = marketData['mabidasks'][inst]
        self._mmr = mmr
        self._fee_rate = fee_rate
        
        self._conts: List[Contract] = []
        self._margin: Dict[UUID, float] = {}
        self._loan: Dict[UUID, float] = {}
        self._open_price: Dict[UUID, float] = {}
        self._close_price: Dict[UUID, float] = {}


    def open(self, entry_price: float, entry_num: int):
        if self.STATUS == PosStatus.CLOSE:
            raise Exception("Can not call a closed position.")
        
        if entry_price <= 0:
            raise ValueError("Open price must be greater than zero.")
        
        if entry_num <= 0:
            raise ValueError("Open number must be greater than zero.")
        
        cont_role = ContRole.SELLER if self._direct == PosDirection.SELLSHORT else ContRole.BUYER
        new_conts = [Contract(self._inst, cont_role) for _ in range(entry_num)]
        margin = entry_price * self._inst.contract_size * 1 / self.leverage
        loan = entry_price * self._inst.contract_size * 1 - margin
        for cont in new_conts:
            self._open_price[cont.uuid] = entry_price
            self._margin[cont.uuid] = margin
            self._loan[cont.uuid] = loan
        self._conts.extend(new_conts)


    def profit(self, base: Literal['Mark', 'Commission'] = 'Mark') -> float:
        raise NotImplementedError


    # Unrealized Profit
    def UProfit(self, base: Literal['Mark', 'Commission'] = 'Mark') -> float:
        if base == 'Mark': # Use MarkPrice to calculate the unrealized profit
            mkPx: Union[MarkPrice, mabidask] = self._mkPx # type: ignore
            opened_conts = list(filter(lambda cont: cont.status==ContStatus.OPEN, self._conts))
            opened_AOP = sum([self._open_price[cont.uuid] for cont in opened_conts])/len(opened_conts)
            if self._direct == PosDirection.BUYLONG:
                delta = mkPx - opened_AOP
            elif self._direct == PosDirection.SELLSHORT:
                delta = opened_AOP - mkPx
            else:
                raise ValueError(f'Unknown position direction {self._direct}')
            uProfit = self.inst.contract_size * len(opened_conts) * 1 * delta
        elif base == 'Commission':
            raise NotImplementedError
        else:
            raise ValueError(f'Unknown base: {base}')

        return uProfit


    def close(self, close_price: float, close_num: int) -> float:
        # TODO: remove closed conts
        return_value = 0.0
        
        if self.STATUS == PosStatus.CLOSE:
            raise Exception("Can not call a closed position.")
        
        if close_price <= 0:
            raise ValueError("Close price must be greater than zero.")
        
        if close_num <= 0:
            raise ValueError("Close number must be greater than zero.")
        if self.OPEN_NUM - close_num < 0:
            raise ValueError(f"Position with {self.OPEN_NUM} contracts can not close {close_num} contracts")
        
        open_conts = list(filter(lambda cont: cont.status==ContStatus.OPEN, self._conts))
        for i in range(close_num):
            cont = open_conts[i]
            self._close_price[cont.uuid] = close_price
            cont.close()
            if self._direct == PosDirection.BUYLONG:
                delta_p = self._close_price[cont.uuid] - self._open_price[cont.uuid]
            else:
                delta_p = self._open_price[cont.uuid] - self._close_price[cont.uuid]
            return_value += self._margin[cont.uuid] + delta_p * self.inst.contract_size * 1
            del self._loan[cont.uuid] # Repay the loan.
            del self._margin[cont.uuid]
        
        if return_value < 0:
            raise ValueError(f'return_value({return_value}) should not be less than 0; When equal to 0, it will be Forced to liquidation')
        return return_value


    def as_dict(self) -> dict:
        return {
            'instId': self.inst.instId,
            'leverage': self.leverage,
            'direction': self.direct,
            'contracts': [cont.as_dict() for cont in self._conts],
            'margin': self._margin,
            'loan': self._loan,
            'open_price': self._open_price,
            'close_price': self._close_price,
        }


    @property
    def inst(self) -> Instrument:
        return self._inst


    @property
    def leverage(self) -> int:
        return self._leverage


    @property
    def direct(self) -> PosDirection:
        return self._direct


    @property
    def STATUS(self) -> PosStatus:
        if len(self._conts) == 0:
            return PosStatus.INIT
        elif list(filter(lambda cont: cont.status==ContStatus.OPEN, self._conts)):
            return PosStatus.OPEN
        else:
            return PosStatus.CLOSE


    @property
    def OPEN_NUM(self) -> int:
        return len([cont for cont in self._conts if cont.status == ContStatus.OPEN])


    # Average Open Price
    @property
    def AOP(self) -> float:
        return sum([self._open_price[cont.uuid] for cont in self._conts])/len(self._conts)


    # Average Close Price
    @property
    def ACP(self) -> float:
        if self.STATUS != PosStatus.CLOSE:
            raise Exception("Only closed position have ACP.")
        return sum([self._close_price[cont.uuid] for cont in self._conts])/len(self._conts)


    # Total loan of the position
    @property
    def Loan(self) -> float:
        return sum([v for v in self._loan.values()])


    # Total margin of the position
    @property
    def Margin(self) -> float:
        return sum([v for v in self._margin.values()])


    @property
    def MarginRate(self) -> float:
        mkPx: Union[MarkPrice, mabidask] = self._mkPx # type: ignore
        rate = self._mmr+self._fee_rate
        return (self.Margin+self.UProfit())/(self.inst.contract_size*self.OPEN_NUM*mkPx*rate)


    def __eq__(self, other) -> bool:
        if isinstance(other, Position) and \
            self._inst == other._inst and \
                self._direct == other._direct and \
                    self._leverage == other._leverage:
                        return True
        elif isinstance(other, Order) and \
            self._inst == other.inst and \
                self.leverage == other.leverage and \
                    (self.direct, other.side) in [
                        (PosDirection.BUYLONG, orderSide.BUYLONG), 
                        (PosDirection.SELLSHORT, orderSide.SELLSHORT),
                    ]:
                        return True
        else:
            return False


    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


    def __hash__(self) -> int:
        return hash((self.inst, self.leverage, self.direct, self._conts, self._margin))



class Positions:
    
    def __init__(self,
                 maintain_margin_rate: float,
                 fee_rate: float,
                 marketData: MarketData,
                 ) -> None:
        self._pos: List[Position] = []
        self._mmr = maintain_margin_rate
        self._fr = fee_rate
        self._marketData = marketData
        
        self.iter_index = 0


    def __get(self,
              inst: Instrument, 
              direct: PosDirection, 
              leverage: int) -> Position:
        filter_func = lambda pos: pos.inst==inst and \
                        pos.direct==direct and \
                            pos.leverage == leverage
        
        target_positions: List[Position] = list(filter(filter_func, self._pos))
        if len(target_positions) > 1: # FIXME: Remove this after debug stage.
            raise Exception(f'There are {len(target_positions)} positions for the same instrument and direction')
        
        if len(target_positions) == 0: # Create the position
            pos = Position(inst, leverage, direct, self._marketData, self._mmr, self._fr)
            self._pos.append(pos)
        else:
            pos = target_positions[0]
        if pos.STATUS == PosStatus.CLOSE: # Replace the closed position
            self._pos.remove(pos)
            pos = Position(inst, leverage, direct, self._marketData, self._mmr, self._fr)
            self._pos.append(pos)
        
        return pos


    def __clear(self) -> None:
        for pos in self._pos:
            if pos.STATUS == PosStatus.CLOSE:
                self._pos.remove(pos)


    def open(self, 
             inst: Instrument, 
             direct: PosDirection, 
             leverage: int, 
             price: float, 
             num: int) -> None:
        self.__get(inst, direct, leverage).open(price, num)


    def close(self,
              inst: Instrument, 
              direct: PosDirection, 
              leverage: int, 
              price: float, 
              num: int) -> float:
        return_value = self.__get(inst, direct, leverage).close(price, num)
        self.__clear()
        return return_value


    def __getitem__(self, key: Tuple[Instrument, PosDirection, int]) -> Position:
        return self.__get(key[0], key[1], key[2])


    def __hash__(self) -> int:
        return hash(tuple(self._pos))


    def __iter__(self):
        self.iter_index = 0
        return self


    def __next__(self) -> Position:
        if self.iter_index >= len(self._pos):
            raise StopIteration
        value = self._pos[self.iter_index]
        self.iter_index += 1
        return value

    def as_dict(self) -> list:
        return [pos.as_dict() for pos in self._pos]

