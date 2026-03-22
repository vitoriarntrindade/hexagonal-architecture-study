"""Shared pytest fixtures and configuration for the test suite.

Environment variables are injected at the **module level** (before any app
module is imported) so that ``app.infrastructure.database`` — which reads
``DATABASE_URL`` lazily via ``get_settings()`` — always finds the test values.

What this guarantees
- Tokens issued during tests are verifiable (same JWT secret everywhere).
- No ``KeyError: DATABASE_URL`` during test collection.
- PyJWT ``InsecureKeyLengthWarning`` is silenced (secret >= 32 bytes).
- SQLAlchemy tables exist in the in-memory DB before any test runs.
"""

from __future__ import annotations

import os
from typing import Generator

import pytest

# ---------------------------------------------------------------------------
# Inject env vars at module import time — before any app module is imported.
# ---------------------------------------------------------------------------
_TEST_JWT_SECRET = "test-secret-key-32-bytes-long-ok!"

os.environ.setdefault("JWT_SECRET", _TEST_JWT_SECRET)
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("ENV", "test")


@pytest.fixture(autouse=True, scope="session")
def set_test_env() -> Generator[None, None, None]:
    """Clear settings/engine caches and create DB tables once per session.

    The env vars are already set at module level above.  This fixture:
    1. Clears ``get_settings()`` and ``_engine()`` caches so the test values
       are always picked up even when a previous session left cached state.
    2. Calls ``Base.metadata.create_all`` so every SQLAlchemy-backed test
       finds the ``users`` table ready to use — no Alembic migrations needed.
    """
    from app.config import get_settings
    from app.infrastructure.database import _engine
    from app.adapters.repositories.models import Base

    get_settings.cache_clear()
    _engine.cache_clear()

    # Build tables in the in-memory SQLite DB.
    engine = _engine()
    Base.metadata.create_all(engine)

    yield

    # Teardown: drop tables and clear caches for a clean slate.
    Base.metadata.drop_all(engine)
    get_settings.cache_clear()
    _engine.cache_clear()

