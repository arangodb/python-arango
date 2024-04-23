import pytest

from arango.client import ArangoClient
from arango.collection import StandardCollection
from arango.exceptions import (
    CollectionChecksumError,
    CollectionConfigureError,
    CollectionCreateError,
    CollectionDeleteError,
    CollectionListError,
    CollectionLoadError,
    CollectionPropertiesError,
    CollectionRecalculateCountError,
    CollectionRenameError,
    CollectionRevisionError,
    CollectionStatisticsError,
    CollectionTruncateError,
    CollectionUnloadError,
    DatabaseDeleteError,
)
from tests.helpers import (
    assert_raises,
    extract,
    generate_col_name,
    generate_string,
    generate_username,
)


def test_collection_attributes(db, col, username):
    assert col.context in ["default", "async", "batch", "transaction"]
    assert col.username == username
    assert col.db_name == db.name
    assert col.name.startswith("test_collection")
    assert repr(col) == f"<StandardCollection {col.name}>"


def test_collection_misc_methods(col, bad_col, cluster):
    # Test get properties
    properties = col.properties()
    assert properties["name"] == col.name
    assert properties["system"] is False

    # Test get properties with bad collection
    with assert_raises(CollectionPropertiesError) as err:
        bad_col.properties()
    assert err.value.error_code in {11, 1228}

    # Test configure properties
    prev_sync = properties["sync"]

    computed_values = [
        {
            "name": "foo",
            "expression": "RETURN 1",
            "computeOn": ["insert", "update", "replace"],
            "overwrite": True,
            "failOnWarning": False,
            "keepNull": True,
        }
    ]

    properties = col.configure(
        sync=not prev_sync, schema={}, computed_values=computed_values
    )

    assert properties["name"] == col.name
    assert properties["system"] is False
    assert properties["sync"] is not prev_sync
    assert properties["computedValues"] == computed_values
    col.configure(computed_values=[])

    # Test configure properties with bad collection
    with assert_raises(CollectionConfigureError) as err:
        bad_col.configure(sync=True)
    assert err.value.error_code in {11, 1228}

    # Test get statistics
    stats = col.statistics()
    assert isinstance(stats, dict)
    assert "indexes" in stats

    # Test get statistics with bad collection
    with assert_raises(CollectionStatisticsError) as err:
        bad_col.statistics()
    assert err.value.error_code in {11, 1228}

    # Test get revision
    assert isinstance(col.revision(), str)

    # Test get revision with bad collection
    with assert_raises(CollectionRevisionError) as err:
        bad_col.revision()
    assert err.value.error_code in {11, 1228}

    # Test load into memory
    assert col.load() is True

    # Test load with bad collection
    with assert_raises(CollectionLoadError) as err:
        bad_col.load()
    assert err.value.error_code in {11, 1228}

    # Test unload from memory
    assert col.unload() is True

    # Test unload with bad collection
    with assert_raises(CollectionUnloadError) as err:
        bad_col.unload()
    assert err.value.error_code in {11, 1228}

    if cluster:
        col.insert({})
    else:
        # Test checksum with empty collection
        assert int(col.checksum(with_rev=True, with_data=False)) == 0
        assert int(col.checksum(with_rev=True, with_data=True)) == 0
        assert int(col.checksum(with_rev=False, with_data=False)) == 0
        assert int(col.checksum(with_rev=False, with_data=True)) == 0

        # Test checksum with non-empty collection
        col.insert({})
        assert int(col.checksum(with_rev=True, with_data=False)) > 0
        assert int(col.checksum(with_rev=True, with_data=True)) > 0
        assert int(col.checksum(with_rev=False, with_data=False)) > 0
        assert int(col.checksum(with_rev=False, with_data=True)) > 0

        # Test checksum with bad collection
        with assert_raises(CollectionChecksumError) as err:
            bad_col.checksum()
        assert err.value.error_code in {11, 1228}

    # Test preconditions
    assert len(col) == 1

    # Test truncate collection
    assert col.truncate() is True
    assert len(col) == 0

    # Test truncate with bad collection
    with assert_raises(CollectionTruncateError) as err:
        bad_col.truncate()
    assert err.value.error_code in {11, 1228}

    # Test recalculate count
    assert col.recalculate_count() is True

    # Test recalculate count with bad collection
    with assert_raises(CollectionRecalculateCountError) as err:
        bad_col.recalculate_count()
    assert err.value.error_code in {11, 1228}

    # Test collection info
    info = col.info()
    assert set(info.keys()) == {"id", "name", "system", "type", "status", "global_id"}
    assert info["name"] == col.name
    assert info["system"] is False

    # Test collection compact
    result = col.compact()
    assert result == info


