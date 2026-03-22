"""Pydantic schemas for the user HTTP endpoints."""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class CreateUserRequest(BaseModel):
    """Request payload for the create-user endpoint."""

    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Response payload returned for user data endpoints."""

    id: str
    name: str
    email: EmailStr
    created_at: datetime


class ListUsersResponse(BaseModel):
    """Response for paginated list of users."""

    items: list[UserResponse]
    total: int


class ListUsersQuery(BaseModel):
    """Query parameters for listing users."""

    page: int = 1
    size: int = 10


class UpdateUserRequest(BaseModel):
    """Request payload for updating a user."""
    name: str | None = None

class DeleteUserRequest(BaseModel):
    """Request payload for deleting a user."""
    email: EmailStr
