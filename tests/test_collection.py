from __future__ import absolute_import, unicode_literals

import pytest
from six import string_types

from arango import ArangoClient
from arango.collections import Collection
from arango.exceptions import *

from .utils import (
    generate_db_name,
    generate_col_name
)

arango_client = ArangoClient()
db_name = generate_db_name(arango_client)
db = arango_client.create_database(db_name)
col_name = generate_col_name(db)
col = db.create_collection(col_name)


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)


def setup_function(*_):
    col.truncate()


def test_properties():
    assert col.name == col_name
    assert repr(col) == '<ArangoDB collection "{}">'.format(col_name)
    properties = col.properties()
    assert 'id' in properties
    assert properties['status'] in Collection.STATUSES.values()
    assert properties['name'] == col_name
    assert properties['edge'] is False
    assert properties['system'] is False
    assert isinstance(properties['sync'], bool)
    assert isinstance(properties['compact'], bool)
    assert isinstance(properties['volatile'], bool)
    assert isinstance(properties['journal_size'], int)
    assert properties['keygen'] in ('autoincrement', 'traditional')
    assert isinstance(properties['user_keys'], bool)
    if 'key_increment' in properties:
        assert isinstance(properties['key_increment'], int)
    if 'key_offset' in properties:
        assert isinstance(properties['key_offset'], int)


def test_configure():
    properties = col.properties()
    old_sync = properties['sync']
    old_journal_size = properties['journal_size']

    # Test preconditions
    new_sync = not old_sync
    new_journal_size = old_journal_size + 1

    # Test set properties
    result = col.configure(sync=new_sync, journal_size=new_journal_size)
    assert result['sync'] == new_sync
    assert result['journal_size'] == new_journal_size

    # Test persistence
    new_properties = col.properties()
    assert new_properties['sync'] == new_sync
    assert new_properties['journal_size'] == new_journal_size


def test_rename():
    assert col.name == col_name
    new_name = generate_col_name(db)

    # Test rename collection
    result = col.rename(new_name)
    assert result['name'] == new_name
    assert col.name == new_name
    assert repr(col) == '<ArangoDB collection "{}">'.format(new_name)

    # Try again (the operation should be idempotent)
    result = col.rename(new_name)
    assert result['name'] == new_name
    assert col.name == new_name
    assert repr(col) == '<ArangoDB collection "{}">'.format(new_name)


def test_statistics():
    stats = col.statistics()
    assert 'alive' in stats
    assert 'compactors' in stats
    assert 'dead' in stats
    assert 'document_refs' in stats
    assert 'journals' in stats


def test_revision():
    revision = col.revision()
    assert isinstance(revision, string_types)


def test_load():
    assert col.load() in {'loaded', 'loading'}


def test_unload():
    assert col.unload() in {'unloaded', 'unloading'}


def test_rotate():
    # No journal should exist with an empty collection
    with pytest.raises(CollectionRotateJournalError):
        col.rotate()


def test_checksum():
    # Test checksum for an empty collection
    assert col.checksum(with_rev=True, with_data=False) == 0
    assert col.checksum(with_rev=True, with_data=True) == 0
    assert col.checksum(with_rev=False, with_data=False) == 0
    assert col.checksum(with_rev=False, with_data=True) == 0

    # Test checksum for a non-empty collection
    col.insert({'value': 'bar'})
    assert col.checksum(with_rev=True, with_data=False) > 0
    assert col.checksum(with_rev=True, with_data=True) > 0
    assert col.checksum(with_rev=False, with_data=False) > 0
    assert col.checksum(with_rev=False, with_data=True) > 0


def test_truncate():
    col.insert_many([{'value': 1}, {'value': 2}, {'value': 3}])

    # Test preconditions
    assert len(col) == 3

    # Test truncate collection
    result = col.truncate()
    assert 'id' in result
    assert 'name' in result
    assert 'status' in result
    assert 'is_system' in result
    assert len(col) == 0
