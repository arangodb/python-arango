from __future__ import absolute_import, unicode_literals

import pytest

from arango import ArangoClient

arango_client = ArangoClient()
wal = arango_client.wal


@pytest.mark.order1
def test_wal_properties():
    properties = wal.properties()
    assert 'oversized_ops' in properties
    assert 'log_size' in properties
    assert 'historic_logs' in properties
    assert 'reserve_logs' in properties


@pytest.mark.order2
def test_wal_configure():
    wal.configure(
        historic_logs=15,
        oversized_ops=False,
        log_size=30000000,
        reserve_logs=5,
        throttle_limit=1000,
        throttle_wait=16000
    )
    properties = arango_client.wal.properties()
    assert properties['historic_logs'] == 15
    assert properties['oversized_ops'] is False
    assert properties['log_size'] == 30000000
    assert properties['reserve_logs'] == 5
    assert properties['throttle_limit'] == 1000
    assert properties['throttle_wait'] == 16000


@pytest.mark.order3
def test_wal_list_transactions():
    result = wal.transactions()
    assert 'count' in result
    assert 'last_sealed' in result
    assert 'last_collected' in result


# @pytest.mark.order4
# def test_flush_wal():
#     assert isinstance(wal.flush(), bool)
