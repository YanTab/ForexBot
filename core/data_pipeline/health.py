import logging

from .pipeline import DataPipeline

log = logging.getLogger("SYSTEM")


class PipelineHealth:
    def __init__(self, pipeline: DataPipeline):
        self._pipeline = pipeline

    def check(self) -> dict:
        status = self._pipeline.health_check()
        ok = status["connected"]
        log.info(f"[HEALTH] DataPipeline : {'OK' if ok else 'DÉCONNECTÉ'} | mode={status['mode']}")
        return {
            "component": "data_pipeline",
            "status": "ok" if ok else "error",
            **status,
        }
