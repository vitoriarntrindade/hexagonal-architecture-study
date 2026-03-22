"""Port defining the contract for user persistence."""

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.user import User


class UserRepository(ABC):
    """Abstract port for user data access."""

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email address.

        Args:
            email: The email address to look up.

        Returns:
            The matching User, or None if not found.
        """

    @abstractmethod
    def save(self, user: User) -> None:
        """Persist a user instance.

        Args:
            user: The User entity to save.
        """

    @abstractmethod
    def update(self, user: User) -> None:
        """Update an existing user instance.

        Args:
            user: The User entity to update.
        """

    @abstractmethod
    def delete(self, email: str) -> None:
        """Remove a user by email address.

        Args:
            email: The email address of the user to remove.
        """

    @abstractmethod
    def list(self, page: int = 1, size: int = 10) -> tuple[list[User], int]:
        """Return a paginated list of users and the total count.

        Args:
            page: 1-based page number.
            size: Number of items per page.

        Returns:
            A tuple containing a list of User and the total user count.
        """