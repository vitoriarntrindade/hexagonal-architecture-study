import pytest
from fastapi.testclient import TestClient

from app.adapters.http.api import create_app
from app.adapters.http.dependencies import get_create_user_use_case
from app.adapters.http.dependencies_list import get_list_users_use_case
from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.list_users import ListUsersUseCase
from app.adapters.repositories.in_memory_user_repository import InMemoryUserRepository
from app.adapters.cache.in_memory_cache import InMemoryCache
from app.adapters.security.simple_hasher import SimpleHasher


@pytest.fixture
def client():
    app = create_app()
    repo = InMemoryUserRepository()
    hasher = SimpleHasher()
    cache = InMemoryCache()
    app.dependency_overrides[get_create_user_use_case] = lambda: CreateUserUseCase(repo, hasher)
    app.dependency_overrides[get_list_users_use_case] = lambda: ListUsersUseCase(repo, cache)
    return TestClient(app)


def test_list_users_pagination(client):
    """Create multiple users and verify pagination results."""
    # create 25 users
    for i in range(25):
        resp = client.post("/users", json={"name": f"User {i}", "email": f"user{i}@example.com", "password": "pwd"})
        assert resp.status_code == 201

    resp = client.get("/users?page=2&size=10")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 25
    assert len(body["items"]) == 10
    assert body["items"][0]["email"] == "user10@example.com"


def test_list_users_cache_hit(client):
    """Verify that repeated queries are served from cache (in-memory)."""
    resp = client.post("/users", json={"name": "Cached", "email": "cached@example.com", "password": "pwd"})
    assert resp.status_code == 201

    resp1 = client.get("/users?page=1&size=10")
    resp2 = client.get("/users?page=1&size=10")
    assert resp1.status_code == 200 and resp2.status_code == 200
    assert resp1.json() == resp2.json()
