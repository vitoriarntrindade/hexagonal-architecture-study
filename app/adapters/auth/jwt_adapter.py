"""JWT adapter implementing AuthTokenProvider using PyJWT."""

from __future__ import annotations

import time
from typing import Any, Mapping

import jwt

from app.ports.auth_token import AuthTokenProvider


class JWTAuthAdapter(AuthTokenProvider):
    """Simple JWT adapter. Suitable for examples and tests.

    In production you should manage keys and algorithms carefully.
    """

    def __init__(self, secret: str, algorithm: str = "HS256") -> None:
        self._secret = secret
        self._alg = algorithm

    def create_token(self, payload: Mapping[str, Any], ttl_seconds: int | None = None) -> str:
        body = dict(payload)
        now = int(time.time())
        body["iat"] = now
        if ttl_seconds:
            body["exp"] = now + int(ttl_seconds)
        return jwt.encode(body, self._secret, algorithm=self._alg)

    def verify_token(self, token: str) -> Mapping[str, Any]:
        return jwt.decode(token, self._secret, algorithms=[self._alg])
