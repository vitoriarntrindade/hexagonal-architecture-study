"""Application entrypoint for manual/local testing."""

from app.adapters.repositories.in_memory_user_repository import InMemoryUserRepository
from app.adapters.security.simple_hasher import SimpleHasher
from app.application.use_cases.create_user import CreateUserUseCase


repository = InMemoryUserRepository()
hasher = SimpleHasher()

create_user = CreateUserUseCase(repository, hasher)


user = create_user.execute(
    name="Vitória",
    email="vitoria@email.com",
    password="123456"
)

print(user)