"""Adapter implementing password hashing using SHA-256."""

import hashlib

from app.ports.password_hasher import PasswordHasher


class SimpleHasher(PasswordHasher):
    """Concrete implementation of PasswordHasher using SHA-256."""

    def hash(self, password: str) -> str:
        """Hash a plain-text password using SHA-256.

        Args:
            password: Plain-text password to hash.

        Returns:
            Hexadecimal SHA-256 digest of the password.
        """
        return hashlib.sha256(password.encode()).hexdigest()