from environment import Environment
from order import Order

class Event:
    def __init__(self, ts: int) -> None:
        self.ts = ts

    def execute(self, env) -> bool:
        raise NotImplementedError

class CreateEvent(Event):
    def __init__(self, ts: int, exchange: str, order: Order) -> None:
        super().__init__(ts)
        self.exchange = exchange
        self.order = order
    
    def execute(self, env: Environment) -> bool:
        env['exchanges'][self.exchange].add_order(self.order)
        return True


class CancelOrder(Event):
    def __init__(self, ts: int, uuid: str) -> None:
        super().__init__(ts)
        self.uuid = uuid

