from __future__ import absolute_import, unicode_literals

import pytest

from arango import ArangoClient
from arango.exceptions import (
    IndexCreateError
)

from .utils import (
    generate_db_name,
    generate_col_name
)

arango_client = ArangoClient()
db_name = generate_db_name(arango_client)
db = arango_client.create_database(db_name)
col_name = generate_col_name(db)
col = db.create_collection(col_name)
col.add_geo_index(['coordinates'])


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)


def setup_function(*_):
    col.truncate()


def test_list_indexes():
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


def test_add_hash_index():
    fields = ['attr1', 'attr2']
    result = col.add_hash_index(fields, unique=True)

    expected_index = {
        'selectivity': 1,
        'sparse': False,
        'type': 'hash',
        'fields': ['attr1', 'attr2'],
        'unique': True
    }
    for key, value in expected_index.items():
        assert result[key] == value

    result.pop('new', None)
    assert result in col.indexes()


def test_add_skiplist_index():
    fields = ['attr1', 'attr2']
    result = col.add_skiplist_index(fields, unique=True)

    expected_index = {
        'sparse': False,
        'type': 'skiplist',
        'fields': ['attr1', 'attr2'],
        'unique': True
    }
    for key, value in expected_index.items():
        assert result[key] == value

    result.pop('new', None)
    assert result in col.indexes()


def test_add_geo_index():
    # Test add geo index with one attribute
    result = col.add_geo_index(fields=['attr1'], ordered=False)

    expected_index = {
        'sparse': True,
        'type': 'geo1',
        'fields': ['attr1'],
        'unique': False,
        'geo_json': False,
        'ignore_none': True,
        'constraint': False
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
        'type': 'geo2',
        'fields': ['attr1', 'attr2'],
        'unique': False,
        'ignore_none': True,
        'constraint': False
    }
    for key, value in expected_index.items():
        assert result[key] == value

    result.pop('new', None)
    assert result in col.indexes()

    # Test add geo index with more than two attributes (should fail)
    with pytest.raises(IndexCreateError):
        col.add_geo_index(fields=['attr1', 'attr2', 'attr3'])


def test_add_fulltext_index():
    # Test add fulltext index with two attributes (should fail)
    with pytest.raises(IndexCreateError):
        col.add_fulltext_index(fields=['attr1', 'attr2'])

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


def test_add_persistent_index():
    # Test add fulltext index with one attributes
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


def test_delete_index():
    old_indexes = set(index['id'] for index in col.indexes())
    col.add_hash_index(['attr3', 'attr4'], unique=True)
    col.add_skiplist_index(['attr3', 'attr4'], unique=True)
    col.add_fulltext_index(fields=['attr3'], min_length=10)

    new_indexes = set(index['id'] for index in col.indexes())
    assert new_indexes.issuperset(old_indexes)

    for index_id in new_indexes - old_indexes:
        assert col.delete_index(index_id) is True

    new_indexes = set(index['id'] for index in col.indexes())
    assert new_indexes == old_indexes
