from __future__ import absolute_import, unicode_literals

import pytest

from arango.errno import (
    FORBIDDEN,
    HTTP_UNAUTHORIZED,
    DATABASE_NOT_FOUND
)
from arango.exceptions import (
    WALConfigureError,
    WALFlushError,
    WALPropertiesError,
    WALTransactionListError,
    WALTickRangesError,
    WALLastTickError,
    WALTailError
)
from tests.helpers import assert_raises


def test_wal_misc_methods(sys_db, bad_db):
    try:
        sys_db.wal.properties()
    except WALPropertiesError as err:
        if err.http_code == 501:
            pytest.skip('WAL not implemented')

    # Test get properties
    properties = sys_db.wal.properties()
    assert 'oversized_ops' in properties
    assert 'log_size' in properties
    assert 'historic_logs' in properties
    assert 'reserve_logs' in properties
    assert 'throttle_wait' in properties
    assert 'throttle_limit' in properties

    # Test get properties with bad database
    with assert_raises(WALPropertiesError) as err:
        bad_db.wal.properties()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}

    # Test configure properties
    sys_db.wal.configure(
        historic_logs=15,
        oversized_ops=False,
        log_size=30000000,
        reserve_logs=5,
        throttle_limit=0,
        throttle_wait=16000
    )
    properties = sys_db.wal.properties()
    assert properties['historic_logs'] == 15
    assert properties['oversized_ops'] is False
    assert properties['log_size'] == 30000000
    assert properties['reserve_logs'] == 5
    assert properties['throttle_limit'] == 0
    assert properties['throttle_wait'] == 16000

    # Test configure properties with bad database
    with assert_raises(WALConfigureError) as err:
        bad_db.wal.configure(log_size=2000000)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}

    # Test get transactions
    result = sys_db.wal.transactions()
    assert 'count' in result
    assert 'last_collected' in result

    # Test get transactions with bad database
    with assert_raises(WALTransactionListError) as err:
        bad_db.wal.transactions()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}

    # Test flush
    result = sys_db.wal.flush(garbage_collect=False, sync=False)
    assert isinstance(result, bool)

    # Test flush with bad database
    with assert_raises(WALFlushError) as err:
        bad_db.wal.flush(garbage_collect=False, sync=False)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_wal_tick_ranges(sys_db, bad_db, cluster):
    if cluster:
        pytest.skip('Not tested in a cluster setup')

    result = sys_db.wal.tick_ranges()
    assert 'server' in result
    assert 'time' in result
    assert 'tick_min' in result
    assert 'tick_max' in result

    # Test tick_ranges with bad database
    with assert_raises(WALTickRangesError) as err:
        bad_db.wal.tick_ranges()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_wal_last_tick(sys_db, bad_db, cluster):
    if cluster:
        pytest.skip('Not tested in a cluster setup')

    result = sys_db.wal.last_tick()
    assert 'time' in result
    assert 'tick' in result
    assert 'server' in result

    # Test last_tick with bad database
    with assert_raises(WALLastTickError) as err:
        bad_db.wal.last_tick()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_wal_tail(sys_db, bad_db, cluster):
    if cluster:
        pytest.skip('Not tested in a cluster setup')

    result = sys_db.wal.tail(
        lower=0,
        upper=1000000,
        last_scanned=0,
        all_databases=True,
        chunk_size=1000000,
        syncer_id=None,
        server_id=None,
        client_info='test',
        barrier_id=None
    )
    assert 'content' in result
    assert 'last_tick' in result
    assert 'last_scanned' in result
    assert 'last_included' in result
    assert isinstance(result['check_more'], bool)
    assert isinstance(result['from_present'], bool)

    # Test tick_ranges with bad database
    with assert_raises(WALTailError) as err:
        bad_db.wal.tail()
    assert err.value.http_code == HTTP_UNAUTHORIZED
