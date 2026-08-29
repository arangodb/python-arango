import pytest
from packaging import version

from arango.exceptions import (
    IndexCreateError,
    IndexDeleteError,
    IndexGetError,
    IndexListError,
    IndexLoadError,
)
from tests.helpers import assert_raises, extract, generate_doc_key


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

    indexes = icol.indexes(with_stats=True)
    assert "figures" in indexes[0]

    with assert_raises(IndexListError) as err:
        bad_col.indexes()
    assert err.value.error_code in {11, 1228}


def test_list_indexes_options(icol, monkeypatch):
    requests = []

    def execute(request, response_handler):
        requests.append(request)
        return []

    monkeypatch.setattr(icol, "_execute", execute)

    assert icol.indexes() == []
    assert requests[-1].params == {"collection": icol.name}

    assert icol.indexes(with_hidden=True) == []
    assert requests[-1].params == {
        "collection": icol.name,
        "withHidden": "1",
    }

    assert icol.indexes(with_stats=True) == []
    assert requests[-1].params == {
        "collection": icol.name,
        "withStats": "1",
    }

    assert icol.indexes(with_stats=True, with_hidden=True) == []
    assert requests[-1].params == {
        "collection": icol.name,
        "withStats": "1",
        "withHidden": "1",
    }


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


