import time

import pytest
import time
from packaging import version

from arango.errno import DATABASE_NOT_FOUND, FILE_NOT_FOUND, FORBIDDEN, HTTP_NOT_FOUND
from arango.exceptions import (
    BackupCreateError,
    BackupDeleteError,
    BackupDownloadError,
    BackupGetError,
    BackupRestoreError,
    BackupUploadError,
)
from tests.helpers import assert_raises

def wait_for_cluster_resilient(sys_db):
    firstExec = True
    collectionsInSync = True
    attempts = 100
    while not collectionsInSync and attempts > 0:
        collectionsInSync = True
        countInSync = 0
        countStillWaiting = 0
        cols = sys_db.replication.cluster_inventory(include_system=True)
        print(cols)
        if cols is None:
          collectionsInSync = False
          time.sleep(1)
          attempts -= 1
          continue
        for col in cols:
          collectionsInSync = collectionsInSync and col.allInSync
          if not col.allInSync:
            countStillWaiting += 1
          else:
            countInSync+= 1

        if not collectionsInSync:
          time.sleep(1)
          if attempts % 50 == 0:
            print(cols)
            print(f"Amount of collection in sync: {countInSync}. Still not in sync: {countStillWaiting}")
        if firstExec:
          firstExec = False
          if countInSync + countStillWaiting > 100:
            attempts = Math.round((countInSync + countStillWaiting) * 0.8);
            print("Set attempts to {attempts}")
        attempts -= 1;
    if attempts == 0:
        raise Exception("collections didn't come in sync!")

def test_backup_management(sys_db, bad_db, cluster, skip_tests, db_version):
    if "enterprise" in skip_tests:
        pytest.skip("Only for ArangoDB enterprise edition")
    if "backup" in skip_tests:
        pytest.skip("Skipping backup tests")
    if not cluster:
        pytest.skip("For simplicity, the backup API is only tested in cluster setups")
    if db_version < version.parse("3.12.0"):
        pytest.skip(
            "For simplicity, the backup API is only tested in the latest versions"
        )

    # Test create backup "foo".
    result = sys_db.backup.create(
        label="foo", allow_inconsistent=True, force=False, timeout=1000
    )
    assert "backup_id" in result
    assert "datetime" in result

    backup_id_foo = result["backup_id"]
    assert backup_id_foo.endswith("foo")

    # Test create backup "bar".
    result = sys_db.backup.create(
        label="bar", allow_inconsistent=True, force=False, timeout=1000
    )
    assert "backup_id" in result
    assert "datetime" in result

    backup_id_bar = result["backup_id"]
    assert backup_id_bar.endswith("bar")

    # Test create backup with bad database.
    with assert_raises(BackupCreateError) as err:
        bad_db.backup.create()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}

    # Test get backup.
    result = sys_db.backup.get()
    assert len(result["list"]) == 2

    result = sys_db.backup.get(backup_id_foo)
    assert len(result["list"]) == 1
    assert all(backup_id.endswith("foo") for backup_id in result["list"])

    result = sys_db.backup.get(backup_id_bar)
    assert len(result["list"]) == 1
    assert all(backup_id.endswith("bar") for backup_id in result["list"])

    # Test get backup with bad database.
    with assert_raises(BackupGetError) as err:
        bad_db.backup.get()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}

    # Test upload backup.
    backup_id = backup_id_foo if cluster else backup_id_bar
    result = sys_db.backup.upload(
        backup_id=backup_id,
        repository="local://tmp/backups",
        config={"local": {"type": "local"}},
    )
    assert "upload_id" in result

    # Test upload backup abort.
    assert isinstance(
        sys_db.backup.upload(upload_id=result["upload_id"], abort=False),
        (str, dict),
    )

    # Test upload backup with bad database.
    with assert_raises(BackupUploadError) as err:
        bad_db.backup.upload(upload_id=result["upload_id"])
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}

    # Test download backup.
    result = sys_db.backup.download(
        backup_id=backup_id_foo,
        repository="local://tmp/backups",
        config={"local": {"type": "local"}},
    )
    assert "download_id" in result

    # Test download backup abort.
    assert isinstance(
        sys_db.backup.download(download_id=result["download_id"], abort=False),
        (str, dict),
    )

    # Test download backup with bad database.
    with assert_raises(BackupDownloadError) as err:
        bad_db.backup.download(download_id=result["download_id"])
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}

    # Test restore backup.
    result = sys_db.backup.restore(backup_id_foo)
    assert isinstance(result, dict)

    # Wait for restore to complete
    if cluster:
        wait_for_cluster_resilient(sys_db)
    else:
        time.sleep(10)

    # Test restore backup with bad database.
    with assert_raises(BackupRestoreError) as err:
        bad_db.backup.restore(backup_id_foo)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}

    # Test delete backup.
    assert sys_db.backup.delete(backup_id_foo) is True
    assert sys_db.backup.delete(backup_id_bar) is True

    # Test delete missing backup.
    with assert_raises(BackupDeleteError) as err:
        sys_db.backup.delete(backup_id_foo)
    if cluster:
        assert err.value.error_code == HTTP_NOT_FOUND
    else:
        assert err.value.error_code == FILE_NOT_FOUND
