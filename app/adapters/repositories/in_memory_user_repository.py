from app.ports.user_repository import UserRepository
from app.domain.entities.user import User


class InMemoryUserRepository(UserRepository):

    def __init__(self):
        self.users = []

    def find_by_email(self, email: str):

        for user in self.users:
            if user.email == email:
                return user

        return None

    def save(self, user: User):
        self.users.append(user)