__all__ = [
    "HostResolver",
    "SingleHostResolver",
    "RandomHostResolver",
    "RoundRobinHostResolver",
]

import random
from abc import ABC, abstractmethod
from typing import Optional, Set


class HostResolver(ABC):  # pragma: no cover
    """Abstract base class for host resolvers."""

    def __init__(self, host_count: int = 1, max_tries: int = 3) -> None:
        if max_tries < host_count:
            raise ValueError("max_tries cannot be less than host_count")

        self._host_count = host_count
        self._max_tries = max_tries

    @abstractmethod
    def get_host_index(self, indexes_to_filter: Set[int] = set()) -> int:
        raise NotImplementedError

    @property
    def host_count(self) -> int:
        return self._host_count

    @property
    def max_tries(self) -> int:
        return self._max_tries


class SingleHostResolver(HostResolver):
    """Single host resolver."""

    def get_host_index(self, indexes_to_filter: Set[int] = set()) -> int:
        return 0


class RandomHostResolver(HostResolver):
    """Random host resolver."""

    def __init__(self, host_count: int, max_tries: Optional[int] = None) -> None:
        super().__init__(host_count, max_tries or host_count * 3)

    def get_host_index(self, indexes_to_filter: Set[int] = set()) -> int:
        host_index = None
        while host_index is None or host_index in indexes_to_filter:
            host_index = random.randint(0, self.host_count - 1)

        return host_index


class RoundRobinHostResolver(HostResolver):
    """Round-robin host resolver."""

    def __init__(self, host_count: int, max_tries: Optional[int] = None) -> None:
        super().__init__(host_count, max_tries or host_count * 3)
        self._index = -1

    def get_host_index(self, indexes_to_filter: Set[int] = set()) -> int:
        self._index = (self._index + 1) % self.host_count
        return self._index
