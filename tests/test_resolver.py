from arango.resolver import (
    RandomHostResolver,
    RoundRobinHostResolver,
    SingleHostResolver,
)


def test_resolver_single_host():
    resolver = SingleHostResolver()
    for _ in range(20):
        assert resolver.get_host_index() == 0


def test_resolver_random_host():
    resolver = RandomHostResolver(10)
    for _ in range(20):
        assert 0 <= resolver.get_host_index() < 10

    resolver = RandomHostResolver(2)
    index_a = resolver.get_host_index()
    index_b = resolver.get_host_index(prev_host_index=index_a)
    index_c = resolver.get_host_index(prev_host_index=index_b)
    assert index_c in [index_a, index_b]

    resolver = RandomHostResolver(3)
    index_a = resolver.get_host_index()
    index_b = resolver.get_host_index(prev_host_index=index_a)
    index_c = resolver.get_host_index(prev_host_index=index_b)
    assert index_c not in [index_a, index_b]


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
