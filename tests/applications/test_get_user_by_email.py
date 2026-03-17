"""Unit tests for GetUserByEmailUseCase."""

import pytest

from app.adapters.repositories.in_memory_user_repository import InMemoryUserRepository
from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.get_user_by_email import GetUserByEmailUseCase
from app.adapters.security.simple_hasher import SimpleHasher
from app.domain.exceptions import UserNotFoundError


@pytest.fixture
def repository() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def get_use_case(repository: InMemoryUserRepository) -> GetUserByEmailUseCase:
    return GetUserByEmailUseCase(repository)


@pytest.fixture
def create_use_case(repository: InMemoryUserRepository) -> CreateUserUseCase:
    return CreateUserUseCase(repository, SimpleHasher())


def test_should_return_user_when_email_exists(
    get_use_case: GetUserByEmailUseCase,
    create_use_case: CreateUserUseCase,
) -> None:
    created = create_use_case.execute(
        name="Vitória",
        email="vitoria@email.com",
        password="123456",
    )

    found = get_use_case.execute("vitoria@email.com")

    assert found.id == created.id
    assert found.name == created.name
    assert found.email == created.email


def test_should_raise_user_not_found_error_when_email_does_not_exist(
    get_use_case: GetUserByEmailUseCase,
) -> None:
    with pytest.raises(UserNotFoundError, match="notfound@email.com"):
        get_use_case.execute("notfound@email.com")
