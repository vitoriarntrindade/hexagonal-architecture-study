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