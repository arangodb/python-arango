from __future__ import absolute_import, unicode_literals

import pytest
from six import string_types

from arango import ArangoClient
from arango.exceptions import *

from tests.utils import (
    generate_db_name,
    generate_col_name,
)

arango_client = ArangoClient()
db_name = generate_db_name()
db = arango_client.create_database(db_name)
ecol_name = generate_col_name()
ecol = db.create_collection(ecol_name, edge=True)
ecol.add_geo_index(['coordinates'])

# Set up test collection and edges
col_name = generate_col_name()
db.create_collection(col_name).import_bulk([
    {'_key': '1'}, {'_key': '2'}, {'_key': '3'}, {'_key': '4'}, {'_key': '5'}
])
edge1 = {'_key': '1', '_from': col_name + '/1', '_to': col_name + '/2'}
edge2 = {'_key': '2', '_from': col_name + '/2', '_to': col_name + '/3'}
edge3 = {'_key': '3', '_from': col_name + '/3', '_to': col_name + '/4'}
edge4 = {'_key': '4', '_from': col_name + '/1', '_to': col_name + '/1'}
edge5 = {'_key': '5', '_from': col_name + '/5', '_to': col_name + '/3'}
test_edges = [edge1, edge2, edge3, edge4, edge5]
test_edge_keys = [e['_key'] for e in test_edges]


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)


def setup_function(*_):
    ecol.truncate()


def test_insert():
    # Test insert first valid edge with return_new and sync
    result = ecol.insert(edge1, return_new=True, sync=True)
    assert len(ecol) == 1
    assert result['_id'] == '{}/{}'.format(ecol_name, edge1['_key'])
    assert result['_key'] == edge1['_key']
    assert isinstance(result['_rev'], string_types)
    assert result['new']['_key'] == edge1['_key']
    assert result['new']['_from'] == edge1['_from']
    assert result['new']['_to'] == edge1['_to']
    assert result['sync'] is True
    assert ecol['1']['_key'] == edge1['_key']
    assert ecol['1']['_from'] == edge1['_from']
    assert ecol['1']['_to'] == edge1['_to']

    # Test insert invalid edges
    with pytest.raises(DocumentInsertError):
        ecol.insert({'foo': 'bar'})
    assert len(ecol) == 1 and '2' not in ecol

    with pytest.raises(DocumentInsertError):
        ecol.insert({'_key': '2'})
    assert len(ecol) == 1 and '2' not in ecol

    with pytest.raises(DocumentInsertError):
        ecol.insert({'_key': '2', '_to': col_name + '/3'})
    assert len(ecol) == 1 and '2' not in ecol

    with pytest.raises(DocumentInsertError):
        ecol.insert({'_key': '2', '_from': col_name + '/3'})
    assert len(ecol) == 1 and '2' not in ecol

    # Test insert second valid edge without return_new and sync
    result = ecol.insert(edge2, return_new=False, sync=False)
    assert len(ecol) == 2
    assert result['_id'] == '{}/{}'.format(ecol_name, edge2['_key'])
    assert result['_key'] == edge2['_key']
    assert isinstance(result['_rev'], string_types)
    assert 'new' not in result
    assert result['sync'] is False
    assert ecol['2']['_key'] == edge2['_key']
    assert ecol['2']['_from'] == edge2['_from']
    assert ecol['2']['_to'] == edge2['_to']


