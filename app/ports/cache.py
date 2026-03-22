"""Port defining the cache contract used by the application.

This keeps the domain independent from specific cache implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


class Cache(ABC):
    """Abstract cache port.

    Implementations may be in-memory (for tests) or Redis, Memcached, etc.
    """

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache by key.

        Returns None when the key is missing or expired.
        """

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store a value in the cache with an optional TTL (seconds)."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a key from the cache."""
