"""Unit tests for AuthenticateUserUseCase.

The ``JWTAuthAdapter`` is built from ``get_settings()`` so the secret
is always >= 32 bytes (set by the session fixture in conftest.py), which
silences the PyJWT InsecureKeyLengthWarning.
"""

import pytest

from app.adapters.auth.jwt_adapter import JWTAuthAdapter
from app.application.use_cases.authenticate_user import AuthenticateUserUseCase
from app.adapters.repositories.in_memory_user_repository import InMemoryUserRepository
from app.adapters.security.simple_hasher import SimpleHasher
from app.domain.entities.user import User
from app.domain.exceptions import UserNotFoundError
from app.config import get_settings


@pytest.fixture
def auth_parts():
    """Return (repo, hasher, token_provider) wired from settings."""
    settings = get_settings()
    repo = InMemoryUserRepository()
    hasher = SimpleHasher()
    token_provider = JWTAuthAdapter(
        secret=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return repo, hasher, token_provider


def test_authenticate_user_success(auth_parts):
    """Valid credentials produce a JWT with expected claims."""
    repo, hasher, token_provider = auth_parts
    settings = get_settings()

    pwd_hash = hasher.hash("secret")
    user = User.create(name="Tester", email="tester@example.com", password_hash=pwd_hash)
    repo.save(user)

    token = AuthenticateUserUseCase(repo, hasher, token_provider).execute(
        email="tester@example.com", password="secret"
    )

    assert isinstance(token, str)
    import jwt as _jwt
    payload = _jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    assert payload["sub"] == "tester@example.com"
    assert payload["user_id"] == user.id


def test_authenticate_user_user_not_found(auth_parts):
    """Unknown email raises UserNotFoundError."""
    repo, hasher, token_provider = auth_parts

    with pytest.raises(UserNotFoundError):
        AuthenticateUserUseCase(repo, hasher, token_provider).execute(
            email="nope@example.com", password="irrelevant"
        )


def test_authenticate_user_wrong_password(auth_parts):
    """Wrong password raises UserNotFoundError."""
    repo, hasher, token_provider = auth_parts

    pwd_hash = hasher.hash("correct")
    user = User.create(name="Tester", email="tester2@example.com", password_hash=pwd_hash)
    repo.save(user)

    with pytest.raises(UserNotFoundError):
        AuthenticateUserUseCase(repo, hasher, token_provider).execute(
            email="tester2@example.com", password="wrong"
        )
