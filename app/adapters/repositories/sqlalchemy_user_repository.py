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

    def update(self, user: User) -> None:
        """Update an existing user in the database.

        Args:
            user: The User domain entity to update.
        """
        model = self._session.query(UserModel).filter(UserModel.email == user.email).first()
        if model:
            model.name = user.name
            model.password_hash = user.password_hash
            self._session.commit()

    def delete(self, email: str) -> None:
        """Remove a user by email address from the database.

        Args:
            email: The email address of the user to remove.
        """
        model = self._session.query(UserModel).filter(UserModel.email == email).first()
        if model:
            self._session.delete(model)
            self._session.commit()

    def list(self, page: int = 1, size: int = 10) -> tuple[list[User], int]:
        """Return paginated users and total count using limit/offset.

        Note: This method issues two queries (count + select). For large datasets
        consider using more efficient pagination strategies.
        """
        query = self._session.query(UserModel)
        total = query.count()
        offset = (page - 1) * size
        models = query.offset(offset).limit(size).all()
        users = [self._to_entity(m) for m in models]
        return users, total

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
