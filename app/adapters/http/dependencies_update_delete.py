from app.adapters.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.application.use_cases.update_user import UpdateUserUseCase
from app.application.use_cases.delete_user import DeleteUserUseCase
from app.infrastructure.database import get_session
from fastapi import Depends
from sqlalchemy.orm import Session


def get_update_user_use_case(session: Session = Depends(get_session)) -> UpdateUserUseCase:
    repository = SQLAlchemyUserRepository(session)
    return UpdateUserUseCase(repository)


def get_delete_user_use_case(session: Session = Depends(get_session)) -> DeleteUserUseCase:
    repository = SQLAlchemyUserRepository(session)
    return DeleteUserUseCase(repository)
