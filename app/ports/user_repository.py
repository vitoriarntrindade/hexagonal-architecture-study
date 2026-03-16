from abc import ABC, abstractmethod
from app.domain.entities.user import User


class UserRepository(ABC):

    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass