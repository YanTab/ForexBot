import logging
from datetime import timedelta

import pandas as pd

log = logging.getLogger("DATA")


class DataValidator:
    def __init__(self, config: dict):
        v = config["validation"]
        self._max_gap = timedelta(seconds=v["max_gap_seconds"])
        self._max_spread_pips = v["max_spread_pips"]
        self._min_spread_pips = v["min_spread_pips"]
        self._max_move_pct = v["max_price_change_pct"]
        self._tf = timedelta(minutes=config.get("timeframe", 5))

    def validate(self, df: pd.DataFrame, symbol: str, pip_size: float) -> tuple[pd.DataFrame, dict]:
        issues: list[str] = []
        issues += self._check_gaps(df)
        issues += self._check_spreads(df, pip_size)
        issues += self._check_price_moves(df)
        if issues:
            log.warning(f"[VALIDATE] {symbol} : {len(issues)} problème(s) détecté(s)")
        return df, {"valid": len(issues) == 0, "issues": issues}

    def _check_gaps(self, df: pd.DataFrame) -> list[str]:
        if len(df) < 2:
            return []
        diffs = df.index.to_series().diff().dropna()
        threshold = self._tf + self._max_gap
        gaps = diffs[diffs > threshold]
        return [f"Gap à {ts}: {dur}" for ts, dur in gaps.items()]

    def _check_spreads(self, df: pd.DataFrame, pip_size: float) -> list[str]:
        if "spread" not in df.columns or pip_size == 0:
            return []
        spread_pips = df["spread"] / pip_size
        too_wide = int((spread_pips > self._max_spread_pips).sum())
        too_narrow = int((spread_pips < self._min_spread_pips).sum())
        issues = []
        if too_wide:
            issues.append(f"{too_wide} bar(s) avec spread > {self._max_spread_pips} pips")
        if too_narrow:
            issues.append(f"{too_narrow} bar(s) avec spread < {self._min_spread_pips} pips")
        return issues

    def _check_price_moves(self, df: pd.DataFrame) -> list[str]:
        moves = df["close"].pct_change().abs() * 100
        extreme = moves[moves > self._max_move_pct].dropna()
        return [f"Mouvement extrême à {ts}: {v:.2f}%" for ts, v in extreme.items()]
