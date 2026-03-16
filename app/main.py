from app.application.use_cases.create_user import CreateUserUseCase
from app.adapters.repositories.in_memory_user_repository import InMemoryUserRepository
from app.adapters.simple_hasher import SimpleHasher


repository = InMemoryUserRepository()
hasher = SimpleHasher()

create_user = CreateUserUseCase(repository, hasher)


user = create_user.execute(
    name="Vitória",
    email="vitoria@email.com",
    password="123456"
)

print(user)