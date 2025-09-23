import pandas as pd


class SimTime:
    def __init__(self, start: int, end: int) -> None:
        if not isinstance(start, int) or not isinstance(end, int):
            raise ValueError(f"Start {start} and end time {end} must be integers.")
        if start >= end:
            raise ValueError(f"End time {end} must be greater than start time {start}.")
        self.__start = start
        self.__end = end
        self.__ts = start # Current timestamp

    def set(self, ts: int) -> None:
        if not isinstance(ts, int):
            raise ValueError(f"Timestamp {ts} must be an integer.")
        if ts < self.__start or ts > self.__end:
            raise ValueError(f"Timestamp {ts} must be within the simulation start {self.__start} and end time {self.__end}.")
        if ts <= self.__ts:
            raise ValueError(f"Timestamp {ts} must be greater than the current timestamp {self.__ts}.")
        self.__ts = ts
    
    def add(self, ts: int) -> None:
        new_ts = self.__ts + ts
        if not isinstance(new_ts, int):
            raise ValueError(f"Timestamp {new_ts} must be an integer.")
        if not (self.__start <= new_ts <= self.__end):
            new_ts = self.__end
        if new_ts <= self.__ts:
            raise ValueError(f"Timestamp {new_ts} must be greater than the current timestamp {self.__ts}.")
        self.__ts = new_ts

    @property
    def start(self) -> int:
        return self.__start

    @property
    def end(self) -> int:
        return self.__end

    def to_Timestamp(self) -> pd.Timestamp:
        return pd.Timestamp(self.__ts, unit='ms')

    def __str__(self) -> str:
        return str(self.__ts)

    def __int__(self) -> int:
        return self.__ts

    def __add__(self, other):
        return self.__ts+int(other)

    def __sub__(self, other):
        return self.__ts-int(other)

    def __float__(self) -> float:
        return float(self.__ts)
    
    def __gt__(self, other) -> bool:
        return self.__ts > int(other)
    
    def __ge__(self, other) -> bool:
        return self.__ts >= int(other)
    
    def __lt__(self, other) -> bool:
        return self.__ts < int(other)
    
    def __le__(self, other) -> bool:
        return self.__ts <= int(other)

    def __eq__(self, other) -> bool:
        return self.__ts == int(other)

    def __ne__(self, other) -> bool:
        return self.__ts != int(other)