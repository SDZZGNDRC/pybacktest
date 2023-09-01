import json
from src.environment import Environment

class HistLevel:
    DEBUG = 'DEBUG'
    INFO = 'INFO'

class History:
    def __init__(self, hist_level: str) -> None:
        self.hist_level = hist_level
        self.last_hash: int = -1
        self._history = []
    
    def snapshot(self, env: Environment):
        if hash(env) == self.last_hash:
            return
        
        self.last_hash = hash(env)
        self._history.append(env.as_dict())
    
    def as_dict(self) -> dict:
        return {
            'hist_level': self.hist_level,
            'history': self._history
        }
    
    def save(self, path: str) -> None:
        with open(path, 'w') as f:
            json.dump(self.as_dict(), f, indent=4)
    
    def __len__(self) -> int:
        return len(self._history)
    
    def __getitem__(self, index: int) -> dict:
        return self._history[index]