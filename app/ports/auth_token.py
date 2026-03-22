"""Port defining the contract for creating and verifying authentication tokens."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping


class AuthTokenProvider(ABC):
    """Abstract port to create and verify authentication tokens (e.g. JWT)."""

    @abstractmethod
    def create_token(self, payload: Mapping[str, Any], ttl_seconds: int | None = None) -> str:
        """Create a signed token containing the given payload.

        Args:
            payload: Serialisable claims to include in the token.
            ttl_seconds: Optional time-to-live in seconds.

        Returns:
            A compact string token.
        """

    @abstractmethod
    def verify_token(self, token: str) -> Mapping[str, Any]:
        """Verify a token and return the payload if valid.

        Raises an exception if verification fails.
        """
