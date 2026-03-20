"""Use case for updating an existing user."""

from app.domain.entities.user import User
from app.domain.exceptions import UserNotFoundError
from app.ports.user_repository import UserRepository


class UpdateUserUseCase:
    """Orchestrates the update of a user in the system."""

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialise the use case with its required dependency.

        Args:
            user_repository: Port for user persistence.
        """
        self.user_repository = user_repository

    def execute(self, email: str, name: str | None = None) -> User:
        """Update a user's information.

        Args:
            email: Email address of the user to update.
            name: New name for the user (optional).

        Returns:
            The updated User entity.

        Raises:
            UserNotFoundError: If the user does not exist.
        """
        user = self.user_repository.find_by_email(email)
        if not user:
            raise UserNotFoundError(email)
        if name:
            user.name = name
        self.user_repository.update(user)
        return user
