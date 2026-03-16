"""Application entrypoint for manual/local testing."""

from app.adapters.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.infrastructure.database import get_session
from app.adapters.security.simple_hasher import SimpleHasher
from app.application.use_cases.create_user import CreateUserUseCase


repository = SQLAlchemyUserRepository(get_session())
hasher = SimpleHasher()

create_user = CreateUserUseCase(repository, hasher)


user = create_user.execute(
    name="Vitória",
    email="vitoria@email.com",
    password="123456"
)

print(user)