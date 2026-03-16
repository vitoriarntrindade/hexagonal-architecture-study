"""Integration tests for SQLAlchemyUserRepository using an in-memory SQLite database."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.adapters.repositories.models import Base
from app.adapters.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.domain.entities.user import User


@pytest.fixture
def session() -> Session:
    """Provide an isolated in-memory SQLite session for each test.

    Creates the schema before the test and drops it after,
    guaranteeing full isolation between test cases.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def repository(session: Session) -> SQLAlchemyUserRepository:
    """Return a SQLAlchemyUserRepository wired to the test session."""
    return SQLAlchemyUserRepository(session)


@pytest.fixture
def user() -> User:
    """Return a sample User domain entity."""
    return User.create(
        name="Vitória",
        email="vitoria@email.com",
        password_hash="hashed_password",
    )


def test_should_save_and_find_user_by_email(repository, user):
    repository.save(user)

    found = repository.find_by_email("vitoria@email.com")

    assert found is not None
    assert found.id == user.id
    assert found.name == user.name
    assert found.email == user.email
    assert found.password_hash == user.password_hash


def test_should_return_none_when_email_not_found(repository):
    found = repository.find_by_email("notfound@email.com")

    assert found is None


def test_should_persist_all_user_fields_correctly(repository, user):
    repository.save(user)

    found = repository.find_by_email(user.email)

    assert found.id == user.id
    assert found.name == user.name
    assert found.email == user.email
    assert found.password_hash == user.password_hash
    assert found.created_at is not None


def test_should_save_multiple_users(repository):
    user_a = User.create(name="Vitória", email="vitoria@email.com", password_hash="hash_a")
    user_b = User.create(name="Ana", email="ana@email.com", password_hash="hash_b")

    repository.save(user_a)
    repository.save(user_b)

    assert repository.find_by_email("vitoria@email.com") is not None
    assert repository.find_by_email("ana@email.com") is not None
