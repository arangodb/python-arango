__all__ = [
    "HostResolver",
    "FallbackHostResolver",
    "PeriodicHostResolver",
    "SingleHostResolver",
    "RandomHostResolver",
    "RoundRobinHostResolver",
]

import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Optional, Set


class HostResolver(ABC):  # pragma: no cover
    """Abstract base class for host resolvers."""

    def __init__(self, host_count: int = 1, max_tries: Optional[int] = None) -> None:
        max_tries = max_tries or host_count * 3
        if max_tries < host_count:
            raise ValueError("max_tries cannot be less than host_count")

        self._host_count = host_count
        self._max_tries = max_tries

    @abstractmethod
    def get_host_index(self, indexes_to_filter: Optional[Set[int]] = None) -> int:
        raise NotImplementedError

    @property
    def host_count(self) -> int:
        return self._host_count

    @property
    def max_tries(self) -> int:
        return self._max_tries


class SingleHostResolver(HostResolver):
    """Single host resolver."""

    def get_host_index(self, indexes_to_filter: Optional[Set[int]] = None) -> int:
        return 0


class RandomHostResolver(HostResolver):
    """Random host resolver."""

    def __init__(self, host_count: int, max_tries: Optional[int] = None) -> None:
        super().__init__(host_count, max_tries)

    def get_host_index(self, indexes_to_filter: Optional[Set[int]] = None) -> int:
        host_index = None
        indexes_to_filter = indexes_to_filter or set()
        while host_index is None or host_index in indexes_to_filter:
            host_index = random.randint(0, self.host_count - 1)

        return host_index


class RoundRobinHostResolver(HostResolver):
    """Round-robin host resolver."""

    def __init__(self, host_count: int, max_tries: Optional[int] = None) -> None:
        super().__init__(host_count, max_tries)
        self._index = -1

    def get_host_index(self, indexes_to_filter: Optional[Set[int]] = None) -> int:
        self._index = (self._index + 1) % self.host_count
        return self._index


class PeriodicHostResolver(HostResolver):
    """
    Changes the host every N requests.
    An optional timeout may be applied between host changes,
    such that all coordinators get a chance to update their view of the agency.
    For example, if one coordinator creates a database, the others may not be
    immediately aware of it. If the timeout is set to 1 second, then the host
    resolver waits for 1 second before changing the host.
    """

    def __init__(
        self,
        host_count: int,
        max_tries: Optional[int] = None,
        requests_period: int = 100,
        switch_timeout: float = 0,
    ) -> None:
        super().__init__(host_count, max_tries)
        self._requests_period = requests_period
        self._switch_timeout = switch_timeout
        self._req_count = 0
        self._index = 0

    def get_host_index(self, indexes_to_filter: Optional[Set[int]] = None) -> int:
        indexes_to_filter = indexes_to_filter or set()
        self._req_count = (self._req_count + 1) % self._requests_period
        if self._req_count == 0 or self._index in indexes_to_filter:
            self._index = (self._index + 1) % self.host_count
            while self._index in indexes_to_filter:
                self._index = (self._index + 1) % self.host_count
            self._req_count = 0
            time.sleep(self._switch_timeout)
        return self._index


class FallbackHostResolver(HostResolver):
    """
    Fallback host resolver.
    If the current host fails, the next one is used.
    """

    def __init__(self, host_count: int, max_tries: Optional[int] = None) -> None:
        super().__init__(host_count, max_tries)
        self._index = 0
        self._logger = logging.getLogger(self.__class__.__name__)

    def get_host_index(self, indexes_to_filter: Optional[Set[int]] = None) -> int:
        indexes_to_filter = indexes_to_filter or set()
        while self._index in indexes_to_filter:
            self._index = (self._index + 1) % self.host_count
            self._logger.debug(f"Trying fallback on host {self._index}")
        return self._index
