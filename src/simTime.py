class SimTime:
    def __init__(self, start: int, end: int) -> None:
        if not isinstance(start, int) or not isinstance(end, int):
            raise ValueError("Start and end times must be integers.")
        if start >= end:
            raise ValueError("End time must be greater than start time.")
        self.__start = start
        self.__end = end
        self.__ts = start # Current timestamp

    def set(self, ts: int) -> None:
        if not isinstance(ts, int):
            raise ValueError("Timestamp must be an integer.")
        if ts < self.__start or ts > self.__end:
            raise ValueError("Timestamp must be within the simulation start and end times.")
        if ts <= self.__ts:
            raise ValueError("Timestamp must be greater than the current timestamp.")
        self.__ts = ts
    
    def add(self, ts: int) -> None:
        new_ts = self.__ts + ts
        if not isinstance(new_ts, int):
            raise ValueError("Timestamp must be an integer.")
        if new_ts < self.__start or new_ts > self.__end:
            raise ValueError("Timestamp must be within the simulation start and end times.")
        if new_ts <= self.__ts:
            raise ValueError("Timestamp must be greater than the current timestamp.")
        self.__ts = new_ts

    def __str__(self) -> str:
        return str(self.__ts)

    def __int__(self) -> int:
        return self.__ts

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