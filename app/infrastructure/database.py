"""Database engine and session factory configuration.

The engine is built lazily on first call to ``get_session()`` so that
importing this module never raises ``KeyError`` when ``DATABASE_URL`` is
not yet in the environment (e.g. during test collection before fixtures run).
"""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


@lru_cache(maxsize=1)
def _engine() -> Engine:
    """Build and cache the SQLAlchemy engine from application settings.

    Using ``get_settings()`` here ensures the value is read lazily — after
    the test session fixture has had a chance to inject ``DATABASE_URL`` into
    the environment — instead of at import time.

    Returns:
        A configured ``Engine`` instance.
    """
    from app.config import get_settings

    settings = get_settings()
    return create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
    )


def get_session() -> Session:
    """Return a new database session.

    The caller is responsible for closing the session.
    Prefer using this as a context manager or via dependency injection.

    Returns:
        An active ``Session`` bound to the configured engine.
    """
    factory = sessionmaker(
        bind=_engine(),
        autocommit=False,
        autoflush=False,
    )
    return factory()
