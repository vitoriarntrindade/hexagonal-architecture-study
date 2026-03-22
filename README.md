
#  Hexagonal Architecture Study

> Estudo prático de **Arquitetura Hexagonal (Ports and Adapters)** usando **Python + FastAPI**.  
> O objetivo deste projeto é demonstrar **boas práticas de engenharia de software**, isolamento do domínio e arquitetura testável.

---

## 📚 Sumário

- 🎯 [Sobre o projeto](#-sobre-o-projeto)
- 🏛️ [Arquitetura](#-arquitetura)
- 🧰 [Tecnologias](#-tecnologias)
- 📂 [Estrutura do projeto](#-estrutura-do-projeto)
- ⚡ [Quick Start](#-quick-start)
- ⚙️ [Configuração de ambiente](#-configuração-de-ambiente)
- 🚀 [Rodando a API](#-rodando-a-api)
- 🧪 [Testes](#-testes)
- 🛠️ [Makefile](#-makefile)
- ✅ [Boas práticas aplicadas](#-boas-práticas-aplicadas)
- 🔁 [CI / Pipeline](#-ci--pipeline)
- 📈 [Evolução do projeto](#-evolução-do-projeto)
- 📚 [Referências](#-referências)

---

# 🎯 Sobre o projeto
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

# 🏛 Arquitetura

Este projeto segue o padrão **Ports and Adapters (Hexagonal Architecture)**.

A lógica de negócio fica **no centro**, enquanto infraestrutura fica **nas bordas**.

```mermaid
flowchart TD

A["HTTP / CLI / Tests"]
B["Input Adapters (FastAPI)"]
C["Application (Use Cases)"]
D["Domain (Entities / Exceptions)"]
E["Ports (Interfaces)"]
F["Output Adapters<br/>(SQLAlchemy / Cache / Security)"]

A --> B
B --> C
C --> D
D --> E
E --> F
```


### Princípios aplicados

- Inversão de dependência
- Isolamento do domínio
- Testabilidade
- Substituição de infraestrutura
- Arquitetura limpa

---

# 🧰 Tecnologias

| Tecnologia | Descrição |
|------------|-----------|
| Python | Linguagem principal |
| FastAPI | Framework HTTP |
| SQLAlchemy | ORM |
| PostgreSQL | Banco de dados |
| Pytest | Testes |
| Testcontainers | Testes de integração |
| Alembic | Migrations |
| JWT | Autenticação |
| GitHub Actions | CI pipeline |
| Pre-commit | Qualidade de código |

---

# 📂 Estrutura do projeto

````
├── alembic.ini                    # Configuração do Alembic (migrations do banco)
├── Makefile                       # Comandos utilitários para desenvolvimento (run, test, lint, check)
├── pyproject.toml                 # Configuração de ferramentas Python (ruff, pytest, etc.)
├── requirements.txt               # Dependências do projeto
├── README.md                      # Documentação principal do repositório
│
├── migrations/                    # Migrations do banco gerenciadas pelo Alembic
│   ├── env.py                     # Configuração do ambiente de migrations
│   ├── script.py.mako             # Template usado pelo Alembic para gerar migrations
│   └── versions/                  # Histórico de migrations do banco
│
├── app/                           # Código principal da aplicação
│
│   ├── __init__.py                # Marca o diretório como módulo Python
│   ├── config.py                  # Configuração da aplicação (settings via env)
│   ├── main.py                    # Ponto de entrada da aplicação FastAPI
│
│   ├── domain/                    # 🧠 Camada de domínio (núcleo da aplicação)
│   │   ├── __init__.py
│   │   ├── exceptions.py          # Exceções de domínio (erros de negócio)
│   │   └── entities/
│   │       ├── __init__.py
│   │       └── user.py            # Entidade User e suas regras básicas
│
│   ├── application/               # ⚙️ Camada de aplicação (casos de uso)
│   │   ├── __init__.py
│   │   └── use_cases/
│   │       ├── __init__.py
│   │       ├── create_user.py         # Caso de uso: criação de usuário
│   │       ├── authenticate_user.py   # Caso de uso: autenticação de usuário
│   │       ├── list_users.py          # Caso de uso: listagem de usuários
│   │       ├── get_user_by_email.py   # Caso de uso: busca de usuário por email
│   │       ├── update_user.py         # Caso de uso: atualização de usuário
│   │       └── delete_user.py         # Caso de uso: remoção de usuário
│
│   ├── ports/                     # 🔌 Contratos (interfaces) definidos pelo domínio
│   │   ├── __init__.py
│   │   ├── user_repository.py     # Interface do repositório de usuários
│   │   ├── password_hasher.py     # Interface para hashing de senha
│   │   ├── auth_token.py          # Interface para geração/validação de tokens
│   │   └── cache.py               # Interface de cache
│
│   ├── adapters/                  # 🔧 Implementações concretas dos ports
│   │   ├── __init__.py
│
│   │   ├── repositories/          # Adapters de persistência
│   │   │   ├── __init__.py
│   │   │   ├── models.py                  # Modelos ORM SQLAlchemy
│   │   │   ├── in_memory_user_repository.py # Implementação em memória (testes/dev)
│   │   │   └── sqlalchemy_user_repository.py # Implementação real com SQLAlchemy
│
│   │   ├── security/              # Implementações de hashing de senha
│   │   │   ├── __init__.py
│   │   │   ├── simple_hasher.py   # Hasher simples (uso didático/testes)
│   │   │   └── bcrypt_hasher.py   # Hasher seguro com bcrypt
│
│   │   ├── auth/                  # Implementações de autenticação
│   │   │   └── jwt_adapter.py     # Implementação JWT do port de autenticação
│
│   │   ├── cache/                 # Implementações de cache
│   │   │   └── in_memory_cache.py # Cache em memória (substituível por Redis etc.)
│
│   │   └── http/                  # Adapter de entrada (API HTTP)
│   │       ├── __init__.py
│   │       ├── api.py                     # Criação da aplicação FastAPI
│   │       ├── schemas.py                 # Schemas Pydantic usados pela API
│   │       ├── dependencies.py            # Dependências compartilhadas da API
│   │       ├── dependencies_auth.py       # Dependências relacionadas à autenticação
│   │       ├── dependencies_list.py       # Dependências específicas de listagem
│   │       ├── dependencies_update_delete.py # Dependências para update/delete
│   │       └── routers/
│   │           ├── __init__.py
│   │           └── users.py               # Rotas HTTP de usuários
│
│   └── infrastructure/            # Infraestrutura técnica da aplicação
│       ├── __init__.py
│       └── database.py            # Configuração do SQLAlchemy e conexão com DB
│
└── tests/                         # 🧪 Suíte de testes
    ├── __init__.py
    ├── conftest.py                # Fixtures globais do pytest
│
    ├── application/               # Testes da camada de aplicação
│
    ├── applications/              # Testes dos casos de uso
│   │   ├── test_create_user.py
│   │   └── test_get_user_by_email.py
│
    ├── http/                      # Testes da API
│   │   ├── test_api.py
│   │   ├── test_auth.py
│   │   ├── test_error_responses.py
│   │   ├── test_list_users.py
│   │   ├── test_smoke.py
│   │   └── test_user_endpoints.py
│
    ├── repositories/              # Testes de integração do repositório
│   │   └── test_sqlalchemy_user_repository_integration.py
│
    └── security/                  # Testes das implementações de hashing
        └── test_hashers.py
````

---

# ⚡ Quick Start

### Clone o repositório

```git clone https://github.com/vitoriarntrindade/hexagonal-architecture-study.git```

```cd hexagonal-architecture-study```

---

# ⚙️ Configuração de ambiente

Crie o arquivo `.env` baseado no `.env.example`.

Exemplo:

- DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hexagonal
- JWT_SECRET=super-secret-key
- JWT_ALGORITHM=HS256

---

# 📦 Instalação de dependências

`` pip install -r requirements.txt``

ou

`` make install ``

---

# 🚀 Rodando a API

``make run``

ou manualmente:

``uvicorn app.main:app --reload``

API disponível em:

http://localhost:8000/docs

---

# 🧪 Testes

O projeto possui dois tipos de testes:

### Unit Tests

pytest tests/

### Integration Tests

pytest -m integration

---

# 🛠 Makefile

| Comando | Descrição |
|--------|-----------|
| make install | Instala dependências |
| make run | Executa a API |
| make test | Executa testes |
| make lint | Executa ruff |
| make check | Executa lint + testes |

---

# 🧹 Qualidade de código

Este projeto usa **pre-commit hooks** para manter o padrão de código.

Ferramentas utilizadas:

- Ruff (lint)
- Pytest

Instalar hooks:

pre-commit install

---

# 🔁 CI / Pipeline

O projeto possui **CI configurado com GitHub Actions**.

Pipeline executa:

1. Lint com Ruff
2. Testes unitários
3. Testes de integração com PostgreSQL via Testcontainers

Arquivo:

.github/workflows/ci.yml

---

# 🏆 Boas práticas aplicadas

| Prática | Implementação |
|------|------|
| Hexagonal Architecture | Separação domain/application/adapters |
| Dependency inversion | Use cases dependem de ports |
| Domain isolation | Domain não depende de framework |
| Testability | Testes sem infraestrutura |
| Integration tests | Testcontainers |
| CI/CD | GitHub Actions |
| Code quality | Ruff + Pre-commit |
| Configuration management | Settings via env |

---

# 🔄 Evolução do projeto

Este projeto continua evoluindo para demonstrar arquitetura em sistemas reais.

Possíveis próximos passos:

- cache Redis
- observabilidade (OpenTelemetry)
- rate limiting
- métricas
- containerização com Docker
- health checks
- dependency injection container

---

# 📚 Referências

- Hexagonal Architecture — Alistair Cockburn
- Clean Architecture — Robert C. Martin
- FastAPI Documentation
- SQLAlchemy Documentation