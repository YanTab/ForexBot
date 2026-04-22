import pandas as pd


class ZScoreIndicator:
    def __init__(self, config: dict):
        self._window = config["zscore"]["window"]

    def series(self, prices: pd.Series, window: int | None = None) -> pd.Series:
        w = window or self._window
        mean = prices.rolling(w).mean()
        std = prices.rolling(w).std()
        return (prices - mean) / std.replace(0, float("nan"))

    def latest(self, prices: pd.Series, window: int | None = None) -> float:
        result = self.series(prices, window)
        val = result.iloc[-1]
        return float(val) if pd.notna(val) else 0.0

    def is_extreme(self, prices: pd.Series, threshold: float = 2.0) -> bool:
        return abs(self.latest(prices)) >= threshold
