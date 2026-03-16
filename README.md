# 🔷 Hexagonal Architecture Study

> Estudo prático de **Arquitetura Hexagonal (Ports and Adapters)** com Python.  
> O foco não é entregar uma API pronta — é entender, na prática, como isolar o domínio,  
> tornar a lógica de negócio testável e trocar infraestrutura sem tocar no núcleo da aplicação.

---

## 🎯 Objetivo

Este repositório existe para um único propósito: **compreender arquitetura hexagonal de forma prática**.

Cada decisão de design aqui foi tomada pensando em **clareza conceitual**, não em performance ou features.  
Algumas simplificações foram feitas propositalmente para que o foco permaneça na arquitetura.

---

## 💡 Por que estudar arquitetura hexagonal?

A maioria dos projetos começa simples e vai acumulando complexidade acidental:  
lógica de negócio misturada com framework, banco de dados acoplado ao domínio,  
testes que dependem de infraestrutura real.

A arquitetura hexagonal resolve isso colocando **o domínio no centro** e empurrando  
toda infraestrutura para as bordas — onde ela sempre deveria estar.

Com isso:

- ✅ A lógica de negócio pode ser testada **sem banco, sem HTTP, sem I/O**
- ✅ Um adapter pode ser trocado **sem alterar nenhuma regra de negócio**
- ✅ O código de domínio **não sabe que FastAPI ou SQLAlchemy existem**
- ✅ A aplicação se torna **independente de framework**

---

## 🏛️ Arquitetura Hexagonal em resumo

A ideia central é simples: o domínio define **o que** o sistema faz.  
Os adapters definem **como** o sistema se comunica com o mundo externo.

```
         [ HTTP / CLI / Tests ]
                  │
          ┌───────▼────────┐
          │   Input Port   │  ← interface que o mundo externo usa
          └───────┬────────┘
                  │
     ┌────────────▼─────────────┐
     │       Use Cases          │  ← orquestra o domínio
     │  (Application Layer)     │
     └────────────┬─────────────┘
                  │
          ┌───────▼────────┐
          │    Domain      │  ← entidades, regras, exceções
          └───────┬────────┘
                  │
          ┌───────▼────────┐
          │  Output Port   │  ← interface que o domínio define
          └───────┬────────┘
                  │
     ┌────────────▼─────────────┐
     │  Adapters de Saída       │  ← InMemory, SQLAlchemy, etc.
     └──────────────────────────┘
```

O domínio **nunca aponta para fora**. Quem depende de quem é sempre de fora para dentro.

---

## 📁 Estrutura de pastas

```
hexagonal-architecture-study/
├── app/
│   ├── domain/                  # 🧠 Núcleo da aplicação
│   │   ├── entities/
│   │   │   └── user.py          # Entidade User
│   │   └── exceptions.py        # Exceções de domínio
│   │
│   ├── ports/                   # 🔌 Interfaces (contratos)
│   │   ├── user_repository.py   # Port de saída: repositório
│   │   └── password_hasher.py   # Port de saída: hasher
│   │
│   ├── application/             # ⚙️ Casos de uso
│   │   └── use_cases/
│   │       └── create_user.py
│   │
│   └── adapters/                # 🔧 Implementações concretas
│       ├── repositories/
│       │   └── in_memory_user_repository.py
│       ├── security/
│       │   └── simple_hasher.py
│       └── http/
│           └── api.py           # Adapter de entrada (FastAPI)
│
├── tests/                       # 🧪 Testes focados no núcleo
│   └── applications/
│       └── test_create_user.py
│
├── main.py
└── requirements.txt
```

---

## 🧱 Camadas explicadas

### 🧠 Domain
O coração da aplicação. Não depende de nada externo.  
Contém entidades e exceções que expressam as regras do negócio.

```python
# Exceção de domínio — sem acoplamento com HTTP ou banco
class EmailAlreadyRegisteredError(Exception):
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Email already registered: {email}")
```

---

### 🔌 Ports
Interfaces abstratas que o domínio define para se comunicar com o mundo externo.  
O domínio **define o contrato**. Os adapters **implementam**.

```python
class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]: ...
```

---

### ⚙️ Application (Use Cases)
Orquestra o domínio sem saber qual infraestrutura está sendo usada.  
Depende apenas de abstrações (ports).

