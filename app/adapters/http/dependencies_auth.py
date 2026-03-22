"""FastAPI dependency providers for authentication.

All JWT configuration is read from :func:`app.config.get_settings` so
there are no hard-coded secrets anywhere in the codebase.
"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.adapters.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.adapters.auth.jwt_adapter import JWTAuthAdapter
from app.adapters.security.bcrypt_hasher import BcryptHasher
from app.application.use_cases.authenticate_user import AuthenticateUserUseCase
from app.config import Settings, get_settings
from app.infrastructure.database import get_session

# Simple bearer scheme for token extraction
bearer = HTTPBearer()


def get_auth_token_provider(
    settings: Settings = Depends(get_settings),
) -> JWTAuthAdapter:
    """Build a JWTAuthAdapter from application settings.

    Args:
        settings: Injected application settings.

    Returns:
        Configured ``JWTAuthAdapter`` instance.
    """
    return JWTAuthAdapter(
        secret=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def get_auth_use_case(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AuthenticateUserUseCase:
    """Provide an ``AuthenticateUserUseCase`` wired with SQLAlchemy repo and bcrypt.

    Args:
        session: Database session.
        settings: Application settings.

    Returns:
        Configured ``AuthenticateUserUseCase``.
    """
    repository = SQLAlchemyUserRepository(session)
    hasher = BcryptHasher()
    token_provider = JWTAuthAdapter(
        secret=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return AuthenticateUserUseCase(repository, hasher, token_provider)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
):
    """Verify Bearer token and return the authenticated domain user.

    Args:
        credentials: HTTP Authorization header credentials.
        session: Database session for user lookup.
        settings: Application settings for JWT verification.

    Returns:
        Domain ``User`` entity for the authenticated user.

    Raises:
        HTTPException: 401 if the token is invalid or user not found.
    """
    token = credentials.credentials
    provider = JWTAuthAdapter(
        secret=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    try:
        payload = provider.verify_token(token)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    repository = SQLAlchemyUserRepository(session)
    user = repository.find_by_email(payload.get("sub", ""))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token user")
    return user
