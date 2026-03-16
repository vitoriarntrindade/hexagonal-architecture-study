"""Use case for creating a new user."""

from app.domain.entities.user import User
from app.domain.exceptions import EmailAlreadyRegisteredError
from app.ports.password_hasher import PasswordHasher
from app.ports.user_repository import UserRepository


class CreateUserUseCase:
    """Orchestrates the creation of a new user in the system."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        """Initialise the use case with its required dependencies.

        Args:
            user_repository: Port for user persistence.
            password_hasher: Port for hashing passwords.
        """
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(self, name: str, email: str, password: str) -> User:
        """Create and persist a new user.

        Args:
            name: Full name of the user.
            email: Email address of the user.
            password: Plain-text password to be hashed before storage.

        Returns:
            The newly created User entity.

        Raises:
            EmailAlreadyRegisteredError: If the email is already in use.
        """
        existing_user = self.user_repository.find_by_email(email)

        if existing_user:
            raise EmailAlreadyRegisteredError(email)

        password_hash = self.password_hasher.hash(password)

        user = User.create(
            name=name,
            email=email,
            password_hash=password_hash,
        )

        self.user_repository.save(user)

        return user