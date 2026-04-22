import pandas as pd


class MicrostructureIndicator:
    def __init__(self, config: dict):
        self._of_window = config["microstructure"]["order_flow_window"]

    def order_flow(self, df: pd.DataFrame, window: int | None = None) -> pd.Series:
        """Volume signé : positif si close > open (pression acheteuse), négatif sinon."""
        w = window or self._of_window
        direction = (df["close"] - df["open"]).apply(lambda x: 1 if x > 0 else -1)
        signed_vol = direction * df["volume"]
        return signed_vol.rolling(w).sum()

    def order_flow_latest(self, df: pd.DataFrame, window: int | None = None) -> float:
        return float(self.order_flow(df, window).iloc[-1])

    def bid_ask_imbalance(self, df: pd.DataFrame) -> pd.Series:
        """(ask - bid) / (ask + bid) normalisé — proxy de pression directionnelle."""
        if "bid" not in df.columns or "ask" not in df.columns:
            return pd.Series(0.0, index=df.index)
        mid = (df["bid"] + df["ask"]) / 2
        return (df["ask"] - df["bid"]) / mid.replace(0, float("nan"))

    def bid_ask_imbalance_latest(self, df: pd.DataFrame) -> float:
        val = self.bid_ask_imbalance(df).iloc[-1]
        return float(val) if pd.notna(val) else 0.0

    def broker_latency(self) -> float:
        """Latence broker en ms. Retourne 0.0 en simulation (mesuré par le connecteur IB en production)."""
        return 0.0
