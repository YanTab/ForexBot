import logging

from .pipeline import IndicatorPipeline

log = logging.getLogger("SYSTEM")


class IndicatorHealth:
    def __init__(self, pipeline: IndicatorPipeline):
        self._pipeline = pipeline

    def check(self) -> dict:
        status = self._pipeline.health_check()
        log.info(f"[HEALTH] Indicators : {status['status']} | cache={status['cache']}")
        return status
