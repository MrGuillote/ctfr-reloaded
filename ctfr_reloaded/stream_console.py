from datetime import datetime, timezone

from ctfr_reloaded.console import Console


class StreamConsole(Console):
    """Console que emite eventos para UI web (SSE) sin imprimir en stdout."""

    def __init__(self, on_event=None):
        super().__init__(verbose=True, use_colors=False)
        self.on_event = on_event

    def _emit(self, level, message):
        event = {
            "level": level,
            "message": str(message),
            "time": datetime.now(timezone.utc).strftime("%H:%M:%S"),
        }
        if self.on_event:
            self.on_event(event)
        return event

    def info(self, message):
        return self._emit("info", message)

    def success(self, message):
        return self._emit("success", message)

    def warn(self, message):
        return self._emit("warn", message)

    def error(self, message):
        return self._emit("error", message)

    def debug(self, message):
        return self._emit("debug", message)
