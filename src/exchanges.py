
from pathlib import Path
from typing import Dict, List, Literal
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

from loguru import logger
from src.IdxPrice import IdxPrices
from src.books import Books
from src.instrument import InstType
from src.marketdata import MarketData
from src.order import Order, orderAction, orderSide, orderStatus, orderType
from src.positions import PosDirection, PosStatus, Positions
from src.simTime import SimTime

colorama_init()

class Balance:
    def __init__(self, initial_balance: Dict[str, float]) -> None:
        self._balance: Dict[str, float] = {}
        for ccy, value in initial_balance.items():
            self[ccy] = value
    
    
    def __getitem__(self, ccy: str) -> float:
        if not isinstance(ccy, str):
            raise TypeError("Currency must be a string.")
        
        if ccy not in self._balance:
            self._balance[ccy] = 0
        return self._balance[ccy]
    
    
    def __setitem__(self, ccy: str, value: float) -> None:
        if not isinstance(ccy, str):
            raise TypeError("Currency must be a string.")
        
        if value < 0:
            raise ValueError("Balance must be greater than or equal to zero.")
        
        self._balance[ccy] = float(value)
    
    def __contains__(self, ccy: str) -> bool:
        return ccy in self._balance

    def __hash__(self) -> int:
        return hash(tuple(self._balance.items()))

    def as_dict(self) -> dict:
        return self._balance.copy()


