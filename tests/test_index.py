import pytest
from packaging import version

from arango.exceptions import (
    IndexCreateError,
    IndexDeleteError,
    IndexGetError,
    IndexListError,
    IndexLoadError,
)
from tests.helpers import assert_raises, extract


def test_list_indexes(icol, bad_col):
    indexes = icol.indexes()
    assert isinstance(indexes, list)
    assert len(indexes) > 0
    assert "id" in indexes[0]
    assert "type" in indexes[0]
    assert "fields" in indexes[0]
    assert "selectivity" in indexes[0]
    assert "sparse" in indexes[0]
    assert "unique" in indexes[0]

    with assert_raises(IndexListError) as err:
        bad_col.indexes()
    assert err.value.error_code in {11, 1228}


def test_get_index(icol, bad_col):
    indexes = icol.indexes()
    for index in indexes:
        retrieved_index = icol.get_index(index["id"])
        assert retrieved_index["id"] == index["id"]
        assert retrieved_index["name"] == index["name"]
        assert retrieved_index["type"] == index["type"]
        assert retrieved_index["fields"] == index["fields"]
        assert retrieved_index["sparse"] == index["sparse"]
        assert retrieved_index["unique"] == index["unique"]
        # TODO: Revisit
        # assert retrieved_index["selectivity"] == index["selectivity"]

    with assert_raises(IndexGetError) as err:
        icol.get_index("bad_index")

    assert err.value.error_code == 1212


def test_add_hash_index(icol):
    icol = icol

    fields = ["attr1", "attr2"]
    result = icol.add_hash_index(
        fields=fields,
        unique=True,
        sparse=True,
        deduplicate=True,
        name="hash_index",
        in_background=False,
    )

    expected_index = {
        "sparse": True,
        "type": "hash",
        "fields": ["attr1", "attr2"],
        "unique": True,
        "deduplicate": True,
        "name": "hash_index",
    }
    for key, value in expected_index.items():
        assert result[key] == value

    assert result["id"] in extract("id", icol.indexes())

    # Clean up the index
    icol.delete_index(result["id"])


def test_add_skiplist_index(icol):
    fields = ["attr1", "attr2"]
    result = icol.add_skiplist_index(
        fields=fields,
        unique=True,
        sparse=True,
        deduplicate=True,
        name="skiplist_index",
        in_background=False,
    )

    expected_index = {
        "sparse": True,
        "type": "skiplist",
        "fields": ["attr1", "attr2"],
        "unique": True,
        "deduplicate": True,
        "name": "skiplist_index",
    }
    for key, value in expected_index.items():
        assert result[key] == value

    assert result["id"] in extract("id", icol.indexes())

    # Clean up the index
    icol.delete_index(result["id"])


def test_add_geo_index(icol):
    # Test add geo index with one attribute
    result = icol.add_geo_index(
        fields=["attr1"], geo_json=True, name="geo_index", in_background=True
    )

    expected_index = {
        "sparse": True,
        "type": "geo",
        "fields": ["attr1"],
        "unique": False,
        "geo_json": True,
        "name": "geo_index",
    }
    for key, value in expected_index.items():
        assert result[key] == value

    assert result["id"] in extract("id", icol.indexes())

    # Test add geo index with two attributes
    result = icol.add_geo_index(
        fields=["attr1", "attr2"],
        geo_json=False,
    )
    expected_index = {
        "sparse": True,
        "type": "geo",
        "fields": ["attr1", "attr2"],
        "unique": False,
    }
    for key, value in expected_index.items():
        assert result[key] == value

    assert result["id"] in extract("id", icol.indexes())

    # Test add geo index with more than two attributes (should fail)
    with assert_raises(IndexCreateError) as err:
        icol.add_geo_index(fields=["attr1", "attr2", "attr3"])
    assert err.value.error_code == 10

    # Clean up the index
    icol.delete_index(result["id"])


def test_add_fulltext_index(icol):
    # Test add fulltext index with one attributes
    result = icol.add_fulltext_index(
        fields=["attr1"], min_length=10, name="fulltext_index", in_background=True
    )
    expected_index = {
        "sparse": True,
        "type": "fulltext",
        "fields": ["attr1"],
        "min_length": 10,
        "unique": False,
        "name": "fulltext_index",
    }
    for key, value in expected_index.items():
        assert result[key] == value

    assert result["id"] in extract("id", icol.indexes())

    # Test add fulltext index with two attributes (should fail)
    with assert_raises(IndexCreateError) as err:
        icol.add_fulltext_index(fields=["attr1", "attr2"])
    assert err.value.error_code == 10

    # Clean up the index
    icol.delete_index(result["id"])


