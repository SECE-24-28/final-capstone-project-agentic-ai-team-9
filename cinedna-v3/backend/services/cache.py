import time
from typing import Any, Optional
from threading import Lock


class TTLCache:
    """Simple thread-safe in-memory TTL cache."""

    def __init__(self):
        self._store: dict = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if expires_at and time.time() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: int = 3600):
        with self._lock:
            expires_at = time.time() + ttl if ttl else None
            self._store[key] = (value, expires_at)

    def delete(self, key: str):
        with self._lock:
            self._store.pop(key, None)

    def clear(self):
        with self._lock:
            self._store.clear()

    def size(self) -> int:
        return len(self._store)


# Singleton
cache = TTLCache()
