"""Adapter implementing password hashing using SHA-256.

Suitable for testing and development only.
Not recommended for production — use BcryptHasher instead.
"""

import hashlib

from app.ports.password_hasher import PasswordHasher


class SimpleHasher(PasswordHasher):
    """Concrete implementation of PasswordHasher using SHA-256.

    Used in tests and local development due to its simplicity and speed.
    """

    def hash(self, password: str) -> str:
        """Hash a plain-text password using SHA-256.

        Args:
            password: Plain-text password to hash.

        Returns:
            Hexadecimal SHA-256 digest of the password.
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def verify(self, password: str, hashed: str) -> bool:
        """Verify a plain-text password against a SHA-256 hash.

        Args:
            password: Plain-text password to check.
            hashed: Previously hashed password to compare against.

        Returns:
            True if the password matches the hash, False otherwise.
        """
        return self.hash(password) == hashed