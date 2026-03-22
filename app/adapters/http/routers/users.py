"""HTTP router for user-related endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from app.adapters.http.dependencies import (
    get_create_user_use_case,
    get_user_by_email_use_case,
)
from app.adapters.http.schemas import CreateUserRequest, UserResponse
from app.adapters.http.schemas import UpdateUserRequest
from app.adapters.http.dependencies_update_delete import (
    get_update_user_use_case,
    get_delete_user_use_case,
)
from app.adapters.http.dependencies_list import get_list_users_use_case
from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.get_user_by_email import GetUserByEmailUseCase
from app.application.use_cases.update_user import UpdateUserUseCase
from app.application.use_cases.delete_user import DeleteUserUseCase
from app.application.use_cases.list_users import ListUsersUseCase
from app.domain.exceptions import EmailAlreadyRegisteredError, UserNotFoundError
from app.adapters.http.schemas import ListUsersResponse, ListUsersQuery
from app.adapters.http.schemas import LoginRequest, TokenResponse
from app.adapters.http.dependencies_auth import get_auth_use_case, get_current_user
from app.application.use_cases.authenticate_user import AuthenticateUserUseCase

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


@router.post("/login", response_model=TokenResponse, status_code=200)
def login(
    payload: LoginRequest,
    use_case: AuthenticateUserUseCase = Depends(get_auth_use_case),
) -> TokenResponse:
    """Authenticate user and return a JWT token."""
    token = use_case.execute(email=payload.email, password=payload.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse, status_code=200)
def me(current_user=Depends(get_current_user)) -> UserResponse:
    """Return current authenticated user."""
    user = current_user
    return UserResponse(id=user.id, name=user.name, email=user.email, created_at=user.created_at)


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


@router.get("", response_model=ListUsersResponse, status_code=200)
def list_users(
    q: ListUsersQuery = Depends(),
    use_case: ListUsersUseCase = Depends(get_list_users_use_case),
) -> ListUsersResponse:
    """Return a paginated list of users.

    Args:
        q (ListUsersQuery): Pagination parameters.
        use_case (ListUsersUseCase): Injected use case instance.

    Returns:
        ListUsersResponse: Paginated users and total count.
    """
    users, total = use_case.execute(page=q.page, size=q.size)
    items = [UserResponse(id=user.id, name=user.name, email=user.email, created_at=user.created_at) for user in users]
    return ListUsersResponse(items=items, total=total)



@router.patch("/{email}", response_model=UserResponse, status_code=200)
def update_user(
    email: str,
    payload: UpdateUserRequest,
    use_case: UpdateUserUseCase = Depends(get_update_user_use_case),
) -> UserResponse:
    """Update a user's information.

    Args:
        email (str): Email address of the user to update.
        payload (UpdateUserRequest): Request body with new user data.
        use_case (UpdateUserUseCase): Injected use case instance.

    Returns:
        UserResponse: Updated user data.

    Raises:
        HTTPException: If user not found (404).
    """
    try:
        user = use_case.execute(email=email, name=payload.name)
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at,
        )
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{email}", status_code=204)
def delete_user(
    email: str,
    use_case: DeleteUserUseCase = Depends(get_delete_user_use_case),
) -> None:
    """Delete a user by email address.

    Args:
        email (str): Email address of the user to delete.
        use_case (DeleteUserUseCase): Injected use case instance.

    Raises:
        HTTPException: If user not found (404).
    """
    try:
        use_case.execute(email=email)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
