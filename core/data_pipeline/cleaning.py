import logging

import pandas as pd

log = logging.getLogger("DATA")


class DataCleaner:
    def __init__(self, config: dict):
        c = config["cleaning"]
        self._zscore_threshold = c["outlier_zscore_threshold"]
        self._max_null_ratio = c["max_null_ratio"]

    def clean(self, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        df, null_report = self._handle_nulls(df)
        df, outlier_report = self._remove_outliers(df)
        return df, {**null_report, **outlier_report}

    def _handle_nulls(self, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        null_ratio = float(df.isnull().mean().max())
        if null_ratio > self._max_null_ratio:
            log.warning(f"[CLEAN] Null ratio élevé : {null_ratio:.3f}")
        df = df.ffill().dropna()
        return df, {"null_ratio": round(null_ratio, 4)}

    def _remove_outliers(self, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        changes = df["close"].pct_change().abs()
        std = changes.std()
        if std == 0 or pd.isna(std):
            return df, {"outliers_removed": 0}
        zscore = (changes - changes.mean()) / std
        mask = zscore.abs() < self._zscore_threshold
        mask.iloc[0] = True  # première ligne toujours conservée (pct_change NaN)
        removed = int((~mask).sum())
        if removed:
            log.warning(f"[CLEAN] {removed} outlier(s) supprimé(s)")
        return df.loc[mask], {"outliers_removed": removed}
