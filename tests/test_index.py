from __future__ import absolute_import, unicode_literals

from arango.exceptions import (
    IndexListError,
    IndexCreateError,
    IndexDeleteError,
    IndexLoadError
)
from tests.helpers import assert_raises, extract


def test_list_indexes(col, bad_col):
    expected_index = {
        'id': '0',
        'selectivity': 1,
        'sparse': False,
        'type': 'primary',
        'fields': ['_key'],
        'unique': True
    }
    indexes = col.indexes()
    assert isinstance(indexes, list)
    assert expected_index in indexes

    with assert_raises(IndexListError) as err:
        bad_col.indexes()
    assert err.value.error_code in {11, 1228}


def test_add_hash_index(col):
    fields = ['attr1', 'attr2']
    result = col.add_hash_index(
        fields=fields,
        unique=True,
        sparse=True,
        deduplicate=True
    )

    expected_index = {
        'selectivity': 1,
        'sparse': True,
        'type': 'hash',
        'fields': ['attr1', 'attr2'],
        'unique': True,
        'deduplicate': True
    }
    for key, value in expected_index.items():
        assert result[key] == value

    result.pop('new', None)
    assert result in col.indexes()


def test_add_skiplist_index(col):
    fields = ['attr1', 'attr2']
    result = col.add_skiplist_index(
        fields=fields,
        unique=True,
        sparse=True,
        deduplicate=True
    )

    expected_index = {
        'sparse': True,
        'type': 'skiplist',
        'fields': ['attr1', 'attr2'],
        'unique': True,
        'deduplicate': True
    }
    for key, value in expected_index.items():
        assert result[key] == value

    result.pop('new', None)
    assert result in col.indexes()


def test_add_geo_index(col):
    # Test add geo index with one attribute
    result = col.add_geo_index(
        fields=['attr1'],
        ordered=False
    )

    expected_index = {
        'sparse': True,
        'type': 'geo',
        'fields': ['attr1'],
        'unique': False,
        'geo_json': False,
    }
    for key, value in expected_index.items():
        assert result[key] == value

    result.pop('new', None)
    assert result in col.indexes()

    # Test add geo index with two attributes
    result = col.add_geo_index(
        fields=['attr1', 'attr2'],
        ordered=False,
    )
    expected_index = {
        'sparse': True,
        'type': 'geo',
        'fields': ['attr1', 'attr2'],
        'unique': False,
    }
    for key, value in expected_index.items():
        assert result[key] == value

    result.pop('new', None)
    assert result in col.indexes()

    # Test add geo index with more than two attributes (should fail)
    with assert_raises(IndexCreateError) as err:
        col.add_geo_index(fields=['attr1', 'attr2', 'attr3'])
    assert err.value.error_code == 10


def test_add_fulltext_index(col):
    # Test add fulltext index with one attributes
    result = col.add_fulltext_index(
        fields=['attr1'],
        min_length=10,
    )
    expected_index = {
        'sparse': True,
        'type': 'fulltext',
        'fields': ['attr1'],
        'min_length': 10,
        'unique': False,
    }
    for key, value in expected_index.items():
        assert result[key] == value

    result.pop('new', None)
    assert result in col.indexes()

    # Test add fulltext index with two attributes (should fail)
    with assert_raises(IndexCreateError) as err:
        col.add_fulltext_index(fields=['attr1', 'attr2'])
    assert err.value.error_code == 10


def test_add_persistent_index(col):
    # Test add persistent index with two attributes
    result = col.add_persistent_index(
        fields=['attr1', 'attr2'],
        unique=True,
        sparse=True,
    )
    expected_index = {
        'sparse': True,
        'type': 'persistent',
        'fields': ['attr1', 'attr2'],
        'unique': True,
    }
    for key, value in expected_index.items():
        assert result[key] == value

    result.pop('new', None)
    assert result in col.indexes()


def test_delete_index(col, bad_col):
    old_indexes = set(extract('id', col.indexes()))
    col.add_hash_index(['attr3', 'attr4'], unique=True)
    col.add_skiplist_index(['attr3', 'attr4'], unique=True)
    col.add_fulltext_index(fields=['attr3'], min_length=10)

    new_indexes = set(extract('id', col.indexes()))
    assert new_indexes.issuperset(old_indexes)

    indexes_to_delete = new_indexes - old_indexes
    for index_id in indexes_to_delete:
        assert col.delete_index(index_id) is True

    new_indexes = set(extract('id', col.indexes()))
    assert new_indexes == old_indexes

    # Test delete missing indexes
    for index_id in indexes_to_delete:
        assert col.delete_index(index_id, ignore_missing=True) is False
    for index_id in indexes_to_delete:
        with assert_raises(IndexDeleteError) as err:
            col.delete_index(index_id, ignore_missing=False)
        assert err.value.error_code == 1212

    # Test delete indexes with bad collection
    for index_id in indexes_to_delete:
        with assert_raises(IndexDeleteError) as err:
            bad_col.delete_index(index_id, ignore_missing=False)
        assert err.value.error_code in {11, 1228}


def test_load_indexes(col, bad_col):
    # Test load indexes
    assert col.load_indexes() is True

    # Test load indexes with bad collection
    with assert_raises(IndexLoadError) as err:
        bad_col.load_indexes()
    assert err.value.error_code in {11, 1228}