```python
class CreateUserUseCase:
    def __init__(
        self,
        repository: UserRepository,
        hasher: PasswordHasher,
    ) -> None:
        self._repository = repository
        self._hasher = hasher

    def execute(self, name: str, email: str, password: str) -> User:
        if self._repository.find_by_email(email):
            raise EmailAlreadyRegisteredError(email)
        ...
```

---

### 🔧 Adapters
Implementações concretas dos ports. Podem ser trocados sem alterar o domínio.

| Port             | Adapter disponível          |
|------------------|-----------------------------|
| `UserRepository` | `InMemoryUserRepository`    |
| `UserRepository` | `SQLAlchemyUserRepository` *(em breve)* |
| `PasswordHasher` | `SimpleHasher`              |
| `PasswordHasher` | `BcryptHasher` *(em breve)* |

---

## 🔄 Trocando adapters sem tocar no domínio

Essa é uma das demonstrações centrais do repositório.  
O use case não sabe — e não precisa saber — qual repositório está sendo usado.

```python
# Ambiente de desenvolvimento / testes
use_case = CreateUserUseCase(
    repository=InMemoryUserRepository(),
    hasher=SimpleHasher(),
)

# Ambiente de produção (mesmo use case, adapters diferentes)
use_case = CreateUserUseCase(
    repository=SQLAlchemyUserRepository(session),
    hasher=BcryptHasher(),
)
```

Zero alteração no `CreateUserUseCase`. Zero alteração no domínio.

---

## 🧪 Testes

Um dos maiores benefícios da arquitetura hexagonal é a **testabilidade do núcleo**.  
Os use cases são testados com adapters em memória — sem banco, sem HTTP, sem mocks complexos.

```python
@pytest.fixture
def use_case():
    return CreateUserUseCase(
        repository=InMemoryUserRepository(),
        hasher=SimpleHasher(),
    )

def test_should_not_allow_duplicate_email(use_case):
    use_case.execute(name="Vitória", email="vitoria@email.com", password="123456")

    with pytest.raises(EmailAlreadyRegisteredError, match="vitoria@email.com"):
        use_case.execute(name="Outra Pessoa", email="vitoria@email.com", password="abcdef")
```

### Rodando os testes

```bash
pytest tests/ -v
```

---

## 🚀 Como rodar o projeto

```bash
# Clone o repositório
git clone https://github.com/vitoriarntrindade/hexagonal-architecture-study.git
cd hexagonal-architecture-study

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Rode a aplicação
python -m app.main
```

---

## 🏆 O que este projeto demonstra

| Conceito                        | Como é demonstrado                                      |
|---------------------------------|---------------------------------------------------------|
| Isolamento do domínio           | `domain/` não importa nada de framework                 |
| Inversão de dependência         | Use cases dependem de abstrações, não implementações    |
| Testabilidade sem infraestrutura| Testes rodam com repositório em memória                 |
| Substituição de adapters        | Mesma interface, implementações diferentes              |
| Exceções de domínio             | `EmailAlreadyRegisteredError` no lugar de `ValueError`  |

---

## 🔄 Evolução do projeto

Este repositório está em evolução contínua. O objetivo é demonstrar  
como uma aplicação cresce **sem comprometer o núcleo arquitetural**.

Próximos passos planejados:

- [ ] Adapter SQLAlchemy para `UserRepository`
- [ ] Migrations com Alembic
- [ ] Adapter Bcrypt para `PasswordHasher`
- [ ] Injeção de dependência com `dependency-injector` ou similar
- [ ] Melhorias no tratamento de exceções na camada HTTP
- [ ] Novos casos de uso (`GetUser`, `ListUsers`)
- [ ] Configuração de ambiente com `pydantic-settings`

> Algumas simplificações foram feitas propositalmente para fins didáticos,  
> como o uso de `SimpleHasher` e repositório em memória como padrão.  
> Elas serão evoluídas gradualmente, sempre preservando o isolamento do domínio.

---

## 📚 Referências

- [Alistair Cockburn — Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Martin Fowler — Patterns of Enterprise Application Architecture](https://martinfowler.com/books/eaa.html)
- [Clean Architecture — Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)