def test_insert_many():
    # Test insert_many valid edges with return_new and sync
    results = ecol.insert_many(test_edges, return_new=True, sync=True)
    for result, edge in zip(results, test_edges):
        key = edge['_key']
        assert result['_id'] == '{}/{}'.format(ecol_name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['new']['_key'] == key
        assert result['new']['_from'] == edge['_from']
        assert result['new']['_to'] == edge['_to']
        assert result['sync'] is True
        assert ecol[key]['_key'] == key
        assert ecol[key]['_from'] == edge['_from']
        assert ecol[key]['_to'] == edge['_to']
    assert len(ecol) == 5
    ecol.truncate()

    # Test insert_many valid edges with return_new and sync
    invalid_edges = [
        {'foo': 'bar'},
        {'_key': '1'},
        {'_key': '2', '_to': col_name + '/3'},
        {'_key': '3', '_from': col_name + '/3'},
    ]
    results = ecol.insert_many(invalid_edges, return_new=False, sync=False)
    for result, edge in zip(results, invalid_edges):
        isinstance(result, DocumentInsertError)
        if '_key' in edge:
            assert edge['_key'] not in ecol
    assert len(ecol) == 0
    ecol.truncate()


def test_update():
    # Set up test edges
    edge = edge1.copy()
    ecol.insert(edge)

    # Test update edge _from and _to to invalid edges
    edge['_from'] = None
    edge['_to'] = None
    result = ecol.update(edge, return_old=True, return_new=True)
    assert result['_id'] == '{}/{}'.format(ecol.name, edge['_key'])
    assert result['_key'] == edge['_key']
    assert isinstance(result['_rev'], string_types)
    assert result['new']['_key'] == edge['_key']
    assert result['new']['_from'] is None
    assert result['new']['_to'] is None
    assert result['old']['_key'] == edge1['_key']
    assert result['old']['_from'] == edge1['_from']
    assert result['old']['_to'] == edge1['_to']
    assert result['sync'] is False
    assert ecol['1']['_key'] == edge1['_key']
    assert ecol['1']['_from'] is None
    assert ecol['1']['_to'] is None

    # TODO should this really be allowed?
    # Test update edge _from and _to to valid edges
    edge['_from'] = edge2['_from']
    edge['_to'] = edge2['_to']
    result = ecol.update(edge, return_old=True, return_new=True)
    assert result['_id'] == '{}/{}'.format(ecol.name, edge['_key'])
    assert result['_key'] == edge['_key']
    assert isinstance(result['_rev'], string_types)
    assert result['new']['_key'] == edge1['_key']
    assert result['new']['_from'] == edge2['_from']
    assert result['new']['_to'] == edge2['_to']
    assert result['old']['_key'] == edge1['_key']
    assert result['old']['_from'] is None
    assert result['old']['_to'] is None
    assert result['sync'] is False
    assert ecol['1']['_key'] == edge1['_key']
    assert ecol['1']['_from'] == edge2['_from']
    assert ecol['1']['_to'] == edge2['_to']


def test_update_many():
    # Set up test edges
    ecol.import_bulk(test_edges)

    # Test update mix of valid and invalid edges
    new_edges = [
        {'_key': '1', '_to': 'foo', '_from': 'bar'},
        {'_key': '2', '_to': 'foo', 'val': 'baz'},
        {'_key': '3', '_from': 'bar'},
        {'_key': '6', '_from': 'bar'},
        {'foo': 'bar', 'bar': 'baz'}
    ]
    results = ecol.update_many(new_edges, return_new=True, return_old=True)

    assert results[0]['old']['_to'] == edge1['_to']
    assert results[0]['old']['_from'] == edge1['_from']
    assert results[0]['new']['_to'] == 'foo'
    assert results[0]['new']['_from'] == 'bar'

    assert results[1]['old']['_to'] == edge2['_to']
    assert results[1]['old']['_from'] == edge2['_from']
    assert results[1]['new']['_to'] == 'foo'
    assert results[1]['new']['_from'] == edge2['_from']

    assert results[2]['old']['_to'] == edge3['_to']
    assert results[2]['old']['_from'] == edge3['_from']
    assert results[2]['new']['_to'] == edge3['_to']
    assert results[2]['new']['_from'] == 'bar'

    assert isinstance(results[3], DocumentUpdateError)
    assert isinstance(results[4], DocumentUpdateError)


def test_update_match():
    # Set up test edges
    ecol.insert_many(test_edges)

    # Test update single matching document
    assert ecol.update_match(
        {'_key': '1'},
        {'_to': 'foo'}
    ) == 1
    assert ecol['1']['_to'] == 'foo'
    assert ecol['1']['_from'] == edge1['_from']

    # Test update multiple matching documents
    assert ecol.update_match(
        {'_from': col_name + '/1'},
        {'foo': 'bar'}
    ) == 2
    assert ecol['1']['foo'] == 'bar'
    assert ecol['4']['foo'] == 'bar'

    # Test update multiple matching documents with arguments
    assert ecol.update_match(
        {'_from': col_name + '/1'},
        {'foo': None, 'bar': 'baz'},
        limit=1,
        sync=True,
        keep_none=False
    ) == 1
    assert ecol['1']['foo'] == 'bar'
    assert 'foo' not in ecol['4']
    assert ecol['4']['bar'] == 'baz'

    # Test unaffected document
    assert ecol['2']['_to'] == edge2['_to']
    assert 'foo' not in ecol['2']

    # Test update matching documents in missing collection
    bad_ecol_name = generate_col_name()
    with pytest.raises(DocumentUpdateError):
        bad_ecol = db.collection(bad_ecol_name)
        bad_ecol.update_match({'_key': '1'}, {'foo': 100})


def test_replace():
    # Set up test edges
    edge = edge1.copy()
    ecol.insert(edge)

    # Test replace edge _from and _to to invalid edges
    edge['_from'] = None
    edge['_to'] = None
    with pytest.raises(DocumentReplaceError):
        ecol.replace(edge, return_old=True, return_new=True)
    assert ecol['1']['_key'] == edge1['_key']
    assert ecol['1']['_from'] == edge1['_from']
    assert ecol['1']['_to'] == edge1['_to']

    # Test replace edge _from and _to to missing edges
    edge['_from'] = 'missing/edge'
    edge['_to'] = 'missing/edge'
    ecol.replace(edge, return_old=True, return_new=True)
    assert ecol['1']['_key'] == edge1['_key']
    assert ecol['1']['_from'] == 'missing/edge'
    assert ecol['1']['_to'] == 'missing/edge'

    # Test replace edge _from and _to to missing edges
    edge['_from'] = edge2['_from']
    edge['_to'] = edge2['_to']
    ecol.replace(edge, return_old=True, return_new=True)
    assert ecol['1']['_key'] == edge1['_key']
    assert ecol['1']['_from'] == edge2['_from']
    assert ecol['1']['_to'] == edge2['_to']


def test_replace_many():
    # Set up test edges
    ecol.insert_many(test_edges)

    # Test replace mix of valid and invalid edges
    new_edges = [
        {'_key': '1', '_to': 'foo', '_from': 'bar'},
        {'_key': '2', '_to': 'foo', 'val': 'baz'},
        {'_key': '3', '_from': 'bar'},
        {'_key': '5', '_from': 'bar'},
        {'foo': 'bar', 'bar': 'baz'}
    ]
    results = ecol.replace_many(new_edges, return_new=True, return_old=True)

    assert results[0]['old']['_to'] == edge1['_to']
    assert results[0]['old']['_from'] == edge1['_from']
    assert results[0]['new']['_to'] == 'foo'
    assert results[0]['new']['_from'] == 'bar'

    assert isinstance(results[1], DocumentReplaceError)
    assert isinstance(results[2], DocumentReplaceError)
    assert isinstance(results[3], DocumentReplaceError)
    assert isinstance(results[4], DocumentReplaceError)


def test_replace_match():
    # Set up test edges
    ecol.insert_many(test_edges)

    # Test replace single matching document with invalid body
    with pytest.raises(DocumentReplaceError):
        ecol.replace_match({'_key': '3'}, {'_to': edge2['_to']})

    # Test replace single matching document with valid body
    assert ecol.replace_match(
        {'_key': '3'},
        {'_to': edge2['_to'], '_from': edge3['_from']}
    ) == 1
    assert ecol['3']['_to'] == edge2['_to']
    assert ecol['3']['_from'] == edge3['_from']

    # Test replace multiple matching documents
    assert ecol.replace_match(
        {'_from': col_name + '/1'},
        {'_to': edge1['_to'], '_from': edge1['_from'], 'foo': 'bar'}
    ) == 2
    assert ecol['1']['foo'] == 'bar'
    assert ecol['1']['_to'] == edge1['_to']
    assert ecol['1']['_from'] == edge1['_from']

    assert ecol['4']['foo'] == 'bar'

    # Test replace multiple matching documents with arguments
    assert ecol.replace_match(
        {'_from': col_name + '/1'},
        {'_to': edge3['_to'], '_from': edge3['_from'], 'foo': 'baz'},
        limit=1,
        sync=True,
    ) == 1
    assert ecol['1']['foo'] == 'baz'
    assert ecol['4']['foo'] == 'bar'

    # Test unaffected document
    assert ecol['2']['_to'] == edge2['_to']
    assert 'foo' not in ecol['2']

    # Test replace matching documents in missing collection
    bad_ecol_name = generate_col_name()
    with pytest.raises(DocumentReplaceError):
        bad_ecol = db.collection(bad_ecol_name)
        bad_ecol.replace_match({'_key': '1'}, {'foo': 100})


def test_delete():
    # Set up test edges
    ecol.import_bulk(test_edges)

    # Test delete (edge) with default options
    result = ecol.delete(edge1)
    assert result['_id'] == '{}/{}'.format(ecol.name, edge1['_key'])
    assert result['_key'] == edge1['_key']
    assert isinstance(result['_rev'], string_types)
    assert result['sync'] is False
    assert 'old' not in result
    assert edge1['_key'] not in ecol
    assert len(ecol) == 4

    # Test delete (edge key) with default options
    result = ecol.delete(edge2['_key'])
    assert result['_id'] == '{}/{}'.format(ecol.name, edge2['_key'])
    assert result['_key'] == edge2['_key']
    assert isinstance(result['_rev'], string_types)
    assert result['sync'] is False
    assert 'old' not in result
    assert edge2['_key'] not in ecol
    assert len(ecol) == 3

    # Test delete (edge) with return_old
    result = ecol.delete(edge3, return_old=True)
    assert result['_id'] == '{}/{}'.format(ecol.name, edge3['_key'])
    assert result['_key'] == edge3['_key']
    assert isinstance(result['_rev'], string_types)
    assert result['sync'] is False
    assert result['old']['_key'] == edge3['_key']
    assert result['old']['_to'] == edge3['_to']
    assert result['old']['_from'] == edge3['_from']
    assert edge3['_key'] not in ecol
    assert len(ecol) == 2

    # Test delete (edge key) with sync
    result = ecol.delete(edge4, sync=True)
    assert result['_id'] == '{}/{}'.format(ecol.name, edge4['_key'])
    assert result['_key'] == edge4['_key']
    assert isinstance(result['_rev'], string_types)
    assert result['sync'] is True
    assert edge4['_key'] not in ecol
    assert len(ecol) == 1

    # Test delete (edge) with check_rev
    rev = ecol[edge5['_key']]['_rev'] + '000'
    bad_edge = edge5.copy()
    bad_edge.update({'_rev': rev})
    with pytest.raises(ArangoError):
        ecol.delete(bad_edge, check_rev=True)
    assert bad_edge['_key'] in ecol
    assert len(ecol) == 1

    # Test delete (edge) with check_rev
    assert ecol.delete(edge4, ignore_missing=True) is False
    with pytest.raises(DocumentDeleteError):
        ecol.delete(edge4, ignore_missing=False)
    assert len(ecol) == 1

    # Test delete with missing edge collection
    bad_col = generate_col_name()
    with pytest.raises(DocumentDeleteError):
        db.collection(bad_col).delete(edge5)

    bad_col = generate_col_name()
    with pytest.raises(DocumentDeleteError):
        db.collection(bad_col).delete(edge5['_key'])


def test_delete_many():
    # Set up test edges
    current_revs = {}
    edges = [edge.copy() for edge in test_edges]

    # Test delete_many (edges) with default options
    ecol.import_bulk(edges)
    results = ecol.delete_many(edges)
    for result, key in zip(results, test_edge_keys):
        assert result['_id'] == '{}/{}'.format(ecol.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['sync'] is False
        assert 'old' not in result
        assert key not in ecol
        current_revs[key] = result['_rev']
    assert len(ecol) == 0

    # Test delete_many (edge keys) with default options
    ecol.import_bulk(edges)
    results = ecol.delete_many(edges)
    for result, key in zip(results, test_edge_keys):
        assert result['_id'] == '{}/{}'.format(ecol.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['sync'] is False
        assert 'old' not in result
        assert key not in ecol
        current_revs[key] = result['_rev']
    assert len(ecol) == 0

    # Test delete_many (edges) with return_old
    ecol.import_bulk(edges)
    results = ecol.delete_many(edges, return_old=True)
    for result, edge in zip(results, edges):
        key = edge['_key']
        assert result['_id'] == '{}/{}'.format(ecol.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['sync'] is False
        assert result['old']['_key'] == key
        assert result['old']['_to'] == edge['_to']
        assert result['old']['_from'] == edge['_from']
        assert key not in ecol
        current_revs[key] = result['_rev']
    assert len(ecol) == 0

    # Test delete_many (edge keys) with sync
    ecol.import_bulk(edges)
    results = ecol.delete_many(edges, sync=True)
    for result, edge in zip(results, edges):
        key = edge['_key']
        assert result['_id'] == '{}/{}'.format(ecol.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['sync'] is True
        assert 'old' not in result
        assert key not in ecol
        current_revs[key] = result['_rev']
    assert len(ecol) == 0

    # Test delete_many (edges) with check_rev
    ecol.import_bulk(edges)
    for edge in edges:
        edge['_rev'] = current_revs[edge['_key']] + '000'
    results = ecol.delete_many(edges, check_rev=True)
    for result, edge in zip(results, edges):
        assert isinstance(result, DocumentRevisionError)
    assert len(ecol) == 5

    # Test delete_many (edges) with missing edges
    ecol.truncate()
    results = ecol.delete_many([{'_key': '6'}, {'_key': '7'}])
    for result, edge in zip(results, edges):
        assert isinstance(result, DocumentDeleteError)
    assert len(ecol) == 0

    # Test delete_many with missing edge collection
    bad_ecol = generate_col_name()
    with pytest.raises(DocumentDeleteError):
        db.collection(bad_ecol).delete_many(edges)

    bad_ecol = generate_col_name()
    with pytest.raises(DocumentDeleteError):
        db.collection(bad_ecol).delete_many(test_edge_keys)


def test_delete_match():
    # Test preconditions
    assert ecol.delete_match({'_from': col_name + '/1'}) == 0

    # Set up test documents
    ecol.import_bulk(test_edges)

    # Test delete matching document with default options
    assert '3' in ecol
    assert ecol.delete_match({'_key': '3'}) == 1
    assert '3' not in ecol

    # Test delete matching documents with sync
    assert '1' in ecol
    assert '4' in ecol
    assert ecol.delete_match({'_from': col_name + '/1'}, sync=True) == 2
    assert '1' not in ecol

    # Test delete matching documents with limit of 2
    assert [doc['_to'] for doc in ecol].count(col_name + '/3') == 2
    assert ecol.delete_match({'_to': col_name + '/3'}, limit=1) == 1
    assert [doc['_to'] for doc in ecol].count(col_name + '/3') == 1
