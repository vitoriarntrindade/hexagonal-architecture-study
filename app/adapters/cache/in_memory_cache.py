"""Simple in-memory cache adapter for the Cache port.

Intended for testing and local development only.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from app.ports.cache import Cache


class InMemoryCache(Cache):
    """A trivial dict-backed cache with TTL support."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float | None]] = {}

    def _expired(self, meta: tuple[Any, float | None]) -> bool:
        _, expiry = meta
        return expiry is not None and time.time() > expiry

    def get(self, key: str) -> Optional[Any]:
        meta = self._store.get(key)
        if not meta:
            return None
        if self._expired(meta):
            self._store.pop(key, None)
            return None
        return meta[0]

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        expiry = time.time() + ttl if ttl is not None else None
        self._store[key] = (value, expiry)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)
