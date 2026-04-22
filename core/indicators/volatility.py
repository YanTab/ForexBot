import numpy as np
import pandas as pd


class VolatilityIndicator:
    def __init__(self, config: dict):
        v = config["volatility"]
        self._atr_window = v["atr_window"]
        self._gk_window = v["gk_window"]
        self._realized_window = v["realized_window"]

    # ── ATR ──────────────────────────────────────────────────────────────────

    def atr_series(self, df: pd.DataFrame, window: int | None = None) -> pd.Series:
        w = window or self._atr_window
        prev_close = df["close"].shift(1)
        tr = pd.concat([
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ], axis=1).max(axis=1)
        return tr.ewm(span=w, adjust=False).mean()

    def atr(self, df: pd.DataFrame, window: int | None = None) -> float:
        return float(self.atr_series(df, window).iloc[-1])

    # ── Garman-Klass ─────────────────────────────────────────────────────────

    def garman_klass_series(self, df: pd.DataFrame, window: int | None = None) -> pd.Series:
        w = window or self._gk_window
        log_hl = np.log(df["high"] / df["low"])
        log_co = np.log(df["close"] / df["open"])
        gk = 0.5 * log_hl ** 2 - (2 * np.log(2) - 1) * log_co ** 2
        return gk.rolling(w).mean().apply(lambda x: np.sqrt(max(x, 0)))

    def garman_klass(self, df: pd.DataFrame, window: int | None = None) -> float:
        return float(self.garman_klass_series(df, window).iloc[-1])

    # ── Realized volatility ───────────────────────────────────────────────────

    def realized_series(self, df: pd.DataFrame, window: int | None = None) -> pd.Series:
        w = window or self._realized_window
        log_ret = np.log(df["close"] / df["close"].shift(1))
        return (log_ret ** 2).rolling(w).sum().apply(np.sqrt)

    def realized(self, df: pd.DataFrame, window: int | None = None) -> float:
        return float(self.realized_series(df, window).iloc[-1])

    # ── Régime de volatilité ──────────────────────────────────────────────────

    def regime(self, df: pd.DataFrame, low_threshold: float, high_threshold: float) -> str:
        """Retourne 'low' | 'normal' | 'high' selon l'ATR courant."""
        current = self.atr(df)
        if current < low_threshold:
            return "low"
        if current > high_threshold:
            return "high"
        return "normal"
