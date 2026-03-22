"""Use case for listing users with pagination."""

from typing import List, Tuple

from app.domain.entities.user import User
from app.ports.user_repository import UserRepository
from app.ports.cache import Cache


class ListUsersUseCase:
    """Return a paginated list of users.

    This use case demonstrates a read/query operation separated from
    command use cases and shows how caching can be applied.
    """

    def __init__(self, user_repository: UserRepository, cache: Cache | None = None) -> None:
        """Initialize with a repository and optional cache.

        Args:
            user_repository: Port for reading users.
            cache: Optional cache port to speed up repeated queries.
        """
        self.user_repository = user_repository
        self.cache = cache

    def execute(self, page: int = 1, size: int = 10) -> Tuple[List[User], int]:
        """Return users for the requested page and the total count.

        Args:
            page: 1-based page number.
            size: Number of items per page.

        Returns:
            A tuple with the list of users for the page and the total user count.
        """
        page = max(1, page)
        size = max(1, size)
        cache_key = f"users:page={page}:size={size}"

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        users, total = self.user_repository.list(page=page, size=size)

        if self.cache:
            self.cache.set(cache_key, (users, total), ttl=30)

        return users, total
