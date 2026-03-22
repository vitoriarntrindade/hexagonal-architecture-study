import pytest
import jwt

from app.adapters.auth.jwt_adapter import JWTAuthAdapter
from app.application.use_cases.authenticate_user import AuthenticateUserUseCase
from app.adapters.repositories.in_memory_user_repository import InMemoryUserRepository
from app.adapters.security.simple_hasher import SimpleHasher
from app.domain.entities.user import User
from app.domain.exceptions import UserNotFoundError


def test_authenticate_user_success():
    repo = InMemoryUserRepository()
    hasher = SimpleHasher()
    token_provider = JWTAuthAdapter(secret="test-secret")

    # prepare user
    pwd_hash = hasher.hash("secret")
    user = User.create(name="Tester", email="tester@example.com", password_hash=pwd_hash)
    repo.save(user)

    use_case = AuthenticateUserUseCase(repo, hasher, token_provider)
    token = use_case.execute(email="tester@example.com", password="secret")

    assert isinstance(token, str)
    payload = jwt.decode(token, "test-secret", algorithms=["HS256"])  # verify token
    assert payload["sub"] == "tester@example.com"
    assert payload["user_id"] == user.id


def test_authenticate_user_user_not_found():
    repo = InMemoryUserRepository()
    hasher = SimpleHasher()
    token_provider = JWTAuthAdapter(secret="test-secret")
    use_case = AuthenticateUserUseCase(repo, hasher, token_provider)

    with pytest.raises(UserNotFoundError):
        use_case.execute(email="nope@example.com", password="irrelevant")


def test_authenticate_user_wrong_password():
    repo = InMemoryUserRepository()
    hasher = SimpleHasher()
    token_provider = JWTAuthAdapter(secret="test-secret")

    pwd_hash = hasher.hash("correct")
    user = User.create(name="Tester", email="tester2@example.com", password_hash=pwd_hash)
    repo.save(user)

    use_case = AuthenticateUserUseCase(repo, hasher, token_provider)

    with pytest.raises(UserNotFoundError):
        use_case.execute(email="tester2@example.com", password="wrong")
