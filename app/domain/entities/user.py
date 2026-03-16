"""Domain entity representing a user."""

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class User:
    """Represents a user in the domain layer."""

    id: str
    name: str
    email: str
    password_hash: str
    created_at: datetime

    @staticmethod
    def create(name: str, email: str, password_hash: str) -> "User":
        """Create and return a new User instance with a generated ID and timestamp.

        Args:
            name: Full name of the user.
            email: Email address of the user.
            password_hash: Already hashed password.

        Returns:
            A new User instance.
        """
        return User(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            password_hash=password_hash,
            created_at=datetime.now(tz=timezone.utc),
        )