def test_collection_management(db, bad_db, cluster):
    # Test create collection
    col_name = generate_col_name()
    assert db.has_collection(col_name) is False

    schema = {
        "rule": {
            "type": "object",
            "properties": {
                "test_attr:": {"type": "string"},
            },
            "required": ["test_attr"],
        },
        "level": "moderate",
        "message": "Schema Validation Failed.",
        "type": "json",
    }

    computed_values = [
        {
            "name": "foo",
            "expression": "RETURN 1",
            "computeOn": ["insert", "update", "replace"],
            "overwrite": True,
            "failOnWarning": False,
            "keepNull": True,
        }
    ]

    col = db.create_collection(
        name=col_name, key_generator="autoincrement", key_increment=9, key_offset=100
    )
    key_options = col.properties()["key_options"]
    assert key_options["key_generator"] == "autoincrement"
    assert key_options["key_increment"] == 9
    assert key_options["key_offset"] == 100
    db.delete_collection(col_name)

    col = db.create_collection(
        name=col_name,
        sync=True,
        system=False,
        key_generator="traditional",
        user_keys=False,
        edge=True,
        shard_count=2,
        shard_fields=["test_attr:"],
        replication_factor=1,
        shard_like="",
        sync_replication=False,
        enforce_replication_factor=False,
        sharding_strategy="community-compat",
        smart_join_attribute="test_attr",
        write_concern=1,
        schema=schema,
        computedValues=computed_values,
    )
    assert db.has_collection(col_name) is True

    if cluster:
        for details in (False, True):
            shards = col.shards(details=details)
            assert shards["name"] == col_name
            assert shards["system"] is False
            assert len(shards["shards"]) == 2

    properties = col.properties()
    assert "key_options" in properties
    assert properties["schema"] == schema
    assert properties["name"] == col_name
    assert properties["sync"] is True
    assert properties["system"] is False
    assert properties["computedValues"] == computed_values
    col.configure(computed_values=[])

    # Test create duplicate collection
    with assert_raises(CollectionCreateError) as err:
        db.create_collection(col_name)
    assert err.value.error_code == 1207

    # Test list collections
    assert all(
        entry["name"].startswith("test_collection") or entry["name"].startswith("_")
        for entry in db.collections()
    )

    # Test list collections with bad database
    with assert_raises(CollectionListError) as err:
        bad_db.collections()
    assert err.value.error_code in {11, 1228}

    # Test has collection with bad database
    with assert_raises(CollectionListError) as err:
        bad_db.has_collection(col_name)
    assert err.value.error_code in {11, 1228}

    # Test get collection object
    test_col = db.collection(col.name)
    assert isinstance(test_col, StandardCollection)
    assert test_col.name == col.name

    test_col = db[col.name]
    assert isinstance(test_col, StandardCollection)
    assert test_col.name == col.name

    # Test delete collection
    assert db.delete_collection(col_name, system=False) is True
    assert col_name not in extract("name", db.collections())

    # Test drop missing collection
    with assert_raises(CollectionDeleteError) as err:
        db.delete_collection(col_name)
    assert err.value.error_code == 1203
    assert db.delete_collection(col_name, ignore_missing=True) is False

    if not cluster:
        # Test rename collection
        new_name = generate_col_name()
        col = db.create_collection(new_name)
        assert col.rename(new_name) is True
        assert col.name == new_name
        assert repr(col) == f"<StandardCollection {new_name}>"

        # Try again (the operation should be idempotent)
        assert col.rename(new_name) is True
        assert col.name == new_name
        assert repr(col) == f"<StandardCollection {new_name}>"

        # Test rename with bad collection
        with assert_raises(CollectionRenameError) as err:
            bad_db.collection(new_name).rename(new_name)
        assert err.value.error_code in {11, 1228}


@pytest.fixture
def special_collection_names(db):
    names = ["abc123", "maçã", "mötör", "😀", "ﻚﻠﺑ ﻞﻄﻴﻓ", "かわいい犬"]

    yield names

    for name in names:
        try:
            db.delete_collection(name)
        except CollectionDeleteError:
            pass


# Code duplication from `test_database.py`...
@pytest.fixture
def special_db_names(sys_db):
    names = ["abc123", "maçã", "mötör", "😀", "ﻚﻠﺑ ﻞﻄﻴﻓ", "かわいい犬"]

    yield names

    for name in names:
        try:
            sys_db.delete_database(name)
        except DatabaseDeleteError:
            pass


def test_collection_utf8(db, special_collection_names):
    for name in special_collection_names:
        create_and_delete_collection(db, name)


# Not sure if this belongs in here or in `test_database.py`...
def test_database_and_collection_utf8(
    sys_db, special_collection_names, special_db_names
):
    client = ArangoClient(hosts="http://127.0.0.1:8529")
    for db_name in special_db_names:
        username = generate_username()
        password = generate_string()

        assert sys_db.create_database(
            name=db_name,
            users=[
                {
                    "active": True,
                    "username": username,
                    "password": password,
                }
            ],
        )

        assert sys_db.has_database(db_name)

        db = client.db(db_name, username, password, verify=True)

        for col_name in special_collection_names:
            create_and_delete_collection(db, col_name)

        assert sys_db.delete_database(db_name)


def create_and_delete_collection(db, name):
    col = db.create_collection(name)
    assert col.name == name
    assert db.has_collection(name) is True

    index_id = col.add_hash_index(fields=["foo"])["name"]
    assert index_id == col.indexes()[-1]["name"]
    assert col.delete_index(index_id) is True

    assert db.delete_collection(name) is True
    assert db.has_collection(name) is False
