"""FastAPI dependency providers for the HTTP adapter layer."""

from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.adapters.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.adapters.security.bcrypt_hasher import BcryptHasher
from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.get_user_by_email import GetUserByEmailUseCase
from app.infrastructure.database import get_session


def get_db() -> Generator[Session, None, None]:
    """Provide a database session per request.

    Yields:
        An active SQLAlchemy Session, closed automatically after the request.
    """
    session = get_session()
    try:
        yield session
    finally:
        session.close()


def get_create_user_use_case(session: Session = Depends(get_db)) -> CreateUserUseCase:
    """Build and return a wired CreateUserUseCase.

    Args:
        session: Injected database session.

    Returns:
        A fully wired CreateUserUseCase instance.
    """
    repository = SQLAlchemyUserRepository(session)
    hasher = BcryptHasher()
    return CreateUserUseCase(repository, hasher)


def get_user_by_email_use_case(
    session: Session = Depends(get_db),
) -> GetUserByEmailUseCase:
    """Build and return a wired GetUserByEmailUseCase.

    Args:
        session: Injected database session.

    Returns:
        A fully wired GetUserByEmailUseCase instance.
    """
    repository = SQLAlchemyUserRepository(session)
    return GetUserByEmailUseCase(repository)
