import logging
from datetime import timedelta

import numpy as np
import pandas as pd

log = logging.getLogger("DATA")


class DataNormaliser:
    def __init__(self, config: dict):
        self._sync_tolerance = timedelta(
            seconds=config["normalisation"]["sync_tolerance_seconds"]
        )
        self._pip_sizes: dict[str, float] = {
            i["symbol"]: i["pip_size"]
            for i in config.get("instruments", [])
        }

    def normalise(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        pip = self._pip_sizes.get(symbol, 0.0001)
        df = df.copy()
        if "spread" in df.columns:
            df["spread_pips"] = df["spread"] / pip
        df["returns"] = df["close"].pct_change()
        df["log_returns"] = np.log(df["close"] / df["close"].shift(1))
        return df

    def sync_instruments(self, dfs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        if len(dfs) <= 1:
            return dfs
        base_index = next(iter(dfs.values())).index.sort_values()
        synced: dict[str, pd.DataFrame] = {}
        for symbol, df in dfs.items():
            df_sorted = df.sort_index()
            reindexed = df_sorted.reindex(base_index, method="nearest", tolerance=self._sync_tolerance)
            dropped = int(reindexed.isnull().any(axis=1).sum())
            if dropped:
                log.warning(f"[NORMALISE] {symbol} : {dropped} bars perdus lors de la synchro")
            synced[symbol] = reindexed.dropna()
        return synced

    def to_pips(self, symbol: str, price_diff: float) -> float:
        pip = self._pip_sizes.get(symbol, 0.0001)
        return round(price_diff / pip, 1)
