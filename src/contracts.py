
class Contract:
    def __init__(self, pair: str, start: int, end: int, entry_ts: int, direction: str, leverage: int, margin: float) -> None:
        self.pair = str(pair)

        if start <= 0 or end <= 0:
            raise ValueError("Timestamp must be greater than zero.")
        if start >= end:
            raise ValueError("Start timestamp must be less than end timestamp.")
        self.start = int(start)
        self.end = int(end)
        
        if entry_ts <= 0:
            raise ValueError("Entry timestamp must be greater than zero.")
        if entry_ts < start or entry_ts >= end:
            raise ValueError("Entry timestamp must be between start and end timestamps.")
        self.entry_ts = int(entry_ts)
        
        self.direction = str(direction)

        if not isinstance(leverage, int):
            raise TypeError("Leverage must be an integer.")
        if leverage <= 0:
            raise ValueError("Leverage must be greater than zero.")
        self.leverage = leverage
        
        if margin < 0:
            raise ValueError("Margin must be greater than or equal to zero.")
        self.margin = float(margin)

        self.exit_ts: float = 0.0
        self.status = 'OPEN'