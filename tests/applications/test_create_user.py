import pytest

from app.adapters.repositories.in_memory_user_repository import InMemoryUserRepository
from app.adapters.security.simple_hasher import SimpleHasher
from app.application.use_cases.create_user import CreateUserUseCase
from app.domain.exceptions import EmailAlreadyRegisteredError


@pytest.fixture
def repository():
    return InMemoryUserRepository()


@pytest.fixture
def hasher():
    return SimpleHasher()


@pytest.fixture
def use_case(repository, hasher):
    return CreateUserUseCase(repository, hasher)


def test_should_create_user_successfully(use_case):
    user = use_case.execute(
        name="Vitória",
        email="vitoria@email.com",
        password="123456",
    )

    assert user.id is not None
    assert user.name == "Vitória"
    assert user.email == "vitoria@email.com"
    assert user.password_hash != "123456"
    assert user.created_at is not None


def test_should_not_allow_duplicate_email(use_case):
    use_case.execute(
        name="Vitória",
        email="vitoria@email.com",
        password="123456",
    )

    with pytest.raises(EmailAlreadyRegisteredError, match="vitoria@email.com"):
        use_case.execute(
            name="Outra Pessoa",
            email="vitoria@email.com",
            password="abcdef",
        )


def test_should_save_user_in_repository(use_case, repository):
    user = use_case.execute(
        name="Vitória",
        email="vitoria@email.com",
        password="123456",
    )

    saved_user = repository.find_by_email("vitoria@email.com")

    assert saved_user is not None
    assert saved_user.id == user.id