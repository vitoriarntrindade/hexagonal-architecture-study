"""SQLAlchemy adapter implementing the UserRepository port."""

from typing import Optional

from sqlalchemy.orm import Session

from app.adapters.repositories.models import UserModel
from app.domain.entities.user import User
from app.ports.user_repository import UserRepository


class SQLAlchemyUserRepository(UserRepository):
    """Concrete implementation of UserRepository backed by SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        """Initialise the repository with an active database session.

        Args:
            session: An open SQLAlchemy Session to use for queries.
        """
        self._session = session

    def find_by_email(self, email: str) -> Optional[User]:
        """Query the database for a user with the given email.

        Args:
            email: The email address to look up.

        Returns:
            The matching User domain entity, or None if not found.
        """
        model = (
            self._session.query(UserModel)
            .filter(UserModel.email == email)
            .first()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def save(self, user: User) -> None:
        """Persist a user entity to the database.

        Args:
            user: The User domain entity to save.
        """
        model = UserModel(
            id=user.id,
            name=user.name,
            email=user.email,
            password_hash=user.password_hash,
            created_at=user.created_at,
        )
        self._session.add(model)
        self._session.commit()

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        """Map a UserModel ORM instance to a User domain entity.

        Args:
            model: The ORM model instance to convert.

        Returns:
            The equivalent User domain entity.
        """
        return User(
            id=model.id,
            name=model.name,
            email=model.email,
            password_hash=model.password_hash,
            created_at=model.created_at,
        )
