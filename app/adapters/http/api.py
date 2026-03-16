"""FastAPI HTTP adapter exposing the user creation endpoint."""

from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

from app.adapters.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)
from app.adapters.security.simple_hasher import SimpleHasher
from app.application.use_cases.create_user import CreateUserUseCase
from app.domain.exceptions import EmailAlreadyRegisteredError

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


repository = InMemoryUserRepository()
hasher = SimpleHasher()
create_user_use_case = CreateUserUseCase(repository, hasher)


@app.post("/users", response_model=CreateUserResponse, status_code=201)
def create_user(payload: CreateUserRequest) -> CreateUserResponse:
    """Create a new user.

    Args:
        payload: Request body containing name, email and password.

    Returns:
        The created user data.

    Raises:
        HTTPException: 400 if the email is already registered.
    """
    try:
        user = create_user_use_case.execute(
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