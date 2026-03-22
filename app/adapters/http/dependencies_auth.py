
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.adapters.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.adapters.auth.jwt_adapter import JWTAuthAdapter
from app.adapters.security.bcrypt_hasher import BcryptHasher
from app.application.use_cases.authenticate_user import AuthenticateUserUseCase
from app.infrastructure.database import get_session

# Simple bearer scheme for token extraction
bearer = HTTPBearer()


def get_auth_token_provider() -> JWTAuthAdapter:
    # In real app read secret from settings
    return JWTAuthAdapter(secret="dev-secret")


def get_auth_use_case(session: Session = Depends(get_session)) -> AuthenticateUserUseCase:
    repository = SQLAlchemyUserRepository(session)
    hasher = BcryptHasher()
    token_provider = get_auth_token_provider()
    return AuthenticateUserUseCase(repository, hasher, token_provider)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(get_session),
):
    token = credentials.credentials
    provider = get_auth_token_provider()
    try:
        payload = provider.verify_token(token)
    except Exception as exc:  # noqa: BLE001 - we handle verification errors
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    repository = SQLAlchemyUserRepository(session)
    user = repository.find_by_email(payload.get("sub", ""))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token user")
    return user
