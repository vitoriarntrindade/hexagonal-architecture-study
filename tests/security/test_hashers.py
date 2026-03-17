"""Unit tests for BcryptHasher and SimpleHasher adapters."""

import pytest

from app.adapters.security.bcrypt_hasher import BcryptHasher
from app.adapters.security.simple_hasher import SimpleHasher
from app.ports.password_hasher import PasswordHasher


class TestBcryptHasher:
    """Tests for the BcryptHasher adapter."""

    @pytest.fixture
    def hasher(self) -> BcryptHasher:
        return BcryptHasher()

    def test_should_implement_password_hasher_port(self, hasher: BcryptHasher) -> None:
        assert isinstance(hasher, PasswordHasher)

    def test_should_return_a_hash_different_from_plain_text(
        self, hasher: BcryptHasher
    ) -> None:
        hashed = hasher.hash("my_password")

        assert hashed != "my_password"

    def test_should_produce_different_hashes_for_same_password(
        self, hasher: BcryptHasher
    ) -> None:
        """Bcrypt generates a unique salt on each call."""
        hash_a = hasher.hash("my_password")
        hash_b = hasher.hash("my_password")

        assert hash_a != hash_b

    def test_should_verify_correct_password(self, hasher: BcryptHasher) -> None:
        hashed = hasher.hash("my_password")

        assert hasher.verify("my_password", hashed) is True

    def test_should_reject_wrong_password(self, hasher: BcryptHasher) -> None:
        hashed = hasher.hash("my_password")

        assert hasher.verify("wrong_password", hashed) is False


class TestSimpleHasher:
    """Tests for the SimpleHasher adapter."""

    @pytest.fixture
    def hasher(self) -> SimpleHasher:
        return SimpleHasher()

    def test_should_implement_password_hasher_port(self, hasher: SimpleHasher) -> None:
        assert isinstance(hasher, PasswordHasher)

    def test_should_return_a_hash_different_from_plain_text(
        self, hasher: SimpleHasher
    ) -> None:
        hashed = hasher.hash("my_password")

        assert hashed != "my_password"

    def test_should_produce_same_hash_for_same_password(
        self, hasher: SimpleHasher
    ) -> None:
        """SHA-256 is deterministic — same input always yields same output."""
        hash_a = hasher.hash("my_password")
        hash_b = hasher.hash("my_password")

        assert hash_a == hash_b

    def test_should_verify_correct_password(self, hasher: SimpleHasher) -> None:
        hashed = hasher.hash("my_password")

        assert hasher.verify("my_password", hashed) is True

    def test_should_reject_wrong_password(self, hasher: SimpleHasher) -> None:
        hashed = hasher.hash("my_password")

        assert hasher.verify("wrong_password", hashed) is False
