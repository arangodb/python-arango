from __future__ import absolute_import, unicode_literals

from arango.resolver import (
    SingleHostResolver,
    RandomHostResolver,
    RoundRobinHostResolver
)


def test_resolver_single_host():
    resolver = SingleHostResolver()
    for _ in range(20):
        assert resolver.get_host_index() == 0


def test_resolver_random_host():
    resolver = RandomHostResolver(10)
    for _ in range(20):
        assert 0 <= resolver.get_host_index() < 10


def test_resolver_round_robin():
    resolver = RoundRobinHostResolver(10)
    assert resolver.get_host_index() == 0
    assert resolver.get_host_index() == 1
    assert resolver.get_host_index() == 2
    assert resolver.get_host_index() == 3
    assert resolver.get_host_index() == 4
    assert resolver.get_host_index() == 5
    assert resolver.get_host_index() == 6
    assert resolver.get_host_index() == 7
    assert resolver.get_host_index() == 8
    assert resolver.get_host_index() == 9
    assert resolver.get_host_index() == 0
