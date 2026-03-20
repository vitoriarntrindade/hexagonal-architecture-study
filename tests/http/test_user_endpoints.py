import pytest
from fastapi.testclient import TestClient
from app.adapters.http.api import create_app
from app.adapters.http.dependencies import get_create_user_use_case
from app.adapters.http.dependencies_update_delete import (
    get_update_user_use_case,
    get_delete_user_use_case,
)
from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.update_user import UpdateUserUseCase
from app.application.use_cases.delete_user import DeleteUserUseCase
from app.adapters.repositories.in_memory_user_repository import InMemoryUserRepository
from app.adapters.security.simple_hasher import SimpleHasher

@pytest.fixture
def client():
    app = create_app()
    repo = InMemoryUserRepository()
    hasher = SimpleHasher()
    app.dependency_overrides[get_create_user_use_case] = lambda: CreateUserUseCase(repo, hasher)
    app.dependency_overrides[get_update_user_use_case] = lambda: UpdateUserUseCase(repo)
    app.dependency_overrides[get_delete_user_use_case] = lambda: DeleteUserUseCase(repo)
    return TestClient(app)


def test_update_user_success(client):
    """Create a user and update its name successfully."""
    response = client.post("/users", json={
        "name": "Alice", "email": "alice@example.com", "password": "123"
        })
    assert response.status_code == 201
    
    response = client.patch("/users/alice@example.com", json={"name": "Alice Updated"})
    assert response.status_code == 200
    assert response.json()["name"] == "Alice Updated"


def test_update_user_not_found(client):
    """Try to update a user that does not exist and expect 404 error."""
    response = client.patch("/users/notfound@example.com", json={"name": "Nobody"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_delete_user_success(client):
    """Create a user, delete it, and verify it is removed."""
    response = client.post("/users", json={"name": "Bob", "email": "bob@example.com", "password": "123"})
    assert response.status_code == 201

    response = client.delete("/users/bob@example.com")
    assert response.status_code == 204
    
    response = client.get("/users/bob@example.com")
    assert response.status_code == 404


def test_delete_user_not_found(client):
    """Try to delete a user that does not exist and expect 404 error."""
    response = client.delete("/users/notfound@example.com")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
