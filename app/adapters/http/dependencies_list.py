from fastapi import Depends
from sqlalchemy.orm import Session

from app.adapters.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.adapters.cache.in_memory_cache import InMemoryCache
from app.application.use_cases.list_users import ListUsersUseCase
from app.infrastructure.database import get_session


def get_list_users_use_case(session: Session = Depends(get_session)) -> ListUsersUseCase:
    repository = SQLAlchemyUserRepository(session)
    cache = InMemoryCache()
    return ListUsersUseCase(repository, cache)
