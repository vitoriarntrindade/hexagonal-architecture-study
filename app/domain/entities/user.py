from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class User:
    id: str
    name: str
    email: str
    password_hash: str
    created_at: datetime

    @staticmethod
    def create(name: str, email: str, password_hash: str) -> "User":
        return User(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            password_hash=password_hash,
            created_at=datetime.utcnow(),
        )