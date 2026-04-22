import pandas as pd


class SpreadIndicator:
    def __init__(self, config: dict):
        s = config["spread"]
        self._mean_window = s["mean_window"]
        self._multiplier = s["threshold_multiplier"]

    def current_pips(self, df: pd.DataFrame) -> float:
        """Spread instantané du dernier bar, en pips (colonne spread_pips requise)."""
        if "spread_pips" in df.columns:
            return float(df["spread_pips"].iloc[-1])
        return 0.0

    def rolling_mean(self, df: pd.DataFrame, window: int | None = None) -> pd.Series:
        w = window or self._mean_window
        col = "spread_pips" if "spread_pips" in df.columns else "spread"
        return df[col].rolling(w).mean()

    def rolling_mean_latest(self, df: pd.DataFrame, window: int | None = None) -> float:
        return float(self.rolling_mean(df, window).iloc[-1])

    def dynamic_threshold(self, df: pd.DataFrame, window: int | None = None) -> float:
        """Seuil dynamique = moyenne glissante × multiplicateur."""
        return self.rolling_mean_latest(df, window) * self._multiplier

    def is_acceptable(self, df: pd.DataFrame, max_pips: float | None = None) -> bool:
        threshold = max_pips if max_pips is not None else self.dynamic_threshold(df)
        return self.current_pips(df) <= threshold
