from typing import Callable

from fastapi.testclient import TestClient

from app.adapters.http.api import create_app
from app.adapters.http.dependencies import get_create_user_use_case
from app.adapters.http.dependencies_list import get_list_users_use_case
from app.adapters.http.dependencies_update_delete import (
    get_update_user_use_case,
    get_delete_user_use_case,
)
from app.adapters.http.dependencies_auth import get_auth_use_case
from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.list_users import ListUsersUseCase
from app.application.use_cases.update_user import UpdateUserUseCase
from app.application.use_cases.delete_user import DeleteUserUseCase
from app.application.use_cases.authenticate_user import AuthenticateUserUseCase
from app.adapters.repositories.in_memory_user_repository import InMemoryUserRepository
from app.adapters.cache.in_memory_cache import InMemoryCache
from app.adapters.security.simple_hasher import SimpleHasher
from app.adapters.auth.jwt_adapter import JWTAuthAdapter


def make_overrides() -> tuple[dict[Callable, Callable], InMemoryUserRepository]:
    """Create dependency overrides returning in-memory adapters wired consistently.

    Returns:
        A mapping suitable for `app.dependency_overrides`.
    """
    repo = InMemoryUserRepository()
    hasher = SimpleHasher()
    cache = InMemoryCache()
    token_provider = JWTAuthAdapter(secret="test-secret")

    return (
        {
            get_create_user_use_case: lambda: CreateUserUseCase(repo, hasher),
            get_list_users_use_case: lambda: ListUsersUseCase(repo, cache),
            get_update_user_use_case: lambda: UpdateUserUseCase(repo),
            get_delete_user_use_case: lambda: DeleteUserUseCase(repo),
            get_auth_use_case: lambda: AuthenticateUserUseCase(repo, hasher, token_provider),
        },
        repo,
    )


def test_smoke_end_to_end():
    """End-to-end smoke test covering create, login, protected, list, update, delete.

    This test uses in-memory adapters for deterministic, fast execution.
    """
    app = create_app()
    overrides, repo = make_overrides()
    app.dependency_overrides.update(overrides)

    client = TestClient(app)

    # 1) Create user
    payload = {"name": "Smoke User", "email": "smoke@example.com", "password": "pwd"}
    resp = client.post("/users", json=payload)
    assert resp.status_code == 201
    created = resp.json()
    assert created["email"] == "smoke@example.com"

    # 2) Login
    resp = client.post("/users/login", json={"email": "smoke@example.com", "password": "pwd"})
    assert resp.status_code == 200
    token = resp.json().get("access_token")
    assert token

    # 3) Protected /me
    headers = {"Authorization": f"Bearer {token}"}
    # use dependency override so current_user is resolved from the same in-memory repo
    from app.adapters.http.dependencies_auth import get_current_user
    app.dependency_overrides[get_current_user] = lambda: repo.find_by_email("smoke@example.com")
    resp = client.get("/users/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "smoke@example.com"

    # 4) List users
    resp = client.get("/users?page=1&size=10")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1

    # 5) Update user name
    resp = client.patch("/users/smoke@example.com", json={"name": "Smoke Updated"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Smoke Updated"

    # 6) Delete user
    resp = client.delete("/users/smoke@example.com")
    assert resp.status_code == 204

    # 7) Ensure user removed
    resp = client.get("/users/smoke@example.com")
    assert resp.status_code == 404
