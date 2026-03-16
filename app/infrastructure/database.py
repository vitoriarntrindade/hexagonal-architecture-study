"""Database engine and session factory configuration."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.adapters.repositories.models import Base

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def create_tables() -> None:
    """Create all tables in the database if they do not exist yet."""
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """Return a new database session.

    The caller is responsible for closing the session.
    Prefer using this as a context manager or via dependency injection.
    """
    return SessionLocal()
