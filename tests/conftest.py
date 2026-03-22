"""Shared pytest fixtures and configuration for the test suite.

The ``autouse`` session fixture below sets a deterministic JWT secret for all
tests so that:
- tokens issued by any adapter are verifiable by any other adapter instance
  within the same test run;
- the PyJWT ``InsecureKeyLengthWarning`` is silenced (secret is >= 32 bytes);
- tests do **not** need to manually override ``get_current_user``.
"""

from __future__ import annotations

import os
import pytest

# Deterministic 32-byte test secret — safe only for testing.
_TEST_JWT_SECRET = "test-secret-key-32-bytes-long-ok!"


@pytest.fixture(autouse=True, scope="session")
def set_test_env() -> None:
    """Inject test environment variables before any test module is imported.

    This fixture runs once per test session and ensures all calls to
    ``get_settings()`` inside the application return the test values.

    The ``lru_cache`` on ``get_settings`` is cleared before and after
    injection so the patched values are always picked up.
    """
    from app.config import get_settings

    # Clear any cached settings from a previous run / import.
    get_settings.cache_clear()

    os.environ.setdefault("JWT_SECRET", _TEST_JWT_SECRET)
    os.environ.setdefault("ENV", "test")

    yield  # run all tests

    # Restore: clear cache so other processes / sessions start fresh.
    get_settings.cache_clear()
