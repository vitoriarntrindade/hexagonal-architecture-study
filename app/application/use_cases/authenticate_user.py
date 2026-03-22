"""Use case for authenticating a user and returning a token."""

from app.ports.user_repository import UserRepository
from app.ports.password_hasher import PasswordHasher
from app.ports.auth_token import AuthTokenProvider
from app.domain.exceptions import UserNotFoundError


class AuthenticateUserUseCase:
    """Verify credentials and return an auth token."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_provider: AuthTokenProvider,
    ) -> None:
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_provider = token_provider

    def execute(self, email: str, password: str) -> str:
        user = self.user_repository.find_by_email(email)
        if not user:
            raise UserNotFoundError(email)
        if not self.password_hasher.verify(password, user.password_hash):
            raise UserNotFoundError(email)

        token = self.token_provider.create_token({"sub": user.email, "user_id": user.id}, ttl_seconds=3600)
        return token