def test_add_geo_index(icol):
    # Test add geo index with one attribute
    result = icol.add_index(
        {
            "type": "geo",
            "fields": ["attr1"],
            "geoJson": True,
            "name": "geo_index",
            "inBackground": True,
        }
    )

    expected_index = {
        "sparse": True,
        "type": "geo",
        "fields": ["attr1"],
        "unique": False,
        "geoJson": True,
        "name": "geo_index",
    }
    for key, value in expected_index.items():
        assert result[key] == value, (key, value, result[key])

    assert result["id"] in extract("id", icol.indexes())

    # Test add geo index with two attributes
    result = icol.add_index(
        {
            "type": "geo",
            "fields": ["attr1", "attr2"],
            "geoJson": False,
        }
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
        icol.add_index({"type": "geo", "fields": ["attr1", "attr2", "attr3"]})
    assert err.value.error_code == 10

    # Clean up the index
    icol.delete_index(result["id"])


def test_add_persistent_index(icol):
    # Test add persistent index with two attributes
    result = icol.add_index(
        {
            "type": "persistent",
            "fields": ["attr1", "attr2"],
            "unique": True,
            "sparse": True,
            "name": "persistent_index",
            "inBackground": True,
        }
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
    result = icol.add_index(
        {
            "type": "ttl",
            "fields": ["attr1"],
            "expireAfter": 1000,
            "name": "ttl_index",
            "inBackground": True,
        }
    )
    expected_index = {
        "type": "ttl",
        "fields": ["attr1"],
        "expireAfter": 1000,
        "name": "ttl_index",
    }
    for key, value in expected_index.items():
        assert result[key] == value

    assert result["id"] in extract("id", icol.indexes())

    # Clean up the index
    icol.delete_index(result["id"])


def test_add_inverted_index(icol, skip_tests):
    parameters = dict(
        fields=[{"name": "attr1", "cache": True}],
        name="c0_cached",
        storedValues=[{"fields": ["a"], "compression": "lz4", "cache": True}],
        includeAllFields=True,
        analyzer="identity",
        primarySort={"cache": True, "fields": [{"field": "a", "direction": "asc"}]},
    )
    expected_keys = ["primarySort", "analyzer", "includeAllFields", "searchField"]

    if "enterprise" not in skip_tests:
        parameters["cache"] = True
        parameters["primaryKeyCache"] = True
        expected_keys.extend(["cache", "primaryKeyCache"])

    result = icol.add_index({"type": "inverted", **parameters})
    assert result["id"] in extract("id", icol.indexes())

    for key in expected_keys:
        assert key in result

    icol.delete_index(result["id"])


def test_add_zkd_index(icol, db_version):
    result = icol.add_index(
        {
            "type": "zkd",
            "fields": ["x", "y", "z"],
            "fieldValueTypes": "double",
            "name": "zkd_index",
            "inBackground": False,
            "unique": False,
        }
    )

    expected_index = {
        "name": "zkd_index",
        "type": "zkd",
        "fields": ["x", "y", "z"],
        "isNewlyCreated": True,
        "unique": False,
    }

    for key, value in expected_index.items():
        assert result[key] == value

    assert result["id"] in extract("id", icol.indexes())

    with assert_raises(IndexCreateError) as err:
        icol.add_index(
            {"type": "zkd", "fieldValueTypes": "integer", "fields": ["x", "y", "z"]}
        )
    assert err.value.error_code == 10

    icol.delete_index(result["id"])


def test_add_mdi_index(icol, db_version):
    if db_version < version.parse("3.12.0"):
        pytest.skip("MDI indexes are usable with 3.12+ only")

    result = icol.add_index(
        {
            "type": "mdi",
            "fields": ["x", "y", "z"],
            "fieldValueTypes": "double",
            "name": "mdi_index",
            "inBackground": False,
            "unique": True,
        }
    )

    expected_index = {
        "name": "mdi_index",
        "type": "mdi",
        "fields": ["x", "y", "z"],
        "isNewlyCreated": True,
        "unique": True,
    }

    for key, value in expected_index.items():
        assert result[key] == value

    assert result["id"] in extract("id", icol.indexes())

    with assert_raises(IndexCreateError) as err:
        icol.add_index(
            {
                "type": "mdi",
                "fieldValueTypes": "integer",
                "fields": ["x", "y", "z"],
            }
        )
    assert err.value.error_code == 10

    icol.delete_index(result["id"])


def test_add_vector_index(col, db_version):
    # Insert vector data.
    docs = []
    for i in range(100):
        docs.append(
            {
                "_key": generate_doc_key(),
                "x": [1] * 128,
                "y": [1] * 128,
            }
        )
    col.insert_many(docs)

    # Test basic compatibility.
    index_meta = [
        {
            "type": "vector",
            "fields": ["x"],
            "name": "vector_index_1",
            "params": {
                "metric": "cosine",
                "dimension": 128,
                "nLists": 2,
            },
        },
        {
            "type": "vector",
            "fields": ["y"],
            "name": "vector_index_2",
            "params": {
                "metric": "cosine",
                "dimension": 128,
                "nLists": 3,
            },
        },
    ]

    results = [col.add_index(index_meta[0]), col.add_index(index_meta[1])]
    assert results[0]["name"] == "vector_index_1"
    assert results[1]["name"] == "vector_index_2"

    # Test hidden shard details.
    indexes = col.indexes(with_hidden=True)

    if db_version >= version.parse("3.12.10"):
        details = {item["id"]: item for item in indexes}
        for result in results:
            shards = details[result["id"]]["shards"]
            assert shards is not None
            for status in shards.values():
                assert {"trainingState", "error", "resolvedNLists"} <= status.keys()

    col.delete_index(results[0]["id"])
    col.delete_index(results[1]["id"])

    if db_version >= version.parse("3.12.10"):
        # Test server-managed nLists.
        default_index = {
            "type": "vector",
            "fields": ["x"],
            "name": "vector_index_default",
            "params": {
                "metric": "cosine",
                "dimension": 128,
            },
        }
        scaling_n_lists = {
            "strategy": "autoSqrt",
            "multiplier": 1,
            "minNLists": 2,
            "tiers": [],
        }
        scaling_index = {
            "type": "vector",
            "fields": ["y"],
            "name": "vector_index_scaling",
            "params": {
                "metric": "cosine",
                "dimension": 128,
                "nLists": scaling_n_lists,
                "numberOfDocsPerCentroid": 10,
                "factory": "IVF{},Flat",
            },
        }

        default_result = col.add_index(default_index)
        scaling_result = col.add_index(scaling_index)

        default_n_lists = default_result["params"]["nLists"]
        assert default_n_lists["strategy"] == "autoSqrt"
        assert default_n_lists["multiplier"] == 4
        assert default_n_lists["minNLists"] == 2
        assert scaling_result["params"]["nLists"] == scaling_n_lists
        assert scaling_result["params"]["numberOfDocsPerCentroid"] == 10
        assert scaling_result["params"]["factory"] == "IVF{},Flat"

        col.delete_index(default_result["id"])
        col.delete_index(scaling_result["id"])

        # Test unusable creation.
        unusable_index = {
            "type": "vector",
            "fields": ["x"],
            "name": "vector_index_unusable",
            "params": {
                "metric": "cosine",
                "dimension": 128,
                "nLists": 2,
                "factory": "IVF3,Flat",
            },
        }
        unusable_result = col.add_index(unusable_index)
        assert unusable_result["trainingState"] == "unusable"
        assert unusable_result["errorMessage"]
        col.delete_index(unusable_result["id"])

        # Test invalid request failure.
        with assert_raises(IndexCreateError) as err:
            col.add_index(
                {
                    "type": "vector",
                    "fields": ["x"],
                    "name": "vector_index_invalid",
                    "params": {
                        "metric": "cosine",
                        "dimension": 128,
                        "nLists": 0,  # must be greater than 0
                    },
                }
            )
        assert err.value.http_code == 400


def test_delete_index(icol, bad_col):
    old_indexes = set(extract("id", icol.indexes()))
    index1 = {"type": "persistent", "fields": ["attr1", "attr2"], "unique": True}
    icol.add_index(index1)
    index2 = {"type": "persistent", "fields": ["attr3", "attr4"], "unique": True}
    icol.add_index(index2)

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
