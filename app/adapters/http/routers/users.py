"""HTTP router for user-related endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from app.adapters.http.dependencies import (
    get_create_user_use_case,
    get_user_by_email_use_case,
)
from app.adapters.http.schemas import CreateUserRequest, UserResponse
from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.get_user_by_email import GetUserByEmailUseCase
from app.domain.exceptions import EmailAlreadyRegisteredError, UserNotFoundError

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    payload: CreateUserRequest,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
) -> UserResponse:
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
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at,
        )
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{email}", response_model=UserResponse, status_code=200)
def get_user(
    email: str,
    use_case: GetUserByEmailUseCase = Depends(get_user_by_email_use_case),
) -> UserResponse:
    """Retrieve a user by email address.

    Args:
        email: The email address to look up.
        use_case: Injected use case instance.

    Returns:
        The matching user data.

    Raises:
        HTTPException: 404 if no user with the given email exists.
    """
    try:
        user = use_case.execute(email)
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at,
        )
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
