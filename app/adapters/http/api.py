"""FastAPI HTTP adapter exposing the user creation endpoint."""

from datetime import datetime
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.adapters.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from app.adapters.security.simple_hasher import SimpleHasher
from app.application.use_cases.create_user import CreateUserUseCase
from app.domain.exceptions import EmailAlreadyRegisteredError
from app.infrastructure.database import get_session

app = FastAPI()


class CreateUserRequest(BaseModel):
    """Request payload for the create-user endpoint."""

    name: str
    email: EmailStr
    password: str


class CreateUserResponse(BaseModel):
    """Response payload returned after successful user creation."""

    id: str
    name: str
    email: EmailStr
    created_at: datetime


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session per request.

    Yields:
        An active SQLAlchemy Session, closed automatically after the request.
    """
    session = get_session()
    try:
        yield session
    finally:
        session.close()


def get_use_case(session: Session = Depends(get_db)) -> CreateUserUseCase:
    """FastAPI dependency that builds the CreateUserUseCase.

    Args:
        session: Injected database session.

    Returns:
        A fully wired CreateUserUseCase instance.
    """
    repository = SQLAlchemyUserRepository(session)
    hasher = SimpleHasher()
    return CreateUserUseCase(repository, hasher)


@app.post("/users", response_model=CreateUserResponse, status_code=201)
def create_user(
    payload: CreateUserRequest,
    use_case: CreateUserUseCase = Depends(get_use_case),
) -> CreateUserResponse:
    """Create a new user.

    Args:
        payload: Request body containing name, email and password.
        use_case: Injected use case instance.

    Returns:
        The created user data.

    Raises:
        HTTPException: 400 if the email is already registered.
    """
    try:
        user = use_case.execute(
            name=payload.name,
            email=payload.email,
            password=payload.password,
        )
        return CreateUserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at,
        )
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc