import logging
from pathlib import Path

import pandas as pd
import yaml

from .cleaning import DataCleaner
from .ingestion import DataSource, IBSource, SimulationSource
from .normalisation import DataNormaliser
from .validation import DataValidator

log = logging.getLogger("DATA")

_CONFIG_PATH = Path(__file__).parent / "config.yaml"


class DataPipeline:
    def __init__(self, config_path: Path | None = None, source: DataSource | None = None):
        cfg_path = config_path or _CONFIG_PATH
        self._config = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
        self._source = source or self._build_source()
        self._cleaner = DataCleaner(self._config)
        self._validator = DataValidator(self._config)
        self._normaliser = DataNormaliser(self._config)
        self._cache: dict[str, pd.DataFrame] = {}

    def connect(self) -> bool:
        ok = self._source.connect()
        if ok:
            log.info("[PIPELINE] Source de données connectée")
        return ok

    def disconnect(self):
        self._source.disconnect()

    def get_data(self, symbol: str, count: int = 100) -> pd.DataFrame | None:
        try:
            raw = self._source.fetch_bars(symbol, count)
            cleaned, _ = self._cleaner.clean(raw)
            pip_size = self._pip_size(symbol)
            validated, v = self._validator.validate(cleaned, symbol, pip_size)
            normalised = self._normaliser.normalise(validated, symbol)
            self._cache[symbol] = normalised
            log.debug(f"[PIPELINE] {symbol} : {len(normalised)} bars | valid={v['valid']}")
            return normalised
        except Exception as exc:
            log.error(f"[PIPELINE] Erreur sur {symbol} : {exc}")
            return None

    def get_all(self, count: int = 100) -> dict[str, pd.DataFrame]:
        symbols = [i["symbol"] for i in self._config.get("instruments", [])]
        dfs = {s: df for s in symbols if (df := self.get_data(s, count)) is not None}
        return self._normaliser.sync_instruments(dfs)

    def health_check(self) -> dict:
        return {
            "connected": self._source.is_connected(),
            "mode": self._config.get("mode"),
            "symbols_cached": list(self._cache.keys()),
        }

    def _pip_size(self, symbol: str) -> float:
        instruments = self._config.get("instruments", [])
        instr = next((i for i in instruments if i["symbol"] == symbol), None)
        return instr["pip_size"] if instr else 0.0001

    def _build_source(self) -> DataSource:
        mode = self._config.get("mode", "simulation")
        if mode == "simulation":
            return SimulationSource(self._config)
        if mode == "production":
            return IBSource()
        raise ValueError(f"Mode inconnu : {mode}. Utiliser 'simulation' ou 'production'.")
