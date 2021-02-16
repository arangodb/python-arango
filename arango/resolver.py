__all__ = [
    "HostResolver",
    "SingleHostResolver",
    "RandomHostResolver",
    "RoundRobinHostResolver",
]

import random
from abc import ABC, abstractmethod


class HostResolver(ABC):  # pragma: no cover
    """Abstract base class for host resolvers."""

    @abstractmethod
    def get_host_index(self) -> int:
        raise NotImplementedError


class SingleHostResolver(HostResolver):
    """Single host resolver."""

    def get_host_index(self) -> int:
        return 0


class RandomHostResolver(HostResolver):
    """Random host resolver."""

    def __init__(self, host_count: int) -> None:
        self._max = host_count - 1

    def get_host_index(self) -> int:
        return random.randint(0, self._max)


class RoundRobinHostResolver(HostResolver):
    """Round-robin host resolver."""

    def __init__(self, host_count: int) -> None:
        self._index = -1
        self._count = host_count

    def get_host_index(self) -> int:
        self._index = (self._index + 1) % self._count
        return self._index
