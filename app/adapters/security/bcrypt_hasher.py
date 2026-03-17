"""Adapter implementing password hashing using bcrypt."""

import bcrypt

from app.ports.password_hasher import PasswordHasher


class BcryptHasher(PasswordHasher):
    """Concrete implementation of PasswordHasher using bcrypt.

    Bcrypt is the recommended algorithm for password hashing:
    it is slow by design (preventing brute-force attacks) and
    automatically handles salt generation and storage.
    """

    def hash(self, password: str) -> str:
        """Hash a plain-text password using bcrypt.

        A unique salt is generated automatically on each call,
        so hashing the same password twice produces different results.

        Args:
            password: Plain-text password to hash.

        Returns:
            A bcrypt hash string containing the salt and digest.
        """
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify(self, password: str, hashed: str) -> bool:
        """Verify a plain-text password against a bcrypt hash.

        Args:
            password: Plain-text password to check.
            hashed: Previously hashed password to compare against.

        Returns:
            True if the password matches the hash, False otherwise.
        """
        return bcrypt.checkpw(password.encode(), hashed.encode())
