from app.domain.entities.user import User
from app.ports.user_repository import UserRepository
from app.ports.password_hasher import PasswordHasher


class CreateUserUseCase:

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(self, name: str, email: str, password: str) -> User:

        existing_user = self.user_repository.find_by_email(email)

        if existing_user:
            raise ValueError("Email already registered")

        password_hash = self.password_hasher.hash(password)

        user = User.create(
            name=name,
            email=email,
            password_hash=password_hash
        )

        self.user_repository.save(user)

        return user