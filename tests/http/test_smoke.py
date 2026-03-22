from typing import Callable

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient

from app.adapters.http.api import create_app
from app.adapters.http.dependencies import get_create_user_use_case, get_user_by_email_use_case
from app.adapters.http.dependencies_list import get_list_users_use_case
from app.adapters.http.dependencies_update_delete import (
    get_update_user_use_case,
    get_delete_user_use_case,
)
from app.adapters.http.dependencies_auth import get_auth_use_case, get_current_user
from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.get_user_by_email import GetUserByEmailUseCase
from app.application.use_cases.list_users import ListUsersUseCase
from app.application.use_cases.update_user import UpdateUserUseCase
from app.application.use_cases.delete_user import DeleteUserUseCase
from app.application.use_cases.authenticate_user import AuthenticateUserUseCase
from app.adapters.repositories.in_memory_user_repository import InMemoryUserRepository
from app.adapters.cache.in_memory_cache import InMemoryCache
from app.adapters.security.simple_hasher import SimpleHasher
from app.adapters.auth.jwt_adapter import JWTAuthAdapter
from app.config import get_settings


def make_overrides(
    repo: InMemoryUserRepository,
) -> dict[Callable, Callable]:
    """Build dependency overrides using in-memory adapters.

    The ``JWTAuthAdapter`` is built from ``get_settings()`` so the same secret
    used to issue tokens is used to verify them — no ad-hoc override needed.

    Args:
        repo: Shared in-memory repository instance.

    Returns:
        A mapping suitable for ``app.dependency_overrides``.
    """
    settings = get_settings()
    hasher = SimpleHasher()
    cache = InMemoryCache()
    token_provider = JWTAuthAdapter(
        secret=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    _bearer = HTTPBearer()

    def _verify_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    ):
        try:
            payload = token_provider.verify_token(credentials.credentials)
        except Exception as exc:
            raise HTTPException(status_code=401, detail="Invalid token") from exc
        user = repo.find_by_email(payload.get("sub", ""))
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token user")
        return user

    return {
        get_create_user_use_case: lambda: CreateUserUseCase(repo, hasher),
        get_user_by_email_use_case: lambda: GetUserByEmailUseCase(repo),
        get_list_users_use_case: lambda: ListUsersUseCase(repo, cache),
        get_update_user_use_case: lambda: UpdateUserUseCase(repo),
        get_delete_user_use_case: lambda: DeleteUserUseCase(repo),
        get_auth_use_case: lambda: AuthenticateUserUseCase(repo, hasher, token_provider),
        get_current_user: _verify_current_user,
    }


def test_smoke_end_to_end():
    """End-to-end smoke test covering create, login, protected, list, update, delete.

    Uses in-memory adapters for deterministic, fast execution.
    The full JWT round-trip (issue → verify) is exercised without a real database.
    """
    repo = InMemoryUserRepository()
    app = create_app()
    app.dependency_overrides.update(make_overrides(repo))
    client = TestClient(app)

    # 1) Create user
    resp = client.post("/users", json={"name": "Smoke User", "email": "smoke@example.com", "password": "pwd"})
    assert resp.status_code == 201
    assert resp.json()["email"] == "smoke@example.com"

    # 2) Login — issues a real JWT signed with the test secret
    resp = client.post("/users/login", json={"email": "smoke@example.com", "password": "pwd"})
    assert resp.status_code == 200
    token = resp.json().get("access_token")
    assert token

    # 3) Protected /me — verifies JWT and returns user
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/users/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "smoke@example.com"

    # 4) List users (paginated)
    resp = client.get("/users?page=1&size=10")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1

    # 5) Update user name
    resp = client.patch("/users/smoke@example.com", json={"name": "Smoke Updated"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Smoke Updated"

    # 6) Delete user
    resp = client.delete("/users/smoke@example.com")
    assert resp.status_code == 204

    # 7) Ensure user is removed
    resp = client.get("/users/smoke@example.com")
    assert resp.status_code == 404