def test_add_persistent_index(icol):
    # Test add persistent index with two attributes
    result = icol.add_persistent_index(
        fields=["attr1", "attr2"],
        unique=True,
        sparse=True,
        name="persistent_index",
        in_background=True,
    )
    expected_index = {
        "sparse": True,
        "type": "persistent",
        "fields": ["attr1", "attr2"],
        "unique": True,
        "name": "persistent_index",
    }
    for key, value in expected_index.items():
        assert result[key] == value

    assert result["id"] in extract("id", icol.indexes())

    # Clean up the index
    icol.delete_index(result["id"])


def test_add_ttl_index(icol):
    # Test add persistent index with two attributes
    result = icol.add_ttl_index(
        fields=["attr1"], expiry_time=1000, name="ttl_index", in_background=True
    )
    expected_index = {
        "type": "ttl",
        "fields": ["attr1"],
        "expiry_time": 1000,
        "name": "ttl_index",
    }
    for key, value in expected_index.items():
        assert result[key] == value

    assert result["id"] in extract("id", icol.indexes())

    # Clean up the index
    icol.delete_index(result["id"])


def test_add_inverted_index(icol, enterprise, db_version):
    if db_version < version.parse("3.10.0"):
        pytest.skip("Inverted indexes are not supported before 3.10.0")

    parameters = dict(
        fields=[{"name": "attr1", "cache": True}],
        name="c0_cached",
        storedValues=[{"fields": ["a"], "compression": "lz4", "cache": True}],
        includeAllFields=True,
        analyzer="identity",
        primarySort={"cache": True, "fields": [{"field": "a", "direction": "asc"}]},
    )
    expected_keys = ["primary_sort", "analyzer", "include_all_fields", "search_field"]

    if enterprise and db_version >= version.parse("3.10.2"):
        parameters["cache"] = True
        parameters["primaryKeyCache"] = True
        expected_keys.extend(["cache", "primaryKeyCache"])

    result = icol.add_inverted_index(**parameters)
    assert result["id"] in extract("id", icol.indexes())

    for key in expected_keys:
        assert key in result

    icol.delete_index(result["id"])


def test_add_zkd_index(icol, db_version):
    result = icol.add_zkd_index(
        name="zkd_index",
        fields=["x", "y", "z"],
        field_value_types="double",
        in_background=False,
        unique=False,
    )

    expected_index = {
        "name": "zkd_index",
        "type": "zkd",
        "fields": ["x", "y", "z"],
        "new": True,
        "unique": False,
    }

    for key, value in expected_index.items():
        assert result[key] == value

    assert result["id"] in extract("id", icol.indexes())

    with assert_raises(IndexCreateError) as err:
        icol.add_zkd_index(field_value_types="integer", fields=["x", "y", "z"])
    assert err.value.error_code == 10

    icol.delete_index(result["id"])


def test_add_mdi_index(icol, db_version):
    if db_version < version.parse("3.12.0"):
        pytest.skip("MDI indexes are usable with 3.12+ only")

    result = icol.add_mdi_index(
        name="mdi_index",
        fields=["x", "y", "z"],
        field_value_types="double",
        in_background=False,
        unique=True,
    )

    expected_index = {
        "name": "mdi_index",
        "type": "mdi",
        "fields": ["x", "y", "z"],
        "new": True,
        "unique": True,
    }

    for key, value in expected_index.items():
        assert result[key] == value

    assert result["id"] in extract("id", icol.indexes())

    with assert_raises(IndexCreateError) as err:
        icol.add_mdi_index(field_value_types="integer", fields=["x", "y", "z"])
    assert err.value.error_code == 10

    icol.delete_index(result["id"])


def test_delete_index(icol, bad_col):
    old_indexes = set(extract("id", icol.indexes()))
    icol.add_hash_index(["attr3", "attr4"], unique=True)
    icol.add_skiplist_index(["attr3", "attr4"], unique=True)
    icol.add_fulltext_index(fields=["attr3"], min_length=10)

    new_indexes = set(extract("id", icol.indexes()))
    assert new_indexes.issuperset(old_indexes)

    indexes_to_delete = new_indexes - old_indexes
    for index_id in indexes_to_delete:
        assert icol.delete_index(index_id) is True

    new_indexes = set(extract("id", icol.indexes()))
    assert new_indexes == old_indexes

    # Test delete missing indexes
    for index_id in indexes_to_delete:
        assert icol.delete_index(index_id, ignore_missing=True) is False
    for index_id in indexes_to_delete:
        with assert_raises(IndexDeleteError) as err:
            icol.delete_index(index_id, ignore_missing=False)
        assert err.value.error_code == 1212

    # Test delete indexes with bad collection
    for index_id in indexes_to_delete:
        with assert_raises(IndexDeleteError) as err:
            bad_col.delete_index(index_id, ignore_missing=False)
        assert err.value.error_code in {11, 1228}


def test_load_indexes(icol, bad_col):
    # Test load indexes
    assert icol.load_indexes() is True

    # Test load indexes with bad collection
    with assert_raises(IndexLoadError) as err:
        bad_col.load_indexes()
    assert err.value.error_code in {11, 1228}
