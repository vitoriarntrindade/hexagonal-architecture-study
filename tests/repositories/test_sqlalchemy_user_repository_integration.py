"""Integration tests for SQLAlchemyUserRepository using a real PostgreSQL container.

These tests exercise the repository against a production-equivalent database,
catching issues that SQLite would never surface (e.g. type coercions, constraint
names, timezone handling with ``TIMESTAMPTZ``).

The ``postgres_session`` fixture spins up a throwaway PostgreSQL container via
Testcontainers, runs Alembic (or ``create_all``) to apply the schema, and tears
everything down after the session — so CI and local runs stay hermetic.

Usage
-----
    pytest tests/repositories/test_sqlalchemy_user_repository_integration.py -v

Docker must be available in the environment.  In CI the job already has Docker
support on ``ubuntu-latest`` runners.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer

from app.adapters.repositories.models import Base
from app.adapters.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.domain.entities.user import User

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

POSTGRES_IMAGE = "postgres:16-alpine"


@pytest.fixture(scope="session")
def postgres_engine():
    """Spin up a PostgreSQL container and return a connected Engine.

    The container lives for the entire test session and is stopped/removed
    automatically by Testcontainers when the fixture goes out of scope.
    """
    with PostgresContainer(POSTGRES_IMAGE) as pg:
        engine = create_engine(
            pg.get_connection_url(),
            # pgbouncer / test runners sometimes reuse connections; echo helps
            # debug unexpected SQL during development.
            echo=False,
        )
        Base.metadata.create_all(engine)
        yield engine
        Base.metadata.drop_all(engine)


@pytest.fixture
def session(postgres_engine) -> Session:
    """Provide a transactional session that rolls back after each test.

    Uses an outer transaction + SAVEPOINT so that:
    - Each test is fully isolated (no data leaks between tests).
    - The schema is created only once per session (fast).
    - IntegrityErrors inside tests don't corrupt the outer transaction:
      the session is joined to the connection, and any aborted inner
      transaction is rolled back to the SAVEPOINT automatically.
    """
    connection = postgres_engine.connect()
    outer_tx = connection.begin()
    # Nested (SAVEPOINT) transaction — survives IntegrityErrors inside tests.
    nested = connection.begin_nested()

    SessionLocal = sessionmaker(bind=connection, join_transaction_mode="create_savepoint")
    db = SessionLocal()

    yield db

    db.close()
    # Roll back to the SAVEPOINT first (handles aborted inner transactions).
    if nested.is_active:
        nested.rollback()
    # Roll back the outer transaction to undo all changes made by this test.
    outer_tx.rollback()
    connection.close()


@pytest.fixture
def repo(session: Session) -> SQLAlchemyUserRepository:
    """Return a repository wired to the transactional test session."""
    return SQLAlchemyUserRepository(session)


@pytest.fixture
def user() -> User:
    """Return a canonical test user."""
    return User.create(
        name="Vitória",
        email="vitoria@email.com",
        password_hash="hashed_password",
    )


# ---------------------------------------------------------------------------
# save / find_by_email
# ---------------------------------------------------------------------------


def test_save_and_find_by_email(repo: SQLAlchemyUserRepository, user: User) -> None:
    """Persist a user and retrieve it by email — happy path."""
    repo.save(user)

    found = repo.find_by_email(user.email)

    assert found is not None
    assert found.id == user.id
    assert found.name == user.name
    assert found.email == user.email
    assert found.password_hash == user.password_hash


def test_find_by_email_returns_none_when_not_found(repo: SQLAlchemyUserRepository) -> None:
    """Query for a non-existent email must return None, not raise."""
    result = repo.find_by_email("ghost@example.com")

    assert result is None


def test_all_fields_are_persisted_correctly(repo: SQLAlchemyUserRepository, user: User) -> None:
    """Every domain field must survive the round-trip through PostgreSQL."""
    repo.save(user)

    found = repo.find_by_email(user.email)

    assert found is not None
    assert found.id == user.id
    assert found.name == user.name
    assert found.email == user.email
    assert found.password_hash == user.password_hash
    assert found.created_at is not None


def test_save_multiple_users(repo: SQLAlchemyUserRepository) -> None:
    """Multiple users can be saved and retrieved independently."""
    alice = User.create(name="Alice", email="alice@example.com", password_hash="hash_a")
    bob = User.create(name="Bob", email="bob@example.com", password_hash="hash_b")

    repo.save(alice)
    repo.save(bob)

    assert repo.find_by_email("alice@example.com") is not None
    assert repo.find_by_email("bob@example.com") is not None


def test_duplicate_email_raises(repo: SQLAlchemyUserRepository, user: User) -> None:
    """Inserting a second user with the same email must violate the UNIQUE constraint."""
    from sqlalchemy.exc import IntegrityError

    repo.save(user)

    duplicate = User.create(
        name="Other",
        email=user.email,  # same email
        password_hash="another_hash",
    )

    with pytest.raises(IntegrityError):
        repo.save(duplicate)


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


def test_update_user_name(repo: SQLAlchemyUserRepository, user: User) -> None:
    """Updating the name must be reflected on the next find."""
    repo.save(user)

    user.name = "Vitória Atualizada"
    repo.update(user)

    found = repo.find_by_email(user.email)
    assert found is not None
    assert found.name == "Vitória Atualizada"


def test_update_password_hash(repo: SQLAlchemyUserRepository, user: User) -> None:
    """Updating the password hash must be reflected on the next find."""
    repo.save(user)

    user.password_hash = "new_hashed_password"
    repo.update(user)

    found = repo.find_by_email(user.email)
    assert found is not None
    assert found.password_hash == "new_hashed_password"


def test_update_nonexistent_user_is_noop(repo: SQLAlchemyUserRepository) -> None:
    """Updating a user that was never saved must not raise."""
    ghost = User.create(name="Ghost", email="ghost@example.com", password_hash="x")

    # Should complete without error
    repo.update(ghost)


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


def test_delete_removes_user(repo: SQLAlchemyUserRepository, user: User) -> None:
    """After deleting a user, find_by_email must return None."""
    repo.save(user)

    repo.delete(user.email)

    assert repo.find_by_email(user.email) is None


def test_delete_nonexistent_user_is_noop(repo: SQLAlchemyUserRepository) -> None:
    """Deleting a user that does not exist must not raise."""
    repo.delete("nobody@example.com")


# ---------------------------------------------------------------------------
# list (pagination)
# ---------------------------------------------------------------------------


def test_list_returns_all_users(repo: SQLAlchemyUserRepository) -> None:
    """list() must return every saved user when page size is large enough."""
    emails = [f"user{i}@example.com" for i in range(5)]
    for email in emails:
        repo.save(User.create(name="User", email=email, password_hash="h"))

    users, total = repo.list(page=1, size=10)

    assert total == 5
    assert len(users) == 5


def test_list_pagination_first_page(repo: SQLAlchemyUserRepository) -> None:
    """First page of size 2 must return exactly 2 users."""
    for i in range(4):
        repo.save(User.create(name=f"User{i}", email=f"u{i}@example.com", password_hash="h"))

    users, total = repo.list(page=1, size=2)

    assert total == 4
    assert len(users) == 2


def test_list_pagination_last_page(repo: SQLAlchemyUserRepository) -> None:
    """Last page must contain only the remaining users."""
    for i in range(3):
        repo.save(User.create(name=f"User{i}", email=f"p{i}@example.com", password_hash="h"))

    users, total = repo.list(page=2, size=2)

    assert total == 3
    assert len(users) == 1


def test_list_empty_repository(repo: SQLAlchemyUserRepository) -> None:
    """list() on an empty repository must return an empty list and total=0."""
    users, total = repo.list(page=1, size=10)

    assert users == []
    assert total == 0
