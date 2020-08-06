from __future__ import absolute_import, unicode_literals

import pytest
from six import string_types

from arango.errno import (
    CURSOR_NOT_FOUND,
    FORBIDDEN,
    HTTP_NOT_FOUND,
    HTTP_UNAUTHORIZED,
    DATABASE_NOT_FOUND
)
from arango.exceptions import (
    ReplicationApplierConfigError,
    ReplicationApplierConfigSetError,
    ReplicationApplierStartError,
    ReplicationApplierStateError,
    ReplicationApplierStopError,
    ReplicationClusterInventoryError,
    ReplicationDumpBatchCreateError,
    ReplicationDumpBatchDeleteError,
    ReplicationDumpBatchExtendError,
    ReplicationDumpError,
    ReplicationInventoryError,
    ReplicationLoggerFirstTickError,
    ReplicationLoggerStateError,
    ReplicationMakeSlaveError,
    ReplicationServerIDError,
    ReplicationSyncError
)
from tests.helpers import assert_raises


def test_replication_dump_methods(db, bad_db, col, docs, cluster):
    if cluster:
        pytest.skip('Not tested in a cluster setup')

    result = db.replication.create_dump_batch(ttl=1000)
    assert 'id' in result and 'last_tick' in result
    batch_id = result['id']

    with assert_raises(ReplicationDumpBatchCreateError) as err:
        bad_db.replication.create_dump_batch(ttl=1000)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}

    result = db.replication.dump(
        collection=col.name,
        batch_id=batch_id,
        chunk_size=0,
        deserialize=True
    )
    assert 'content' in result
    assert 'check_more' in result

    with assert_raises(ReplicationDumpError) as err:
        bad_db.replication.dump(
            collection=col.name,
            batch_id=batch_id
        )
    assert err.value.error_code == HTTP_UNAUTHORIZED

    assert db.replication.extend_dump_batch(batch_id, ttl=1000) is True
    with assert_raises(ReplicationDumpBatchExtendError) as err:
        bad_db.replication.extend_dump_batch(batch_id, ttl=1000)
    assert err.value.error_code == HTTP_UNAUTHORIZED

    assert db.replication.delete_dump_batch(batch_id) is True
    with assert_raises(ReplicationDumpBatchDeleteError) as err:
        db.replication.delete_dump_batch(batch_id)
    assert err.value.error_code in {HTTP_NOT_FOUND, CURSOR_NOT_FOUND}


def test_replication_inventory(sys_db, bad_db, cluster):
    if cluster:
        pytest.skip('Not tested in a cluster setup')

    dump_batch = sys_db.replication.create_dump_batch(ttl=1000)
    dump_batch_id = dump_batch['id']

    result = sys_db.replication.inventory(
        batch_id=dump_batch_id,
        include_system=True,
        all_databases=True
    )
    assert isinstance(result, dict)
    assert 'collections' not in result
    assert 'databases' in result
    assert 'state' in result
    assert 'tick' in result

    result = sys_db.replication.inventory(
        batch_id=dump_batch_id,
        include_system=True,
        all_databases=False
    )
    assert isinstance(result, dict)
    assert 'databases' not in result
    assert 'collections' in result
    assert 'state' in result
    assert 'tick' in result

    with assert_raises(ReplicationInventoryError) as err:
        bad_db.replication.inventory(dump_batch_id)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}

    sys_db.replication.delete_dump_batch(dump_batch_id)


