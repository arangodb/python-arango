from __future__ import absolute_import, unicode_literals

import pytest

from arango.exceptions import (
    WALConfigureError,
    WALFlushError,
    WALPropertiesError,
    WALTransactionListError
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
    assert err.value.error_code in {11, 1228}

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
    assert err.value.error_code in {11, 1228}

    # Test get transactions
    result = sys_db.wal.transactions()
    assert 'count' in result
    assert 'last_collected' in result

    # Test get transactions with bad database
    with assert_raises(WALTransactionListError) as err:
        bad_db.wal.transactions()
    assert err.value.error_code in {11, 1228}

    # Test flush
    result = sys_db.wal.flush(garbage_collect=False, sync=False)
    assert isinstance(result, bool)

    # Test flush with bad database
    with assert_raises(WALFlushError) as err:
        bad_db.wal.flush(garbage_collect=False, sync=False)
    assert err.value.error_code in {11, 1228}
