
from typing import List

from src.event import Event
from src.environment import Environment
from src.backtest import Backtest
from src.history import History
from src.simTime import SimTime


class World:
    def __init__(self, path: str, max_interval: int = 2000) -> None:
        self.events: List[Event] = []
        self.path = path
        self.simTime = SimTime(0, 1)
        self.env = None
        self.max_interval = max_interval


    def run(self, backtest: Backtest) -> History:
        self.simTime = SimTime(backtest.start, backtest.end)
        self.env = Environment(self.path, self.simTime, self.max_interval)
        
        history = History(backtest.hist_level)
        strategy = backtest.strategy
        eval_step = backtest.eval_step
        
        while True:
            history.snapshot(self.env)
            
            if backtest.stop_condition != None and backtest.stop_condition(self.env):
                break
            
            if self.simTime >= backtest.end:
                break
            
            self.events.extend(strategy.eval(self.env))
            
            for event in self.events:
                if event.execute(self.env):
                    self.events.remove(event)
            
            self.env.eval()
            
            self.simTime.add(eval_step)
        
        return history