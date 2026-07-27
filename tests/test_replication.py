import pytest

from arango.errno import (
    CURSOR_NOT_FOUND,
    DATABASE_NOT_FOUND,
    FORBIDDEN,
    HTTP_NOT_FOUND,
    HTTP_UNAUTHORIZED,
)
from arango.exceptions import (
    ReplicationClusterInventoryError,
    ReplicationDumpBatchCreateError,
    ReplicationDumpBatchDeleteError,
    ReplicationDumpBatchExtendError,
    ReplicationDumpError,
    ReplicationInventoryError,
    ReplicationLoggerStateError,
    ReplicationServerIDError,
    ReplicationSyncError,
)
from tests.helpers import assert_raises


def test_replication_dump_methods(db, bad_db, col, docs, cluster):
    if cluster:
        pytest.skip("Not tested in a cluster setup")

    result = db.replication.create_dump_batch(ttl=1000)
    assert "id" in result and "last_tick" in result
    batch_id = result["id"]

    with assert_raises(ReplicationDumpBatchCreateError) as err:
        bad_db.replication.create_dump_batch(ttl=1000)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}

    result = db.replication.dump(
        collection=col.name, batch_id=batch_id, chunk_size=0, deserialize=True
    )
    assert "content" in result
    assert "check_more" in result

    with assert_raises(ReplicationDumpError) as err:
        bad_db.replication.dump(collection=col.name, batch_id=batch_id)
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
        pytest.skip("Not tested in a cluster setup")

    dump_batch = sys_db.replication.create_dump_batch(ttl=1000)
    dump_batch_id = dump_batch["id"]

    result = sys_db.replication.inventory(
        batch_id=dump_batch_id, include_system=True, all_databases=True
    )
    assert isinstance(result, dict)
    assert "collections" not in result
    assert "databases" in result
    assert "state" in result
    assert "tick" in result

    result = sys_db.replication.inventory(
        batch_id=dump_batch_id, include_system=True, all_databases=False
    )
    assert isinstance(result, dict)
    assert "databases" not in result
    assert "collections" in result
    assert "state" in result
    assert "tick" in result

    with assert_raises(ReplicationInventoryError) as err:
        bad_db.replication.inventory(dump_batch_id)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}

    sys_db.replication.delete_dump_batch(dump_batch_id)


def test_replication_logger_state(sys_db, bad_db, cluster):
    if cluster:
        pytest.skip("Not tested in a cluster setup")

    result = sys_db.replication.logger_state()
    assert "state" in result
    assert "server" in result

    with assert_raises(ReplicationLoggerStateError) as err:
        bad_db.replication.logger_state()
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
    assert isinstance(result, str)

    with assert_raises(ReplicationServerIDError) as err:
        bad_db.replication.server_id()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_replication_synchronize(sys_db, bad_db, url, replication):
    if not replication:
        pytest.skip("Only tested for replication")

    result = sys_db.replication.synchronize(
        endpoint="tcp://192.168.1.65:8500",
        database="test",
        username="root",
        password="passwd",
        include_system=False,
        incremental=False,
        restrict_type="include",
        restrict_collections=["test"],
        initial_sync_wait_time=None,
    )
    assert "collections" in result
    assert "last_log_tick" in result

    with assert_raises(ReplicationSyncError) as err:
        bad_db.replication.synchronize(endpoint=url)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}
