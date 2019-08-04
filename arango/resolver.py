from __future__ import absolute_import, unicode_literals

__all__ = [
    'SingleHostResolver',
    'RandomHostResolver',
    'RoundRobinHostResolver',
]

import random
from abc import ABCMeta, abstractmethod


class HostResolver(object):  # pragma: no cover
    """Abstract base class for host resolvers."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_host_index(self):
        raise NotImplementedError


class SingleHostResolver(HostResolver):
    """Single host resolver."""

    def get_host_index(self):
        return 0


class RandomHostResolver(HostResolver):
    """Random host resolver."""

    def __init__(self, host_count):
        self._max = host_count - 1

    def get_host_index(self):
        return random.randint(0, self._max)


class RoundRobinHostResolver(HostResolver):
    """Round-robin host resolver."""

    def __init__(self, host_count):
        self._index = -1
        self._count = host_count

    def get_host_index(self):
        self._index = (self._index + 1) % self._count
        return self._index
