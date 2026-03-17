"""Use case for retrieving a user by email address."""

from app.domain.entities.user import User
from app.domain.exceptions import UserNotFoundError
from app.ports.user_repository import UserRepository


class GetUserByEmailUseCase:
    """Retrieves an existing user by their email address."""

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialise the use case with its required dependency.

        Args:
            user_repository: Port for user data access.
        """
        self.user_repository = user_repository

    def execute(self, email: str) -> User:
        """Retrieve a user by email.

        Args:
            email: The email address to look up.

        Returns:
            The matching User entity.

        Raises:
            UserNotFoundError: If no user exists with the given email.
        """
        user = self.user_repository.find_by_email(email)

        if user is None:
            raise UserNotFoundError(email)

        return user
