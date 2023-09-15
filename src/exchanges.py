
from typing import Dict, List
from src.contract import ContRole
from src.instrument import InstType
from src.marketdata import MarketData
from src.order import Order, orderAction, orderSide, orderType
from src.positions import PosDirection, Positions
from src.simTime import SimTime

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
    def __init__(self, data_path: str, simTime: SimTime, initial_balance: Dict[str, float] = {'USDT': 100, 'USDC': 100}, max_interval: int = 2000) -> None:
        self.simTime = simTime
        self.marketData = MarketData(simTime, data_path, max_interval)
        self.orders: List[Order] = []
        self.balance: Balance = Balance(initial_balance)
        self.positions: Positions = Positions()
        
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
    
    
    def eval(self) -> None:
        # TODO: Should try to make delivery of the contracts.
        # TODO: Should simulate the delay of network.
        if len(self.orders) == 0:
            return
        
        for order in self.orders:
            if order.status == 'OPEN':
                self.__execute(order)
    
    
    def add_order(self, order: Order) -> None:
        if order.status != 'OPEN':
            raise Exception(f'Order status must be OPEN, not {order.status}')
        
        self.orders.append(order)
    
    def __execute(self, order: Order):
        if order.orderType == orderType.LIMIT:
            self.__execute_limit_order(order)
        elif order.orderType == orderType.MARKET:
            self.__execute_market_order(order)
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
        instId = str(order.inst.instId)
        if order.side == orderSide.BUYLONG:
            for bl in self.marketData['books'][instId]['ask']:
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
            for bl in self.marketData['books'][instId]['bid']:
                if order.leftAmount == 0:
                    break
                exec_amount = min(order.leftAmount, bl.amount)
                if exec_amount > self.balance[order.base_ccy]:
                    order.insufficient()
                    print(f'[{self.marketData.simTime}] Insufficient balance: {self.balance[order.base_ccy]} < {exec_amount}')
                    break
                
                self.balance[order.base_ccy] -= exec_amount
                get_amount = exec_amount * bl.price
                self.balance[order.quote_ccy] += get_amount * (1 - fee_rate)
                order.exe(bl.price, exec_amount, get_amount * fee_rate)
        else:
            raise Exception(f'Unsupported order side: {order.side}')
    
    def __execute_market_order_futures(self, order: Order):
        # NOTICE: ONLY support `USDT/USDC Contracts`.
        
        fee_rate = self.transaction_fee['FUTURES']['MarketOrder']['TAKER']
        instId = order.inst.instId
        
        if order.action == orderAction.OPEN:
            if order.side == orderSide.BUYLONG:
                pos_direct = PosDirection.BUYLONG
                bls = self.marketData['books'][instId]['ask'] # open long(buy) -> ask
            elif order.side == orderSide.SELLSHORT:
                pos_direct = PosDirection.SELLSHORT
                bls = self.marketData['books'][instId]['bid'] # open short(sell) -> bid
            else:
                raise Exception(f'Unsupported order side: {order.side}')
            
            for bl in bls:
                if order.leftAmount == 0:
                    break
                
                exec_amount = min(order.leftAmount, bl.amount)
                fee = bl.price * exec_amount * order.inst.contract_size * fee_rate # FIXME: Haven't consider the contract multiplier here
                margin = bl.price * exec_amount / order.leverage
                borrow = bl.price * exec_amount - margin # Borrowed amount.
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
                bls = self.marketData['books'][instId]['bid'] # close long(sell) -> bid
            elif order.side == orderSide.SELLSHORT:
                pos_direct = PosDirection.SELLSHORT
                bls = self.marketData['books'][instId]['ask'] # close short(buy) -> aks
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
                if self.balance[order.quote_ccy] - fee < 0:
                    order.insufficient()
                    break
                
                net_profit = self.positions.close(
                    order.inst, pos_direct, 
                    order.leverage, 
                    bl.price, int(exec_amount)
                )
                self.balance[order.quote_ccy] += net_profit - fee
                
                order.exe(bl.price, exec_amount, fee)


    def __hash__(self) -> int:
        return hash((tuple(self.orders), self.balance))
    
    def as_dict(self) -> dict:
        return {
            'simTime': int(self.simTime),
            'orders': [o.as_dict() for o in self.orders],
            'balance': self.balance.as_dict(),
            'positions': self.positions.as_dict()
        }
    
