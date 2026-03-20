"""Use case for deleting a user."""

from app.domain.exceptions import UserNotFoundError
from app.ports.user_repository import UserRepository


class DeleteUserUseCase:
    """Orchestrates the removal of a user from the system."""

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialise the use case with its required dependency.

        Args:
            user_repository: Port for user persistence.
        """
        self.user_repository = user_repository

    def execute(self, email: str) -> None:
        """Delete a user by email address.

        Args:
            email: Email address of the user to delete.

        Raises:
            UserNotFoundError: If the user does not exist.
        """
        user = self.user_repository.find_by_email(email)
        if not user:
            raise UserNotFoundError(email)
        self.user_repository.delete(email)
