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

    def __init__(self) -> None:
        self._max_tries: int = 3

    @abstractmethod
    def get_host_index(self, prev_host_index: Optional[int] = None) -> int:
        raise NotImplementedError


class SingleHostResolver(HostResolver):
    """Single host resolver."""

    def get_host_index(self, prev_host_index: Optional[int] = None) -> int:
        return 0


class RandomHostResolver(HostResolver):
    """Random host resolver."""

    def __init__(self, host_count: int) -> None:
        self._max = host_count - 1
        self._max_tries = host_count * 3
        self._prev_host_indexes: Set[int] = set()

    def get_host_index(self, prev_host_index: Optional[int] = None) -> int:
        if prev_host_index is not None:
            if len(self._prev_host_indexes) == self._max:
                self._prev_host_indexes.clear()

            self._prev_host_indexes.add(prev_host_index)

        host_index = None
        while host_index is None or host_index in self._prev_host_indexes:
            host_index = random.randint(0, self._max)

        return host_index


class RoundRobinHostResolver(HostResolver):
    """Round-robin host resolver."""

    def __init__(self, host_count: int) -> None:
        self._max_tries = host_count * 3
        self._index = -1
        self._count = host_count

    def get_host_index(self, prev_host_index: Optional[int] = None) -> int:
        self._index = (self._index + 1) % self._count
        return self._index
