import hashlib
from app.ports.password_hasher import PasswordHasher


class SimpleHasher(PasswordHasher):

    def hash(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()