"""HTTP tests for authentication endpoints (/login, /me).

All adapters are in-memory; the JWTAuthAdapter is built from ``get_settings()``
so the token issued by the login use case is verifiable by ``get_current_user``
without any ad-hoc dependency pop/override mid-test.
"""

from __future__ import annotations

from typing import Tuple

import pytest
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient

from app.adapters.auth.jwt_adapter import JWTAuthAdapter
from app.adapters.http.api import create_app
from app.adapters.http.dependencies import get_create_user_use_case
from app.adapters.http.dependencies_auth import get_auth_use_case, get_current_user
from app.adapters.repositories.in_memory_user_repository import InMemoryUserRepository
from app.adapters.security.simple_hasher import SimpleHasher
from app.application.use_cases.authenticate_user import AuthenticateUserUseCase
from app.application.use_cases.create_user import CreateUserUseCase
from app.config import get_settings


@pytest.fixture
def client_and_repo() -> Tuple[TestClient, InMemoryUserRepository]:
    """Create a TestClient wired with in-memory adapters.

    Both the auth use case and ``get_current_user`` share the same
    ``JWTAuthAdapter`` (built from ``get_settings()``), so the full JWT
    round-trip is exercised without a real database.

    Returns:
        A tuple of ``(client, repo)``.
    """
    app = create_app()
    repo = InMemoryUserRepository()
    hasher = SimpleHasher()
    settings = get_settings()

    token_provider = JWTAuthAdapter(
        secret=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    _bearer = HTTPBearer()

    def _current_user(credentials: HTTPAuthorizationCredentials = Depends(_bearer)):
        try:
            payload = token_provider.verify_token(credentials.credentials)
        except Exception as exc:
            raise HTTPException(status_code=401, detail="Invalid token") from exc
        user = repo.find_by_email(payload.get("sub", ""))
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token user")
        return user

    app.dependency_overrides[get_create_user_use_case] = lambda: CreateUserUseCase(repo, hasher)
    app.dependency_overrides[get_auth_use_case] = lambda: AuthenticateUserUseCase(
        repo, hasher, token_provider
    )
    app.dependency_overrides[get_current_user] = _current_user

    return TestClient(app), repo


def test_login_returns_token(client_and_repo):
    """Login endpoint returns an access token for valid credentials."""
    client, _ = client_and_repo

    resp = client.post("/users", json={"name": "AuthUser", "email": "auth@example.com", "password": "pwd"})
    assert resp.status_code == 201

    resp = client.post("/users/login", json={"email": "auth@example.com", "password": "pwd"})
    assert resp.status_code == 200
    token = resp.json().get("access_token")
    assert isinstance(token, str) and len(token) > 0


def test_me_endpoint_with_valid_token_returns_user(client_and_repo):
    """Protected /me endpoint returns user data when the token is valid."""
    client, _ = client_and_repo

    client.post("/users", json={"name": "AuthUser", "email": "auth@example.com", "password": "pwd"})
    resp = client.post("/users/login", json={"email": "auth@example.com", "password": "pwd"})
    token = resp.json().get("access_token")

    resp = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "auth@example.com"


def test_me_endpoint_with_invalid_token_returns_401(client_and_repo):
    """Protected /me endpoint returns 401 when the token is invalid."""
    client, _ = client_and_repo

    resp = client.get("/users/me", headers={"Authorization": "Bearer bad.token.here"})
    assert resp.status_code == 401
