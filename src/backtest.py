from typing import Callable, List, Optional
from src.strategy import Strategy
from src.environment import Environment

class Backtest:
    def __init__(self,
                strategy: Strategy,
                start: int,
                end: int,
                hist_level: str,
                exchanges: List[str],
                eval_step: int = 1000,
                stop_condition: Optional[Callable[[Environment], bool]] = None,
                ) -> None:
        self.strategy = strategy

        if start >= end:
            raise ValueError("Start time must be before end time")
        self.start = int(start)
        self.end = int(end)
        self.stop_condition = stop_condition
        self.hist_level = hist_level
        self.exchanges = exchanges

        if eval_step <= 0:
            raise ValueError("Evaluation step must be a positive integer")
        self.eval_step = int(eval_step)