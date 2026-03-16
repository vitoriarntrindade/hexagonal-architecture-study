"""Port defining the contract for password hashing."""

from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    """Abstract port for hashing passwords."""

    @abstractmethod
    def hash(self, password: str) -> str:
        """Hash a plain-text password and return the resulting hash.

        Args:
            password: Plain-text password to hash.

        Returns:
            Hashed password string.
        """