
from typing import List

from event import Event
from src.environment import Environment
from src.backtest import Backtest
from src.history import History
from src.simTime import SimTime


class World:
    def __init__(self, path: str) -> None:
        self.events: List[Event] = []
        self.path = path
        self.simTime = SimTime(0, 1)
        self.env = Environment(path, self.simTime)


    def run(self, backtest: Backtest) -> History:
        self.simTime = SimTime(backtest.start, backtest.end)
        self.env = Environment(self.path, self.simTime)
        
        history = History(backtest.hist_level)
        strategy = backtest.strategy
        eval_step = backtest.eval_step
        
        while not backtest.stop_condition(self.env):
            history.snapshot(self.env)
            
            if self.simTime >= backtest.end:
                break
            
            self.events.extend(strategy.eval(self.env))
            
            for event in self.events:
                if event.execute(self.env):
                    self.events.remove(event)
            
            self.env.eval()
            
            self.simTime.add(eval_step)
        
        return history