class Exchange:
    def __init__(self, data_path: Path, simTime: SimTime, initial_balance: Dict[str, float] = {'USDT': 100, 'USDC': 100}, max_interval: int = 2000) -> None:
        self.simTime = simTime
        self.marketData = MarketData(simTime, data_path, max_interval)
        self.orders: List[Order] = []
        self.balance: Balance = Balance(initial_balance)
        
        self.transaction_fee = {
            'SPOT': {
                'MarketOrder': {
                    'MAKER': 0.0008,
                    'TAKER': 0.0010,
                }
            },
            'FUTURES': {
                'MarketOrder': {
                    'MAKER': 0.0002,
                    'TAKER': 0.0005,
                }
            },
        }
        self.delivery_fee_rate = 0.0001
        # NOTICE: The mmr is not the same for all contracts and not the same for different size of positions.
        #         Select a fixed value for simplicity when testing.
        # ! make sure to complete the mmr mechanism in the future.
        self.mmr = 0.004    # come from(maybe need to login): https://www.okx.com/cn/trade-market/position/futures
        self.positions: Positions = Positions(
            self.mmr, 
            self.transaction_fee['FUTURES']['MarketOrder']['TAKER'], 
            self.marketData,
        )
    
    def eval(self) -> None:
        # TODO: Should simulate the delay of network.
        
        self.liquidation()
        self.delivery()
        
        # execute orders
        for order in self.orders:
            if order.status == orderStatus.OPEN:
                self.__execute(order)


    def liquidation(self) -> None:
        for pos in filter(lambda pos: pos.STATUS == PosStatus.OPEN, self.positions):
            if pos.MarginRate <= 1.0:
                logger.debug(f'[{self.simTime}] {Fore.RED}Occurred liquidation at {pos.inst}{Style.RESET_ALL}')
                logger.debug(f'MarginRate: {pos.MarginRate}')
                logger.debug(f'Margin: {pos.Margin}')
                logger.debug(f'UProfit: {pos.UProfit()}')
                logger.debug(f'pos.mkPx: {pos._mkPx}')
                logger.debug(f'pos.leverage: {pos.leverage}')
                logger.debug(f'pos.OPEN_NUM: {pos.OPEN_NUM}')
                logger.debug(f'pos.direct: {pos.direct}')
                if pos.direct == PosDirection.BUYLONG:
                    order_side = orderSide.BUYLONG
                else:
                    order_side = orderSide.SELLSHORT
                
                liquidate_order = Order(
                    pos.inst,
                    orderType.MARKET,
                    order_side,
                    self.simTime,
                    pos.OPEN_NUM,
                    leverage=pos.leverage,        # ? What is the leverage of the liquidation order?
                    action=orderAction.CLOSE
                )
                self.__execute(liquidate_order)
                logger.debug(f'AOP: {pos.AOP}')
                logger.debug(f'ACP: {pos.ACP}')
                logger.debug(f'ask: {pos._mkPx._asks[0].price}')    # type: ignore
                logger.debug(f'bid: {pos._mkPx._bids[0].price}')    # type: ignore


    def delivery(self, base: Literal['IndexPrice', 'TradePrice'] = 'IndexPrice') -> None:
        # NOTICE: Due to the lack of IndexPrice for most cases, 
        #         TradePrice is introduced as a substitute for the delivery price.

        if base == 'IndexPrice':
            basePxs: IdxPrices = self.marketData['indexprices'] # type: ignore
        else:
            raise NotImplementedError
        opened_orders = [
            order for order in self.orders if order.status == orderStatus.OPEN
        ]
        for pos in self.positions:
            if pos.inst.end_ts <= self.simTime:
                logger.debug(f'[{self.simTime}] Occurred delivery at {pos.inst}')
                fee = basePxs[pos.inst].now*pos.OPEN_NUM* \
                    pos.inst.contract_size*self.delivery_fee_rate
                self.balance[pos.inst.quote_ccy] += pos.close(basePxs[pos.inst].now, pos.OPEN_NUM)
                self.balance[pos.inst.quote_ccy] -= fee

                # Remove all Unfulfilled orders.
                for order in opened_orders:
                    if order == pos:
                        self.orders.remove(order)


    def add_order(self, order: Order) -> None:
        if order.status != orderStatus.OPEN:
            raise Exception(f'Order status must be orderStatus.OPEN, instead of {order.status}')
        
        self.orders.append(order)


    def __execute(self, order: Order):
        if order.orderType == orderType.LIMIT:
            self.__execute_limit_order(order)
        elif order.orderType == orderType.MARKET:
            self.__execute_market_order(order)
            logger.debug(f'[{self.simTime}] executed {order}')
            logger.debug(f'balance: {self.balance.as_dict()}')
        else:
            raise Exception(f'Unsupported order type: {order.orderType}')


    def __execute_limit_order(self, order: Order):
        raise NotImplementedError()


    def __execute_market_order(self, order: Order):
        if order.inst.type == InstType.SPOT:
            self.__execute_market_order_spot(order)
        elif order.inst.type == InstType.FUTURES:
            if not order.inst.quote_ccy in ['USDT', 'USDC']:
                raise Exception(f'Unsupported quote currency: {order.inst.quote_ccy} for futures')
            self.__execute_market_order_futures(order)
        elif order.inst.type == InstType.SWAP:
            raise NotImplementedError()
        else:
            raise Exception(f'Unsupported instrument type: {order.inst.type}')


    def __execute_market_order_spot(self, order: Order):
        fee_rate = self.transaction_fee['SPOT']['MarketOrder']['TAKER']
        inst = order.inst
        books: Books = self.marketData['books'] # type: ignore
        if order.side == orderSide.BUYLONG:
            for bl in books[inst]['ask']:
                if order.leftAmount == 0:
                    break
                
                exec_amount = min(order.leftAmount, bl.amount)
                cost = bl.price * exec_amount
                if cost > self.balance[order.quote_ccy]:
                    order.insufficient()
                    print(f'[{self.marketData.simTime}] Insufficient balance: {self.balance[order.quote_ccy]} < {cost}')
                    break
                
                self.balance[order.quote_ccy] -= cost
                self.balance[order.base_ccy] += exec_amount * (1 - fee_rate)
                order.exe(bl.price, exec_amount, exec_amount * fee_rate)
        elif order.side == orderSide.SELLSHORT:
            for bl in books[inst]['bid']:
                if order.leftAmount == 0:
                    break
                exec_amount = min(order.leftAmount, bl.amount)
                if order.leftAmount > self.balance[order.base_ccy]:
                    order.insufficient()
                    print(f'[{self.marketData.simTime}] Insufficient balance: {self.balance[order.base_ccy]} < {exec_amount}')
                    break
                
                self.balance[order.base_ccy] -= exec_amount
                get_amount = exec_amount * bl.price
                self.balance[order.quote_ccy] += get_amount * (1 - fee_rate)
                order.exe(bl.price, exec_amount, get_amount * fee_rate)
            if order.leftAmount > 0:
                order.insufficient()
                logger.warning(f'[{self.simTime}] Insufficient liquidity for {order}')
        else:
            raise Exception(f'Unsupported order side: {order.side}')



    def __execute_market_order_futures(self, order: Order):
        # NOTICE: ONLY support `USDT/USDC Contracts`.
        
        fee_rate = self.transaction_fee['FUTURES']['MarketOrder']['TAKER']
        inst = order.inst
        books: Books = self.marketData['books'] # type: ignore
        if order.action == orderAction.OPEN:
            if order.side == orderSide.BUYLONG:
                pos_direct = PosDirection.BUYLONG
                bls = books[inst]['ask'] # open long(buy) -> ask
            elif order.side == orderSide.SELLSHORT:
                pos_direct = PosDirection.SELLSHORT
                bls = books[inst]['bid'] # open short(sell) -> bid
            else:
                raise Exception(f'Unsupported order side: {order.side}')
            
            for bl in bls:
                if order.leftAmount == 0:
                    break
                
                exec_amount = min(order.leftAmount, bl.amount)
                fee = bl.price * exec_amount * order.inst.contract_size * fee_rate # FIXME: Haven't consider the contract multiplier here
                margin = bl.price * exec_amount * order.inst.contract_size / order.leverage
                cost = margin + fee # total cost
                if cost > self.balance[order.quote_ccy]:
                    order.insufficient()
                    print(f'[{self.marketData.simTime}] Insufficient balance: {self.balance[order.quote_ccy]} < {cost}')
                    break
                
                self.positions.open(
                    order.inst, pos_direct, 
                    order.leverage, 
                    bl.price, int(exec_amount)
                )
                
                # Deducting
                self.balance[order.quote_ccy] -= cost
                order.exe(bl.price, exec_amount, fee)
        elif order.action == orderAction.CLOSE:
            if order.side == orderSide.BUYLONG:
                pos_direct = PosDirection.BUYLONG
                bls = books[inst]['bid'] # close long(sell) -> bid
            elif order.side == orderSide.SELLSHORT:
                pos_direct = PosDirection.SELLSHORT
                bls = books[inst]['ask'] # close short(buy) -> aks
            else:
                raise Exception(f'Unsupported order side: {order.side}')
            
            for bl in bls:
                if order.leftAmount == 0:
                    break
                
                exec_amount = min(order.leftAmount, bl.amount)
                fee = bl.price * exec_amount * order.inst.contract_size * fee_rate
                
                # NOTICE: The fee is only deducted from the balance; 
                # when the balance cannot cover the fee, 
                # the operation cannot be carried out, regardless of the income.
                # ! FIXME: We should consider the fee is not enough where the position is closed because liquidation.
                if self.balance[order.quote_ccy] - fee < 0:
                    order.insufficient()
                    break
                
                return_value = self.positions.close(
                    order.inst, pos_direct, 
                    order.leverage, 
                    bl.price, int(exec_amount)
                )
                logger.debug(f'returned: {return_value-fee}')
                self.balance[order.quote_ccy] += return_value - fee
                
                order.exe(bl.price, exec_amount, fee)
        else: 
            raise Exception(f'Invalid order action: {order.action}')


    def __hash__(self) -> int:
        return hash((tuple(self.orders), self.balance, self.positions))
    
    def as_dict(self) -> dict:
        return {
            'simTime': int(self.simTime),
            'orders': [o.as_dict() for o in self.orders],
            'balance': self.balance.as_dict(),
            'positions': self.positions.as_dict()
        }
    
