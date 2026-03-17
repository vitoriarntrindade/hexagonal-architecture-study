"""End-to-end HTTP tests for the user creation endpoint.

Uses FastAPI's TestClient with dependency_overrides to replace the
SQLAlchemy repository with an in-memory implementation — demonstrating
one of the key benefits of hexagonal architecture: infrastructure can
be swapped at any boundary without touching the core logic.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Generator

from app.adapters.http.api import app, get_use_case
from app.adapters.repositories.in_memory_user_repository import InMemoryUserRepository
from app.adapters.security.simple_hasher import SimpleHasher
from app.application.use_cases.create_user import CreateUserUseCase


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Return a TestClient with the SQLAlchemy dependency overridden.

    A single in-memory repository instance is shared across all requests
    within the same test, preserving state between calls (e.g. duplicate
    email checks). The override is cleared after each test.
    """
    repository = InMemoryUserRepository()
    hasher = SimpleHasher()

    def override_use_case() -> CreateUserUseCase:
        return CreateUserUseCase(
            user_repository=repository,
            password_hasher=hasher,
        )

    app.dependency_overrides[get_use_case] = override_use_case
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_should_create_user_and_return_201(client: TestClient) -> None:
    response = client.post(
        "/users",
        json={
            "name": "Vitória",
            "email": "vitoria@email.com",
            "password": "123456",
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["name"] == "Vitória"
    assert body["email"] == "vitoria@email.com"
    assert "id" in body
    assert "created_at" in body
    assert "password" not in body
    assert "password_hash" not in body


def test_should_return_400_on_duplicate_email(client: TestClient) -> None:
    payload = {
        "name": "Vitória",
        "email": "vitoria@email.com",
        "password": "123456",
    }

    client.post("/users", json=payload)
    response = client.post("/users", json=payload)

    assert response.status_code == 400
    assert "vitoria@email.com" in response.json()["detail"]


def test_should_return_422_on_invalid_email(client: TestClient) -> None:
    response = client.post(
        "/users",
        json={
            "name": "Vitória",
            "email": "not-an-email",
            "password": "123456",
        },
    )

    assert response.status_code == 422


def test_should_return_422_on_missing_fields(client: TestClient) -> None:
    response = client.post("/users", json={"name": "Vitória"})

    assert response.status_code == 422


def test_should_not_expose_password_hash_in_response(client: TestClient) -> None:
    response = client.post(
        "/users",
        json={
            "name": "Vitória",
            "email": "vitoria@email.com",
            "password": "123456",
        },
    )

    body = response.json()
    assert "password" not in body
    assert "password_hash" not in body


def test_should_create_user_and_return_201(client: TestClient) -> None:
    response = client.post(
        "/users",
        json={
            "name": "Vitória",
            "email": "vitoria@email.com",
            "password": "123456",
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["name"] == "Vitória"
    assert body["email"] == "vitoria@email.com"
    assert "id" in body
    assert "created_at" in body
    assert "password" not in body
    assert "password_hash" not in body


def test_should_return_400_on_duplicate_email(client: TestClient) -> None:
    payload = {
        "name": "Vitória",
        "email": "vitoria@email.com",
        "password": "123456",
    }

    client.post("/users", json=payload)
    response = client.post("/users", json=payload)

    assert response.status_code == 400
    assert "vitoria@email.com" in response.json()["detail"]


def test_should_return_422_on_invalid_email(client: TestClient) -> None:
    response = client.post(
        "/users",
        json={
            "name": "Vitória",
            "email": "not-an-email",
            "password": "123456",
        },
    )

    assert response.status_code == 422


def test_should_return_422_on_missing_fields(client: TestClient) -> None:
    response = client.post("/users", json={"name": "Vitória"})

    assert response.status_code == 422


def test_should_not_expose_password_hash_in_response(client: TestClient) -> None:
    response = client.post(
        "/users",
        json={
            "name": "Vitória",
            "email": "vitoria@email.com",
            "password": "123456",
        },
    )

    body = response.json()
    assert "password" not in body
    assert "password_hash" not in body
