from __future__ import absolute_import, unicode_literals

import pytest

from arango import ArangoClient
from arango.exceptions import (
    WALConfigureError,
    WALFlushError,
    WALPropertiesError,
    WALTransactionListError
)

from tests.utils import generate_user_name, generate_db_name

arango_client = ArangoClient()
username = generate_user_name()
user = arango_client.create_user(username, 'password')
db_name = generate_db_name()
db = arango_client.create_database(db_name)


def teardown_module(*_):
    arango_client.delete_user(username, ignore_missing=True)


@pytest.mark.order1
def test_wal_properties():
    properties = arango_client.wal.properties()
    assert 'ArangoDB write-ahead log' in repr(arango_client.wal)
    assert 'oversized_ops' in properties
    assert 'log_size' in properties
    assert 'historic_logs' in properties
    assert 'reserve_logs' in properties


@pytest.mark.order2
def test_wal_configure():
    arango_client.wal.configure(
        historic_logs=15,
        oversized_ops=False,
        log_size=30000000,
        reserve_logs=5,
        throttle_limit=0,
        throttle_wait=16000
    )
    properties = arango_client.wal.properties()
    assert properties['historic_logs'] == 15
    assert properties['oversized_ops'] is False
    assert properties['log_size'] == 30000000
    assert properties['reserve_logs'] == 5
    assert properties['throttle_limit'] == 0
    assert properties['throttle_wait'] == 16000


@pytest.mark.order3
def test_wal_list_transactions():
    result = arango_client.wal.transactions()
    assert 'count' in result
    assert 'last_sealed' in result
    assert 'last_collected' in result


@pytest.mark.order4
def test_flush_wal():
    result = arango_client.wal.flush(garbage_collect=False, sync=False)
    assert isinstance(result, bool)


@pytest.mark.order5
def test_wal_errors():
    client_with_bad_user = ArangoClient(
        username=username,
        password='incorrect',
        verify=False
    )
    bad_wal = client_with_bad_user.wal
    with pytest.raises(WALPropertiesError):
        bad_wal.properties()

    with pytest.raises(WALConfigureError):
        bad_wal.configure(log_size=2000000)

    with pytest.raises(WALTransactionListError):
        bad_wal.transactions()

    with pytest.raises(WALFlushError):
        bad_wal.flush(garbage_collect=False, sync=False)


@pytest.mark.order6
def test_wal_properties_db_level():
    properties = db.wal.properties()
    assert 'ArangoDB write-ahead log' in repr(arango_client.wal)
    assert 'oversized_ops' in properties
    assert 'log_size' in properties
    assert 'historic_logs' in properties
    assert 'reserve_logs' in properties


@pytest.mark.order7
def test_wal_configure_db_level():
    db.wal.configure(
        historic_logs=15,
        oversized_ops=False,
        log_size=30000000,
        reserve_logs=5,
        throttle_limit=0,
        throttle_wait=16000
    )
    properties = db.wal.properties()
    assert properties['historic_logs'] == 15
    assert properties['oversized_ops'] is False
    assert properties['log_size'] == 30000000
    assert properties['reserve_logs'] == 5
    assert properties['throttle_limit'] == 0
    assert properties['throttle_wait'] == 16000


@pytest.mark.order8
def test_wal_list_transactions_db_level():
    result = db.wal.transactions()
    assert 'count' in result
    assert 'last_sealed' in result
    assert 'last_collected' in result


@pytest.mark.order9
def test_flush_wal_db_level():
    result = db.wal.flush(garbage_collect=False, sync=False)
    assert isinstance(result, bool)


@pytest.mark.order10
def test_wal_errors_db_level():
    bad_wal = ArangoClient(
        username=username,
        password='incorrect',
        verify=False
    ).db(db_name).wal
    with pytest.raises(WALPropertiesError):
        bad_wal.properties()

    with pytest.raises(WALConfigureError):
        bad_wal.configure(log_size=2000000)

    with pytest.raises(WALTransactionListError):
        bad_wal.transactions()

    with pytest.raises(WALFlushError):
        bad_wal.flush(garbage_collect=False, sync=False)