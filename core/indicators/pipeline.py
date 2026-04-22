import logging
from pathlib import Path

import pandas as pd
import yaml

from .cache import IndicatorCache
from .microstructure import MicrostructureIndicator
from .spread import SpreadIndicator
from .volatility import VolatilityIndicator
from .zscore import ZScoreIndicator

log = logging.getLogger("DATA")

_CONFIG_PATH = Path(__file__).parent / "config.yaml"

_MIN_BARS = 25  # minimum requis pour tous les indicateurs


class IndicatorPipeline:
    def __init__(self, config_path: Path | None = None):
        cfg_path = config_path or _CONFIG_PATH
        self._config = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
        self._cache = IndicatorCache(self._config["cache"]["maxsize"])
        self._zscore = ZScoreIndicator(self._config)
        self._volatility = VolatilityIndicator(self._config)
        self._spread = SpreadIndicator(self._config)
        self._micro = MicrostructureIndicator(self._config)

    def compute(self, symbol: str, df: pd.DataFrame) -> dict:
        if len(df) < _MIN_BARS:
            log.warning(f"[INDICATORS] {symbol} : seulement {len(df)} bars (minimum {_MIN_BARS})")
            return {}

        last_bar = df.index[-1]

        def cached(indicator: str, window: int, fn):
            key = IndicatorCache.make_key(symbol, indicator, window, last_bar)
            value = self._cache.get(key)
            if value is None:
                value = fn()
                self._cache.set(key, value)
            return value

        zw = self._config["zscore"]["window"]
        aw = self._config["volatility"]["atr_window"]
        gw = self._config["volatility"]["gk_window"]
        rw = self._config["volatility"]["realized_window"]
        sw = self._config["spread"]["mean_window"]
        mw = self._config["microstructure"]["order_flow_window"]

        return {
            "zscore":             cached("zscore",        zw, lambda: self._zscore.latest(df["close"])),
            "atr":                cached("atr",           aw, lambda: self._volatility.atr(df)),
            "volatility_gk":      cached("vol_gk",        gw, lambda: self._volatility.garman_klass(df)),
            "volatility_realized":cached("vol_realized",  rw, lambda: self._volatility.realized(df)),
            "spread_current":     cached("spread_cur",     0, lambda: self._spread.current_pips(df)),
            "spread_mean":        cached("spread_mean",   sw, lambda: self._spread.rolling_mean_latest(df)),
            "spread_threshold":   cached("spread_thresh", sw, lambda: self._spread.dynamic_threshold(df)),
            "order_flow":         cached("order_flow",    mw, lambda: self._micro.order_flow_latest(df)),
            "bid_ask_imbalance":  cached("ba_imbalance",   0, lambda: self._micro.bid_ask_imbalance_latest(df)),
            "broker_latency_ms":  cached("latency",        0, lambda: self._micro.broker_latency()),
        }

    def compute_all(self, dfs: dict[str, pd.DataFrame]) -> dict[str, dict]:
        return {symbol: self.compute(symbol, df) for symbol, df in dfs.items()}

    def health_check(self) -> dict:
        return {
            "component": "indicators",
            "status": "ok",
            "cache": self._cache.stats(),
        }
