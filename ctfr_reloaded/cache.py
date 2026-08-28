import hashlib
import json
import time
from pathlib import Path

from ctfr_reloaded.constants import CACHE_DIR_NAME


def default_cache_dir():
    return Path.home() / ".cache" / CACHE_DIR_NAME


class ResultCache:
    def __init__(self, enabled=False, cache_dir=None, ttl_seconds=3600):
        self.enabled = enabled
        self.cache_dir = Path(cache_dir) if cache_dir else default_cache_dir()
        self.ttl_seconds = ttl_seconds
        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, domain, source):
        key = hashlib.sha256("{d}:{s}".format(d=domain, s=source).encode()).hexdigest()
        return self.cache_dir / "{k}.json".format(k=key)

    def get(self, domain, source):
        if not self.enabled:
            return None
        path = self._path_for(domain, source)
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        if time.time() - payload.get("cached_at", 0) > self.ttl_seconds:
            return None
        return payload.get("subdomains")

    def set(self, domain, source, subdomains):
        if not self.enabled:
            return
        path = self._path_for(domain, source)
        payload = {
            "domain": domain,
            "source": source,
            "cached_at": time.time(),
            "subdomains": subdomains,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