def test_replication_logger_state(sys_db, bad_db, cluster):
    if cluster:
        pytest.skip('Not tested in a cluster setup')

    result = sys_db.replication.logger_state()
    assert 'state' in result
    assert 'server' in result

    with assert_raises(ReplicationLoggerStateError) as err:
        bad_db.replication.logger_state()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_replication_first_tick(sys_db, bad_db, cluster):
    if cluster:
        pytest.skip('Not tested in a cluster setup')

    result = sys_db.replication.logger_first_tick()
    assert isinstance(result, string_types)

    with assert_raises(ReplicationLoggerFirstTickError) as err:
        bad_db.replication.logger_first_tick()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_replication_applier(sys_db, bad_db, url, cluster):
    if cluster:
        pytest.skip('Not tested in a cluster setup')

    # Test replication applier state
    state = sys_db.replication.applier_state()
    assert 'server' in state
    assert 'state' in state

    with assert_raises(ReplicationApplierStateError) as err:
        bad_db.replication.applier_state()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}

    # Test replication get applier config
    result = sys_db.replication.applier_config()
    assert 'verbose' in result
    assert 'incremental' in result
    assert 'include_system' in result

    with assert_raises(ReplicationApplierConfigError) as err:
        bad_db.replication.applier_config()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}

    # Test replication stop applier
    result = sys_db.replication.stop_applier()
    assert 'server' in result
    assert 'state' in result

    with assert_raises(ReplicationApplierStopError) as err:
        bad_db.replication.stop_applier()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}

    # Test replication set applier config
    result = sys_db.replication.set_applier_config(
        endpoint=url,
        database='_system',
        username='root',
        password='passwd',
        max_connect_retries=120,
        connect_timeout=15,
        request_timeout=615,
        chunk_size=0,
        auto_start=True,
        adaptive_polling=False,
        include_system=True,
        auto_resync=True,
        auto_resync_retries=3,
        initial_sync_max_wait_time=405,
        connection_retry_wait_time=25,
        idle_min_wait_time=2,
        idle_max_wait_time=3,
        require_from_present=False,
        verbose=True,
        restrict_type='exclude',
        restrict_collections=['students']
    )
    assert result['endpoint'] == url
    assert result['database'] == '_system'
    assert result['username'] == 'root'
    assert result['max_connect_retries'] == 120
    assert result['connect_timeout'] == 15
    assert result['request_timeout'] == 615
    assert result['chunk_size'] == 0
    assert result['auto_start'] is True
    assert result['adaptive_polling'] is False
    assert result['include_system'] is True
    assert result['auto_resync'] is True
    assert result['auto_resync_retries'] == 3
    assert result['initial_sync_max_wait_time'] == 405
    assert result['connection_retry_wait_time'] == 25
    assert result['idle_min_wait_time'] == 2
    assert result['idle_max_wait_time'] == 3
    assert result['require_from_present'] is False
    assert result['verbose'] is True
    assert result['restrict_type'] == 'exclude'
    assert result['restrict_collections'] == ['students']

    with assert_raises(ReplicationApplierConfigSetError) as err:
        bad_db.replication.set_applier_config(url)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}

    # Test replication start applier
    result = sys_db.replication.start_applier()
    assert 'server' in result
    assert 'state' in result
    sys_db.replication.stop_applier()

    with assert_raises(ReplicationApplierStartError) as err:
        bad_db.replication.start_applier()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_replication_make_slave(sys_db, bad_db, url, replication):
    if not replication:
        pytest.skip('Only tested for replication')

    sys_db.replication.stop_applier()

    result = sys_db.replication.make_slave(
        endpoint='tcp://192.168.1.65:8500',
        database='test',
        username='root',
        password='passwd',
        restrict_type='include',
        restrict_collections=['test'],
        include_system=False,
        max_connect_retries=5,
        connect_timeout=500,
        request_timeout=500,
        chunk_size=0,
        adaptive_polling=False,
        auto_resync=False,
        auto_resync_retries=0,
        initial_sync_max_wait_time=0,
        connection_retry_wait_time=0,
        idle_min_wait_time=0,
        idle_max_wait_time=0,
        require_from_present=False,
        verbose=True
    )
    assert 'endpoint' in result
    assert 'database' in result

    with assert_raises(ReplicationMakeSlaveError) as err:
        bad_db.replication.make_slave(endpoint=url)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_replication_cluster_inventory(sys_db, bad_db, cluster):
    if cluster:
        result = sys_db.replication.cluster_inventory(include_system=True)
        assert isinstance(result, dict)

    with assert_raises(ReplicationClusterInventoryError) as err:
        bad_db.replication.cluster_inventory(include_system=True)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_replication_server_id(sys_db, bad_db):
    result = sys_db.replication.server_id()
    assert isinstance(result, string_types)

    with assert_raises(ReplicationServerIDError) as err:
        bad_db.replication.server_id()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_replication_synchronize(sys_db, bad_db, url, replication):
    if not replication:
        pytest.skip('Only tested for replication')

    result = sys_db.replication.synchronize(
        endpoint='tcp://192.168.1.65:8500',
        database='test',
        username='root',
        password='passwd',
        include_system=False,
        incremental=False,
        restrict_type='include',
        restrict_collections=['test'],
        initial_sync_wait_time=None
    )
    assert 'collections' in result
    assert 'last_log_tick' in result

    with assert_raises(ReplicationSyncError) as err:
        bad_db.replication.synchronize(endpoint=url)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}
