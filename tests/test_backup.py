import pytest

from arango.errno import DATABASE_NOT_FOUND, FILE_NOT_FOUND, FORBIDDEN
from arango.exceptions import (
    BackupCreateError,
    BackupDeleteError,
    BackupDownloadError,
    BackupGetError,
    BackupRestoreError,
    BackupUploadError,
)
from tests.helpers import assert_raises


def test_backup_management(sys_db, bad_db, enterprise):
    if not enterprise:
        pytest.skip("Only for ArangoDB enterprise edition")

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
    result = sys_db.backup.upload(
        backup_id=backup_id_foo,
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
        backup_id=backup_id_bar,
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
    assert err.value.error_code == FILE_NOT_FOUND
