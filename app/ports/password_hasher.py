"""Port defining the contract for password hashing."""

from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    """Abstract port for hashing and verifying passwords."""

    @abstractmethod
    def hash(self, password: str) -> str:
        """Hash a plain-text password and return the resulting hash.

        Args:
            password: Plain-text password to hash.

        Returns:
            Hashed password string.
        """

    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool:
        """Verify a plain-text password against a stored hash.

        Args:
            password: Plain-text password to check.
            hashed: Previously hashed password to compare against.

        Returns:
            True if the password matches the hash, False otherwise.
        """