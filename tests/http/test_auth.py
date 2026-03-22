from typing import Tuple

import pytest
from fastapi.testclient import TestClient

from app.adapters.http.api import create_app
from app.adapters.http.dependencies import get_create_user_use_case
from app.adapters.http.dependencies_auth import get_auth_use_case, get_auth_token_provider
from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.authenticate_user import AuthenticateUserUseCase
from app.adapters.repositories.in_memory_user_repository import InMemoryUserRepository
from app.adapters.security.simple_hasher import SimpleHasher


@pytest.fixture
def client_and_repo() -> Tuple[TestClient, InMemoryUserRepository]:
    """Create a TestClient wired with in-memory repository and dependencies.

    Returns a tuple of (client, repo) so tests can interact with storage when
    needed (for dependency overrides).
    """
    app = create_app()
    repo = InMemoryUserRepository()
    hasher = SimpleHasher()

    app.dependency_overrides[get_create_user_use_case] = lambda: CreateUserUseCase(repo, hasher)
    app.dependency_overrides[get_auth_use_case] = lambda: AuthenticateUserUseCase(repo, hasher, get_auth_token_provider())

    client = TestClient(app)
    return client, repo


def test_login_returns_token(client_and_repo):
    """Login endpoint returns an access token for valid credentials."""
    client, _ = client_and_repo

    # create user
    resp = client.post("/users", json={"name": "AuthUser", "email": "auth@example.com", "password": "pwd"})
    assert resp.status_code == 201

    # login
    resp = client.post("/users/login", json={"email": "auth@example.com", "password": "pwd"})
    assert resp.status_code == 200
    data = resp.json()
    token = data.get("access_token")
    assert isinstance(token, str) and len(token) > 0


def test_me_endpoint_requires_token_and_returns_user(client_and_repo):
    """Protected /me endpoint requires a valid token and returns the user data."""
    client, repo = client_and_repo

    # create user and obtain token
    resp = client.post("/users", json={"name": "AuthUser", "email": "auth@example.com", "password": "pwd"})
    assert resp.status_code == 201
    resp = client.post("/users/login", json={"email": "auth@example.com", "password": "pwd"})
    token = resp.json().get("access_token")

    # valid token -> success
    headers = {"Authorization": f"Bearer {token}"}
    # ensure dependency resolves current_user from in-memory repo
    from app.adapters.http.dependencies_auth import get_current_user

    app = client.app
    app.dependency_overrides[get_current_user] = lambda: repo.find_by_email("auth@example.com")
    resp = client.get("/users/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "auth@example.com"

    # invalid token -> unauthorized
    app.dependency_overrides.pop(get_current_user, None)
    resp = client.get("/users/me", headers={"Authorization": "Bearer bad.token"})
    assert resp.status_code == 401
