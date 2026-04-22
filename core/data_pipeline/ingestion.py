from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import logging

import numpy as np
import pandas as pd

log = logging.getLogger("DATA")

COLUMNS = ["open", "high", "low", "close", "volume", "bid", "ask", "spread"]


class DataSource(ABC):
    @abstractmethod
    def connect(self) -> bool: ...

    @abstractmethod
    def disconnect(self): ...

    @abstractmethod
    def fetch_bars(self, symbol: str, count: int) -> pd.DataFrame: ...

    @abstractmethod
    def is_connected(self) -> bool: ...


class SimulationSource(DataSource):
    def __init__(self, config: dict):
        self._config = config
        self._connected = False
        seed = config.get("simulation", {}).get("random_seed", 42)
        self._rng = np.random.default_rng(seed=seed)

    def connect(self) -> bool:
        self._connected = True
        log.info("[INGESTION] SimulationSource connected")
        return True

    def disconnect(self):
        self._connected = False
        log.info("[INGESTION] SimulationSource disconnected")

    def is_connected(self) -> bool:
        return self._connected

    def fetch_bars(self, symbol: str, count: int = 100) -> pd.DataFrame:
        instruments = self._config.get("instruments", [])
        instr = next((i for i in instruments if i["symbol"] == symbol), None)
        if instr is None:
            raise ValueError(f"Unknown symbol: {symbol}")

        base = instr["base_price"]
        pip = instr["pip_size"]
        sim = self._config.get("simulation", {})
        vol_pct = sim.get("daily_volatility_pct", 0.5) / 100
        spread_pips = sim.get("spread_pips", 0.2)
        tf = self._config.get("timeframe", 5)

        periods_per_day = (24 * 60) / tf
        bar_vol = vol_pct * base / (periods_per_day ** 0.5)

        returns = self._rng.normal(0, bar_vol, count)
        closes = base + np.cumsum(returns)
        opens = np.empty(count)
        opens[0] = base
        opens[1:] = closes[:-1]
        noise_h = abs(self._rng.normal(0, bar_vol * 0.5, count))
        noise_l = abs(self._rng.normal(0, bar_vol * 0.5, count))
        highs = np.maximum(opens, closes) + noise_h
        lows = np.minimum(opens, closes) - noise_l
        volumes = self._rng.integers(100, 2000, count).astype(float)

        spread = spread_pips * pip
        bids = closes - spread / 2
        asks = closes + spread / 2

        end = datetime.utcnow().replace(second=0, microsecond=0)
        end -= timedelta(minutes=end.minute % tf)
        timestamps = [end - timedelta(minutes=tf * i) for i in range(count - 1, -1, -1)]

        return pd.DataFrame(
            {"open": opens, "high": highs, "low": lows, "close": closes,
             "volume": volumes, "bid": bids, "ask": asks, "spread": asks - bids},
            index=pd.DatetimeIndex(timestamps, name="timestamp"),
        )


class IBSource(DataSource):
    """Stub — implémenté dans broker/interactive_brokers/connector.py."""

    def connect(self) -> bool:
        raise NotImplementedError("IBSource : connecteur IB non encore activé. Utiliser mode=simulation.")

    def disconnect(self): ...

    def fetch_bars(self, symbol: str, count: int = 100) -> pd.DataFrame:
        raise NotImplementedError

    def is_connected(self) -> bool:
        return False
