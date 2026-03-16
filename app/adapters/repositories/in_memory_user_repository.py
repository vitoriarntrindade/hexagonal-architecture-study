"""In-memory adapter implementing the UserRepository port."""

from typing import List, Optional

from app.domain.entities.user import User
from app.ports.user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    """Stores users in memory. Suitable for testing and prototyping."""

    def __init__(self) -> None:
        self._users: List[User] = []

    def find_by_email(self, email: str) -> Optional[User]:
        """Return the user with the given email, or None if not found.

        Args:
            email: The email address to search for.

        Returns:
            Matching User or None.
        """
        for user in self._users:
            if user.email == email:
                return user
        return None

    def save(self, user: User) -> None:
        """Append a user to the in-memory store.

        Args:
            user: The User entity to persist.
        """
        self._users.append(user)