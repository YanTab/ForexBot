from collections import OrderedDict

import pandas as pd


class IndicatorCache:
    def __init__(self, maxsize: int = 256):
        self._store: OrderedDict = OrderedDict()
        self._maxsize = maxsize
        self._hits = 0
        self._misses = 0

    @staticmethod
    def make_key(symbol: str, indicator: str, window: int, last_bar: pd.Timestamp) -> str:
        return f"{symbol}|{indicator}|{window}|{last_bar.isoformat()}"

    def get(self, key: str):
        if key in self._store:
            self._store.move_to_end(key)
            self._hits += 1
            return self._store[key]
        self._misses += 1
        return None

    def set(self, key: str, value):
        if key in self._store:
            self._store.move_to_end(key)
        else:
            if len(self._store) >= self._maxsize:
                self._store.popitem(last=False)
        self._store[key] = value

    def invalidate_symbol(self, symbol: str):
        keys = [k for k in self._store if k.startswith(f"{symbol}|")]
        for k in keys:
            del self._store[k]

    def clear(self):
        self._store.clear()

    def stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "size": len(self._store),
            "maxsize": self._maxsize,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total, 3) if total else 0.0,
        }
