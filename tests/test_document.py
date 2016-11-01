from __future__ import absolute_import, unicode_literals

import pytest
from six import string_types

from arango import ArangoClient
from arango.exceptions import *

from .utils import (
    generate_db_name,
    generate_col_name,
    clean_keys,
    ordered
)

arango_client = ArangoClient()
db_name = generate_db_name(arango_client)
db = arango_client.create_database(db_name)
col_name = generate_col_name(db)
col = db.create_collection(col_name)
geo_index = col.add_geo_index(['coordinates'])
bad_col_name = generate_col_name(db)
bad_col = db.collection(bad_col_name)

doc1 = {'_key': '1', 'val': 100, 'text': 'foo', 'coordinates': [1, 1]}
doc2 = {'_key': '2', 'val': 100, 'text': 'bar', 'coordinates': [2, 2]}
doc3 = {'_key': '3', 'val': 100, 'text': 'baz', 'coordinates': [3, 3]}
doc4 = {'_key': '4', 'val': 200, 'text': 'foo', 'coordinates': [4, 4]}
doc5 = {'_key': '5', 'val': 300, 'text': 'foo', 'coordinates': [5, 5]}
test_docs = [doc1, doc2, doc3, doc4, doc5]
test_doc_keys = [d['_key'] for d in test_docs]


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)


def setup_function(*_):
    col.truncate()


def test_insert():
    # Test insert with default options
    for doc in test_docs:
        result = col.insert(doc)
        assert result['_id'] == '{}/{}'.format(col.name, doc['_key'])
        assert result['_key'] == doc['_key']
        assert isinstance(result['_rev'], string_types)
        assert col[doc['_key']]['val'] == doc['val']
    assert len(col) == 5
    col.truncate()

    # Test insert with sync
    doc = doc1
    result = col.insert(doc, sync=True)
    assert result['_id'] == '{}/{}'.format(col.name, doc['_key'])
    assert result['_key'] == doc['_key']
    assert isinstance(result['_rev'], string_types)
    assert result['sync'] is True
    assert col[doc['_key']]['_key'] == doc['_key']
    assert col[doc['_key']]['val'] == doc['val']

    # Test insert without sync
    doc = doc2
    result = col.insert(doc, sync=False)
    assert result['_id'] == '{}/{}'.format(col.name, doc['_key'])
    assert result['_key'] == doc['_key']
    assert isinstance(result['_rev'], string_types)
    assert result['sync'] is False
    assert col[doc['_key']]['_key'] == doc['_key']
    assert col[doc['_key']]['val'] == doc['val']

    # Test insert with return_new
    doc = doc3
    result = col.insert(doc, return_new=True)
    assert result['_id'] == '{}/{}'.format(col.name, doc['_key'])
    assert result['_key'] == doc['_key']
    assert isinstance(result['_rev'], string_types)
    assert result['new']['_id'] == result['_id']
    assert result['new']['_key'] == result['_key']
    assert result['new']['_rev'] == result['_rev']
    assert result['new']['val'] == doc['val']
    assert col[doc['_key']]['_key'] == doc['_key']
    assert col[doc['_key']]['val'] == doc['val']

    # Test insert without return_new
    doc = doc4
    result = col.insert(doc, return_new=False)
    assert result['_id'] == '{}/{}'.format(col.name, doc['_key'])
    assert result['_key'] == doc['_key']
    assert isinstance(result['_rev'], string_types)
    assert 'new' not in result
    assert col[doc['_key']]['_key'] == doc['_key']
    assert col[doc['_key']]['val'] == doc['val']

    # Test insert duplicate document
    with pytest.raises(DocumentInsertError):
        col.insert(doc4)


def test_insert_many():
    # Test insert_many with default options
    results = col.insert_many(test_docs)
    for result, doc in zip(results, test_docs):
        assert result['_id'] == '{}/{}'.format(col.name, doc['_key'])
        assert result['_key'] == doc['_key']
        assert isinstance(result['_rev'], string_types)
        assert col[doc['_key']]['val'] == doc['val']
    assert len(col) == 5
    col.truncate()

    # Test insert_many with sync
    results = col.insert_many(test_docs, sync=True)
    for result, doc in zip(results, test_docs):
        assert result['_id'] == '{}/{}'.format(col.name, doc['_key'])
        assert result['_key'] == doc['_key']
        assert isinstance(result['_rev'], string_types)
        assert result['sync'] is True
        assert col[doc['_key']]['_key'] == doc['_key']
        assert col[doc['_key']]['val'] == doc['val']
    col.truncate()

    # Test insert_many without sync
    results = col.insert_many(test_docs, sync=False)
    for result, doc in zip(results, test_docs):
        assert result['_id'] == '{}/{}'.format(col.name, doc['_key'])
        assert result['_key'] == doc['_key']
        assert isinstance(result['_rev'], string_types)
        assert result['sync'] is False
        assert col[doc['_key']]['_key'] == doc['_key']
        assert col[doc['_key']]['val'] == doc['val']
    col.truncate()

    # Test insert_many with return_new
    results = col.insert_many(test_docs, return_new=True)
    for result, doc in zip(results, test_docs):
        assert result['_id'] == '{}/{}'.format(col.name, doc['_key'])
        assert result['_key'] == doc['_key']
        assert isinstance(result['_rev'], string_types)
        assert result['new']['_id'] == result['_id']
        assert result['new']['_key'] == result['_key']
        assert result['new']['_rev'] == result['_rev']
        assert result['new']['val'] == doc['val']
        assert col[doc['_key']]['_key'] == doc['_key']
        assert col[doc['_key']]['val'] == doc['val']
    col.truncate()

    # Test insert_many without return_new
    results = col.insert_many(test_docs, return_new=False)
    for result, doc in zip(results, test_docs):
        assert result['_id'] == '{}/{}'.format(col.name, doc['_key'])
        assert result['_key'] == doc['_key']
        assert isinstance(result['_rev'], string_types)
        assert 'new' not in result
        assert col[doc['_key']]['_key'] == doc['_key']
        assert col[doc['_key']]['val'] == doc['val']

    # Test insert_many duplicate documents
    results = col.insert_many(test_docs, return_new=False)
    for result, doc in zip(results, test_docs):
        isinstance(result, DocumentInsertError)
        
    # Test get with missing collection
    with pytest.raises(DocumentInsertError):
        bad_col.insert_many(test_docs)


def test_update():
    doc = doc1.copy()
    col.insert(doc)

    # Test update with default options
    doc['val'] = {'foo': 1}
    doc = col.update(doc)
    assert doc['_id'] == '{}/1'.format(col.name)
    assert doc['_key'] == '1'
    assert isinstance(doc['_rev'], string_types)
    assert col['1']['val'] == {'foo': 1}
    current_rev = doc['_rev']

    # Test update with merge
    doc['val'] = {'bar': 2}
    doc = col.update(doc, merge=True)
    assert doc['_id'] == '{}/1'.format(col.name)
    assert doc['_key'] == '1'
    assert isinstance(doc['_rev'], string_types)
    assert doc['_old_rev'] == current_rev
    assert col['1']['val'] == {'foo': 1, 'bar': 2}
    current_rev = doc['_rev']

    # Test update without merge
    doc['val'] = {'baz': 3}
    doc = col.update(doc, merge=False)
    assert doc['_id'] == '{}/1'.format(col.name)
    assert doc['_key'] == '1'
    assert isinstance(doc['_rev'], string_types)
    assert doc['_old_rev'] == current_rev
    assert col['1']['val'] == {'baz': 3}
    current_rev = doc['_rev']

    # Test update with keep_none
    doc['val'] = None
    doc = col.update(doc, keep_none=True)
    assert doc['_id'] == '{}/1'.format(col.name)
    assert doc['_key'] == '1'
    assert isinstance(doc['_rev'], string_types)
    assert doc['_old_rev'] == current_rev
    assert col['1']['val'] is None
    current_rev = doc['_rev']

    # Test update without keep_none
    doc['val'] = None
    doc = col.update(doc, keep_none=False)
    assert doc['_id'] == '{}/1'.format(col.name)
    assert doc['_key'] == '1'
    assert isinstance(doc['_rev'], string_types)
    assert doc['_old_rev'] == current_rev
    assert 'val' not in col['1']
    current_rev = doc['_rev']

    # Test update with return_new and return_old
    doc['val'] = 300
    doc = col.update(doc, return_new=True, return_old=True)
    assert doc['_id'] == '{}/1'.format(col.name)
    assert doc['_key'] == '1'
    assert isinstance(doc['_rev'], string_types)
    assert doc['_old_rev'] == current_rev
    assert doc['new']['_key'] == '1'
    assert doc['new']['val'] == 300
    assert doc['old']['_key'] == '1'
    assert 'val' not in doc['old']
    assert col['1']['val'] == 300
    current_rev = doc['_rev']

    # Test update without return_new and return_old
    doc['val'] = 400
    doc = col.update(doc, return_new=False, return_old=False)
    assert doc['_id'] == '{}/1'.format(col.name)
    assert doc['_key'] == '1'
    assert isinstance(doc['_rev'], string_types)
    assert doc['_old_rev'] == current_rev
    assert 'new' not in doc
    assert 'old' not in doc
    assert col['1']['val'] == 400
    current_rev = doc['_rev']

    # Test update with check_rev
    doc['val'] = 500
    doc['_rev'] = current_rev + '000'
    with pytest.raises(DocumentRevisionError):
        col.update(doc, check_rev=True)
    assert col['1']['val'] == 400

    # Test update with sync
    doc['val'] = 600
    doc = col.update(doc, sync=True)
    assert doc['_id'] == '{}/1'.format(col.name)
    assert doc['_key'] == '1'
    assert isinstance(doc['_rev'], string_types)
    assert doc['_old_rev'] == current_rev
    assert doc['sync'] is True
    assert col['1']['val'] == 600
    current_rev = doc['_rev']

    # Test update without sync
    doc['val'] = 700
    doc = col.update(doc, sync=False)
    assert doc['_id'] == '{}/1'.format(col.name)
    assert doc['_key'] == '1'
    assert isinstance(doc['_rev'], string_types)
    assert doc['_old_rev'] == current_rev
    assert doc['sync'] is False
    assert col['1']['val'] == 700
    current_rev = doc['_rev']

    # Test update missing document
    with pytest.raises(DocumentUpdateError):
        col.update(doc2)
    assert '2' not in col
    assert col['1']['val'] == 700
    assert col['1']['_rev'] == current_rev

    # Test update in missing collection
    with pytest.raises(DocumentUpdateError):
        bad_col.update(doc)


def test_update_many():
    current_revs = {}
    docs = [doc.copy() for doc in test_docs]
    doc_keys = [doc['_key'] for doc in docs]
    col.insert_many(docs)

    # Test update_many with default options
    for doc in docs:
        doc['val'] = {'foo': 1}
    results = col.update_many(docs)
    for result, key in zip(results, doc_keys):
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert col[key]['val'] == {'foo': 1}
        current_revs[key] = result['_rev']

    # Test update_many with merge
    for doc in docs:
        doc['val'] = {'bar': 2}
    results = col.update_many(docs, merge=True)
    for result, doc in zip(results, docs):
        key = doc['_key']
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['_old_rev'] == current_revs[key]
        assert col[key]['val'] == {'foo': 1, 'bar': 2}
        current_revs[key] = result['_rev']

    # Test update_many without merge
    for doc in docs:
        doc['val'] = {'baz': 3}
    results = col.update_many(docs, merge=False)
    for result, doc in zip(results, docs):
        key = doc['_key']
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['_old_rev'] == current_revs[key]
        assert col[key]['val'] == {'baz': 3}
        current_revs[key] = result['_rev']

    # Test update_many with keep_none
    for doc in docs:
        doc['val'] = None
    results = col.update_many(docs, keep_none=True)
    for result, doc in zip(results, docs):
        key = doc['_key']
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['_old_rev'] == current_revs[key]
        assert col[key]['val'] is None
        current_revs[key] = result['_rev']

    # Test update_many without keep_none
    for doc in docs:
        doc['val'] = None
    results = col.update_many(docs, keep_none=False)
    for result, doc in zip(results, docs):
        key = doc['_key']
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['_old_rev'] == current_revs[key]
        assert 'val' not in col[key]
        current_revs[key] = result['_rev']

    # Test update_many with return_new and return_old
    for doc in docs:
        doc['val'] = 300
    results = col.update_many(docs, return_new=True, return_old=True)
    for result, doc in zip(results, docs):
        key = doc['_key']
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['_old_rev'] == current_revs[key]
        assert result['new']['_key'] == key
        assert result['new']['val'] == 300
        assert result['old']['_key'] == key
        assert 'val' not in result['old']
        assert col[key]['val'] == 300
        current_revs[key] = result['_rev']

    # Test update without return_new and return_old
    for doc in docs:
        doc['val'] = 400
    results = col.update_many(docs, return_new=False, return_old=False)
    for result, doc in zip(results, docs):
        key = doc['_key']
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['_old_rev'] == current_revs[key]
        assert 'new' not in result
        assert 'old' not in result
        assert col[key]['val'] == 400
        current_revs[key] = result['_rev']

    # Test update_many with check_rev
    for doc in docs:
        doc['val'] = 500
        doc['_rev'] = current_revs[doc['_key']] + '000'
    results = col.update_many(docs, check_rev=True)
    for result, key in zip(results, doc_keys):
        assert isinstance(result, DocumentRevisionError)
    for doc in col:
        assert doc['val'] == 400

    # Test update_many with sync
    for doc in docs:
        doc['val'] = 600
    results = col.update_many(docs, sync=True)
    for result, doc in zip(results, docs):
        key = doc['_key']
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['_old_rev'] == current_revs[key]
        assert result['sync'] is True
        assert col[key]['val'] == 600
        current_revs[key] = result['_rev']

    # Test update_many without sync
    for doc in docs:
        doc['val'] = 700
    results = col.update_many(docs, sync=False)
    for result, doc in zip(results, docs):
        key = doc['_key']
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['_old_rev'] == current_revs[key]
        assert result['sync'] is False
        assert col[key]['val'] == 700
        current_revs[key] = result['_rev']

    # Test update_many with missing documents
    results = col.update_many([{'_key': '6'}, {'_key': '7'}])
    for result, key in zip(results, doc_keys):
        assert isinstance(result, DocumentUpdateError)
    assert '6' not in col
    assert '7' not in col
    for doc in col:
        assert doc['val'] == 700

    # Test update_many in missing collection
    with pytest.raises(DocumentUpdateError):
        bad_col.update_many(docs)


def test_update_match():
    # Test preconditions
    assert col.update_match({'val': 100}, {'foo': 100}) == 0

    # Set up test documents
    col.import_bulk(test_docs)

    # Test update single matching document
    assert col.update_match({'val': 200}, {'foo': 100}) == 1
    assert col['4']['val'] == 200
    assert col['4']['foo'] == 100

    # Test update multiple matching documents
    assert col.update_match({'val': 100}, {'foo': 100}) == 3
    for key in ['1', '2', '3']:
        assert col[key]['val'] == 100
        assert col[key]['foo'] == 100

    # Test update multiple matching documents with limit
    assert col.update_match(
        {'val': 100},
        {'foo': 200},
        limit=2
    ) == 2
    assert [doc.get('foo') for doc in col].count(200) == 2

    # Test unaffected document
    assert col['5']['val'] == 300
    assert 'foo' not in col['5']

    # Test update matching documents with sync and keep_none
    assert col.update_match(
        {'val': 300},
        {'val': None},
        sync=True,
        keep_none=True
    ) == 1
    assert col['5']['val'] is None

    # Test update matching documents without sync and keep_none
    assert col.update_match(
        {'val': 200},
        {'val': None},
        sync=False,
        keep_none=False
    ) == 1
    assert 'val' not in col['4']

    # Test update matching documents in missing collection
    with pytest.raises(DocumentUpdateError):
        bad_col.update_match({'val': 100}, {'foo': 100})


def test_replace():
    doc = doc1.copy()
    col.insert(doc)

    # Test replace with default options
    doc['foo'] = 200
    doc.pop('val')
    doc = col.replace(doc)
    assert doc['_id'] == '{}/1'.format(col.name)
    assert doc['_key'] == '1'
    assert isinstance(doc['_rev'], string_types)
    assert col['1']['foo'] == 200
    assert 'val' not in col['1']
    current_rev = doc['_rev']

    # Test update with return_new and return_old
    doc['bar'] = 300
    doc = col.replace(doc, return_new=True, return_old=True)
    assert doc['_id'] == '{}/1'.format(col.name)
    assert doc['_key'] == '1'
    assert isinstance(doc['_rev'], string_types)
    assert doc['_old_rev'] == current_rev
    assert doc['new']['_key'] == '1'
    assert doc['new']['bar'] == 300
    assert 'foo' not in doc['new']
    assert doc['old']['_key'] == '1'
    assert doc['old']['foo'] == 200
    assert 'bar' not in doc['old']
    assert col['1']['bar'] == 300
    assert 'foo' not in col['1']
    current_rev = doc['_rev']

    # Test update without return_new and return_old
    doc['baz'] = 400
    doc = col.replace(doc, return_new=False, return_old=False)
    assert doc['_id'] == '{}/1'.format(col.name)
    assert doc['_key'] == '1'
    assert isinstance(doc['_rev'], string_types)
    assert doc['_old_rev'] == current_rev
    assert 'new' not in doc
    assert 'old' not in doc
    assert col['1']['baz'] == 400
    assert 'bar' not in col['1']
    current_rev = doc['_rev']

    # Test replace with check_rev
    doc['foo'] = 500
    doc['_rev'] = current_rev + '000'
    with pytest.raises(DocumentRevisionError):
        col.replace(doc, check_rev=True)
    assert 'foo' not in col['1']
    assert col['1']['baz'] == 400

    # Test replace with sync
    doc['foo'] = 500
    doc = col.replace(doc, sync=True)
    assert doc['_id'] == '{}/1'.format(col.name)
    assert doc['_key'] == '1'
    assert isinstance(doc['_rev'], string_types)
    assert doc['_old_rev'] == current_rev
    assert doc['sync'] is True
    assert col['1']['foo'] == 500
    assert 'baz' not in col['1']
    current_rev = doc['_rev']

    # Test replace without sync
    doc['bar'] = 600
    doc = col.replace(doc, sync=False)
    assert doc['_id'] == '{}/1'.format(col.name)
    assert doc['_key'] == '1'
    assert isinstance(doc['_rev'], string_types)
    assert doc['_old_rev'] == current_rev
    assert doc['sync'] is False
    assert col['1']['bar'] == 600
    assert 'foo' not in col['1']
    current_rev = doc['_rev']

    # Test replace missing document
    with pytest.raises(DocumentReplaceError):
        col.replace(doc2)
    assert col['1']['bar'] == 600
    assert col['1']['_rev'] == current_rev

    # Test replace in missing collection
    with pytest.raises(DocumentReplaceError):
        bad_col.replace(doc)


def test_replace_many():
    current_revs = {}
    docs = [doc.copy() for doc in test_docs]
    col.insert_many(docs)

    # Test replace_many with default options
    for doc in docs:
        doc['foo'] = 200
        doc.pop('val')
    results = col.replace_many(docs)
    for result, key in zip(results, test_doc_keys):
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert col[key]['foo'] == 200
        assert 'val' not in col[key]
        current_revs[key] = result['_rev']

    # Test update with return_new and return_old
    for doc in docs:
        doc['bar'] = 300
        doc.pop('foo')
    results = col.replace_many(docs, return_new=True, return_old=True)
    for result, doc in zip(results, docs):
        key = doc['_key']
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['_old_rev'] == current_revs[key]
        assert result['new']['_key'] == key
        assert result['new']['bar'] == 300
        assert 'foo' not in result['new']
        assert result['old']['_key'] == key
        assert result['old']['foo'] == 200
        assert 'bar' not in result['old']
        assert col[key]['bar'] == 300
        current_revs[key] = result['_rev']

    # Test update without return_new and return_old
    for doc in docs:
        doc['baz'] = 400
        doc.pop('bar')
    results = col.replace_many(docs, return_new=False, return_old=False)
    for result, doc in zip(results, docs):
        key = doc['_key']
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['_old_rev'] == current_revs[key]
        assert 'new' not in result
        assert 'old' not in result
        assert col[key]['baz'] == 400
        assert 'bar' not in col[key]
        current_revs[key] = result['_rev']

    # Test replace_many with check_rev
    for doc in docs:
        doc['foo'] = 500
        doc.pop('baz')
        doc['_rev'] = current_revs[doc['_key']] + '000'
    results = col.replace_many(docs, check_rev=True)
    for result, key in zip(results, test_doc_keys):
        assert isinstance(result, DocumentRevisionError)
    for doc in col:
        assert 'foo' not in doc
        assert doc['baz'] == 400

    # Test replace_many with sync
    for doc in docs:
        doc['foo'] = 500
    results = col.replace_many(docs, sync=True)
    for result, doc in zip(results, docs):
        key = doc['_key']
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['_old_rev'] == current_revs[key]
        assert result['sync'] is True
        assert col[key]['foo'] == 500
        assert 'baz' not in col[key]
        current_revs[key] = result['_rev']

    # Test replace_many without sync
    for doc in docs:
        doc['bar'] = 600
        doc.pop('foo')
    results = col.replace_many(docs, sync=False)
    for result, doc in zip(results, docs):
        key = doc['_key']
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['_old_rev'] == current_revs[key]
        assert result['sync'] is False
        assert col[key]['bar'] == 600
        assert 'foo' not in col[key]
        current_revs[key] = result['_rev']

    # Test replace_many with missing documents
    results = col.replace_many([{'_key': '6'}, {'_key': '7'}])
    for result, key in zip(results, test_doc_keys):
        assert isinstance(result, DocumentReplaceError)
    assert '6' not in col
    assert '7' not in col
    for doc in col:
        assert doc['bar'] == 600
        assert doc['_rev'] == current_revs[doc['_key']]

    # Test replace_many in missing collection
    with pytest.raises(DocumentReplaceError):
        bad_col.replace_many(docs)


def test_replace_match():
    # Test preconditions
    assert col.replace_match({'val': 100}, {'foo': 100}) == 0

    # Set up test documents
    col.import_bulk(test_docs)

    # Test replace single matching document
    assert col.replace_match({'val': 200}, {'foo': 100}) == 1
    assert 'val' not in col['4']
    assert col['4']['foo'] == 100

    # Test replace multiple matching documents
    assert col.replace_match({'val': 100}, {'foo': 100}) == 3
    for key in ['1', '2', '3']:
        assert 'val' not in col[key]
        assert col[key]['foo'] == 100

    # Test replace multiple matching documents with limit
    assert col.replace_match(
        {'foo': 100},
        {'bar': 200},
        limit=2
    ) == 2
    assert [doc.get('bar') for doc in col].count(200) == 2

    # Test unaffected document
    assert col['5']['val'] == 300
    assert 'foo' not in col['5']

    # Test replace matching documents in missing collection
    with pytest.raises(DocumentReplaceError):
        bad_col.replace_match({'val': 100}, {'foo': 100})


def test_delete():
    # Set up test documents
    col.import_bulk(test_docs)

    # Test delete (document) with default options
    result = col.delete(doc1)
    assert result['_id'] == '{}/{}'.format(col.name, doc1['_key'])
    assert result['_key'] == doc1['_key']
    assert isinstance(result['_rev'], string_types)
    assert result['sync'] is False
    assert 'old' not in result
    assert doc1['_key'] not in col
    assert len(col) == 4

    # Test delete (document key) with default options
    result = col.delete(doc2['_key'])
    assert result['_id'] == '{}/{}'.format(col.name, doc2['_key'])
    assert result['_key'] == doc2['_key']
    assert isinstance(result['_rev'], string_types)
    assert result['sync'] is False
    assert 'old' not in result
    assert doc2['_key'] not in col
    assert len(col) == 3

    # Test delete (document) with return_old
    result = col.delete(doc3, return_old=True)
    assert result['_id'] == '{}/{}'.format(col.name, doc3['_key'])
    assert result['_key'] == doc3['_key']
    assert isinstance(result['_rev'], string_types)
    assert result['sync'] is False
    assert result['old']['_key'] == doc3['_key']
    assert result['old']['val'] == 100
    assert doc3['_key'] not in col
    assert len(col) == 2

    # Test delete (document key) with sync
    result = col.delete(doc4, sync=True)
    assert result['_id'] == '{}/{}'.format(col.name, doc4['_key'])
    assert result['_key'] == doc4['_key']
    assert isinstance(result['_rev'], string_types)
    assert result['sync'] is True
    assert doc4['_key'] not in col
    assert len(col) == 1

    # Test delete (document) with check_rev
    rev = col[doc5['_key']]['_rev'] + '000'
    bad_doc = doc5.copy()
    bad_doc.update({'_rev': rev})
    with pytest.raises(ArangoError):
        col.delete(bad_doc, check_rev=True)
    assert bad_doc['_key'] in col
    assert len(col) == 1

    bad_doc.update({'_rev': 'bad_rev'})
    with pytest.raises(ArangoError):
        col.delete(bad_doc, check_rev=True)
    assert bad_doc['_key'] in col
    assert len(col) == 1

    # Test delete (document) with check_rev
    assert col.delete(doc4, ignore_missing=True) is False
    with pytest.raises(ArangoError):
        col.delete(doc4, ignore_missing=False)
    assert len(col) == 1

    # Test delete with missing collection
    with pytest.raises(ArangoError):
        bad_col.delete(doc5)

    with pytest.raises(ArangoError):
        bad_col.delete(doc5['_key'])


def test_delete_many():
    # Set up test documents
    current_revs = {}
    docs = [doc.copy() for doc in test_docs]

    # Test delete_many (documents) with default options
    col.import_bulk(docs)
    results = col.delete_many(docs)
    for result, key in zip(results, test_doc_keys):
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['sync'] is False
        assert 'old' not in result
        assert key not in col
        current_revs[key] = result['_rev']
    assert len(col) == 0

    # Test delete_many (document keys) with default options
    col.import_bulk(docs)
    results = col.delete_many(docs)
    for result, key in zip(results, test_doc_keys):
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['sync'] is False
        assert 'old' not in result
        assert key not in col
        current_revs[key] = result['_rev']
    assert len(col) == 0

    # Test delete_many (documents) with return_old
    col.import_bulk(docs)
    results = col.delete_many(docs, return_old=True)
    for result, doc in zip(results, docs):
        key = doc['_key']
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['sync'] is False
        assert result['old']['_key'] == key
        assert result['old']['val'] == doc['val']
        assert key not in col
        current_revs[key] = result['_rev']
    assert len(col) == 0

    # Test delete_many (document keys) with sync
    col.import_bulk(docs)
    results = col.delete_many(docs, sync=True)
    for result, doc in zip(results, docs):
        key = doc['_key']
        assert result['_id'] == '{}/{}'.format(col.name, key)
        assert result['_key'] == key
        assert isinstance(result['_rev'], string_types)
        assert result['sync'] is True
        assert 'old' not in result
        assert key not in col
        current_revs[key] = result['_rev']
    assert len(col) == 0

    # Test delete_many (documents) with check_rev
    col.import_bulk(docs)
    for doc in docs:
        doc['_rev'] = current_revs[doc['_key']] + '000'
    results = col.delete_many(docs, check_rev=True)
    for result, doc in zip(results, docs):
        assert isinstance(result, DocumentRevisionError)
    assert len(col) == 5

    # Test delete_many (documents) with missing documents
    col.truncate()
    results = col.delete_many([{'_key': '6'}, {'_key': '7'}])
    for result, doc in zip(results, docs):
        assert isinstance(result, DocumentDeleteError)
    assert len(col) == 0

    # Test delete_many with missing collection
    with pytest.raises(DocumentDeleteError):
        bad_col.delete_many(docs)

    with pytest.raises(DocumentDeleteError):
        bad_col.delete_many(test_doc_keys)


def test_delete_match():
    # Test preconditions
    assert col.delete_match({'val': 100}) == 0

    # Set up test documents
    col.import_bulk(test_docs)

    # Test delete matching documents with default options
    assert '4' in col
    assert col.delete_match({'val': 200}) == 1
    assert '4' not in col

    # Test delete matching documents with sync
    assert '5' in col
    assert col.delete_match({'val': 300}, sync=True) == 1
    assert '5' not in col

    # Test delete matching documents with limit of 2
    assert col.delete_match({'val': 100}, limit=2) == 2
    assert [doc['val'] for doc in col].count(100) == 1

    with pytest.raises(DocumentDeleteError):
        bad_col.delete_match({'val': 100})


def test_count():
    # Set up test documents
    col.import_bulk(test_docs)

    assert len(col) == len(test_docs)
    assert col.count() == len(test_docs)

    with pytest.raises(DocumentCountError):
        len(bad_col)

    with pytest.raises(DocumentCountError):
        bad_col.count()


def test_find():
    # Check preconditions
    assert len(col) == 0

    # Set up test documents
    col.import_bulk(test_docs)

    # Test find (single match) with default options
    found = list(col.find({'val': 200}))
    assert len(found) == 1
    assert found[0]['_key'] == '4'

    # Test find (multiple matches) with default options
    found = list(col.find({'val': 100}))
    assert len(found) == 3
    for doc in map(dict, found):
        assert doc['_key'] in {'1', '2', '3'}
        assert doc['_key'] in col

    # Test find with offset
    found = list(col.find({'val': 100}, offset=1))
    assert len(found) == 2
    for doc in map(dict, found):
        assert doc['_key'] in {'1', '2', '3'}
        assert doc['_key'] in col

    # Test find with limit
    for limit in [3, 4, 5]:
        found = list(col.find({}, limit=limit))
        assert len(found) == limit
        for doc in map(dict, found):
            assert doc['_key'] in {'1', '2', '3', '4', '5'}
            assert doc['_key'] in col

    # Test find in empty collection
    col.truncate()
    assert list(col.find({})) == []
    assert list(col.find({'val': 100})) == []
    assert list(col.find({'val': 200})) == []
    assert list(col.find({'val': 300})) == []
    assert list(col.find({'val': 400})) == []

    # Test find in missing collection
    with pytest.raises(DocumentGetError):
        bad_col.find({'val': 100})


def test_has():
    # Set up test documents
    col.import_bulk(test_docs)

    # Test has existing document
    assert col.has('1') is True

    # Test has another existing document
    assert col.has('2') is True

    # Test has missing document
    assert col.has('6') is False

    # Test has with correct revision
    good_rev = col['5']['_rev']
    assert col.has('5', rev=good_rev) is True

    # Test has with invalid revision
    bad_rev = col['5']['_rev'] + '000'
    with pytest.raises(ArangoError):
        col.has('5', rev=bad_rev, match_rev=True)

    # Test has with correct revision and match_rev turned off
    # bad_rev = col['5']['_rev'] + '000'
    # assert col.has('5', rev=bad_rev, match_rev=False) is True

    with pytest.raises(DocumentInError):
        bad_col.has('1')

    with pytest.raises(DocumentInError):
        '1' in bad_col


def test_get():
    # Set up test documents
    col.import_bulk(test_docs)

    # Test get existing document
    result = col.get('1')
    assert result['_key'] == '1'
    assert result['val'] == 100

    # Test get another existing document
    result = col.get('2')
    assert result['_key'] == '2'
    assert result['val'] == 100

    # Test get missing document
    assert col.get('6') is None

    # Test get with correct revision
    good_rev = col['5']['_rev']
    result = col.get('5', rev=good_rev)
    assert result['_key'] == '5'
    assert result['val'] == 300

    # Test get with invalid revision
    bad_rev = col['5']['_rev'] + '000'
    with pytest.raises(ArangoError):
        col.get('5', rev=bad_rev, match_rev=True)
    with pytest.raises(ArangoError):
        col.get('5', rev='bad_rev')

    # Test get with correct revision and match_rev turned off
    # bad_rev = col['5']['_rev'] + '000'
    # result = col.get('5', rev=bad_rev, match_rev=False)
    # assert result['_key'] == '5'
    # assert result['_rev'] != bad_rev
    # assert result['val'] == 300

    # Test get with missing collection
    with pytest.raises(DocumentGetError):
        _ = bad_col.get('1')

    with pytest.raises(DocumentGetError):
        _ = bad_col['1']

    with pytest.raises(DocumentGetError):
        iter(bad_col)


def test_get_many():
    # Test precondition
    assert len(col) == 0

    # Set up test documents
    col.import_bulk(test_docs)

    # Test get_many missing documents
    assert col.get_many(['6']) == []
    assert col.get_many(['6', '7']) == []
    assert col.get_many(['6', '7', '8']) == []

    # Test get_many existing documents
    result = col.get_many(['1'])
    result = clean_keys(result)
    assert result == [doc1]

    result = col.get_many(['2'])
    result = clean_keys(result)
    assert result == [doc2]

    result = col.get_many(['3', '4'])
    assert clean_keys(result) == [doc3, doc4]

    result = col.get_many(['1', '3', '6'])
    assert clean_keys(result) == [doc1, doc3]

    # Test get_many in empty collection
    col.truncate()
    assert col.get_many([]) == []
    assert col.get_many(['1']) == []
    assert col.get_many(['2', '3']) == []
    assert col.get_many(['2', '3', '4']) == []

    with pytest.raises(DocumentGetError):
        bad_col.get_many(['2', '3', '4'])


def test_all():
    # Check preconditions
    assert len(list(col.all())) == 0

    # Set up test documents
    col.import_bulk(test_docs)

    # Test all with default options
    result = list(col.all())
    assert ordered(clean_keys(result)) == test_docs

    # Test all with flush
    # result = list(col.all(flush=True, flush_wait=1))
    # assert ordered(clean_keys(result)) == test_docs

    # Test all with count
    result = col.all(count=True)
    assert result.count() == len(test_docs)
    assert ordered(clean_keys(result)) == test_docs

    # Test all with batch size
    result = col.all(count=True, batch_size=1)
    assert result.count() == len(test_docs)
    assert ordered(clean_keys(result)) == test_docs

    # Test all with time-to-live
    result = col.all(count=True, ttl=1000)
    assert result.count() == len(test_docs)
    assert ordered(clean_keys(result)) == test_docs

    # Test all with filters
    result = col.all(
        count=True,
        filter_fields=['text'],
        filter_type='exclude'
    )
    assert result.count() == 5
    for doc in result:
        assert 'text' not in doc

    # Test all with a limit of 0
    result = col.all(count=True, limit=0)
    assert result.count() == len(test_docs)
    assert ordered(clean_keys(result)) == test_docs

    # Test all with a limit of 1
    result = col.all(count=True, limit=1)
    assert result.count() == 1
    assert len(list(result)) == 1
    for doc in list(clean_keys(result)):
        assert doc in test_docs

    # Test all with a limit of 3
    result = col.all(count=True, limit=3)
    assert result.count() == 3
    assert len(list(result)) == 3
    for doc in list(clean_keys(list(result))):
        assert doc in test_docs

    # Test all in missing collection
    with pytest.raises(DocumentGetError):
        bad_col.all()


def test_random():
    # Set up test documents
    col.import_bulk(test_docs)

    # Test random in non-empty collection
    for attempt in range(10):
        random_doc = col.random()
        assert clean_keys(random_doc) in test_docs

    # Test random in empty collection
    col.truncate()
    for attempt in range(10):
        random_doc = col.random()
        assert random_doc is None

    # Test random in missing collection
    with pytest.raises(DocumentGetError):
        bad_col.random()


def test_find_near():
    # Set up test documents
    col.import_bulk(test_docs)

    # Test find_near with default options
    result = col.find_near(latitude=1, longitude=1)
    assert [doc['_key'] for doc in result] == ['1', '2', '3', '4', '5']

    # Test find_near with limit of 0
    result = col.find_near(latitude=1, longitude=1, limit=0)
    assert [doc['_key'] for doc in result] == []

    # Test find_near with limit of 1
    result = col.find_near(latitude=1, longitude=1, limit=1)
    assert [doc['_key'] for doc in result] == ['1']

    # Test find_near with limit of 3
    result = col.find_near(latitude=1, longitude=1, limit=3)
    assert [doc['_key'] for doc in result] == ['1', '2', '3']

    # Test find_near with limit of 3 (another set of coordinates)
    result = col.find_near(latitude=5, longitude=5, limit=3)
    assert [doc['_key'] for doc in result] == ['5', '4', '3']

    # Test random in missing collection
    with pytest.raises(DocumentGetError):
        bad_col.find_near(latitude=1, longitude=1, limit=1)

    # Test find_near in an empty collection
    col.truncate()
    result = col.find_near(latitude=1, longitude=1, limit=1)
    assert list(result) == []
    result = col.find_near(latitude=5, longitude=5, limit=4)
    assert list(result) == []

    # Test find near in missing collection
    with pytest.raises(DocumentGetError):
        bad_col.find_near(latitude=1, longitude=1, limit=1)


def test_find_in_range():
    # Set up required index
    col.add_skiplist_index(['val'])

    # Set up test documents
    col.import_bulk(test_docs)

    # Test find_in_range with default options
    result = col.find_in_range(field='val', lower=100, upper=200)
    assert [doc['_key'] for doc in result] == ['1', '2', '3', '4']

    # Test find_in_range with limit of 0
    result = col.find_in_range(field='val', lower=100, upper=200, limit=0)
    assert [doc['_key'] for doc in result] == []

    # Test find_in_range with limit of 3
    result = col.find_in_range(field='val', lower=100, upper=200, limit=3)
    assert [doc['_key'] for doc in result] == ['1', '2', '3']

    # Test find_in_range with offset of 0
    result = col.find_in_range(field='val', lower=100, upper=200, offset=0)
    assert [doc['_key'] for doc in result] == ['1', '2', '3', '4']

    # Test find_in_range with offset of 2
    result = col.find_in_range(field='val', lower=100, upper=200, offset=2)
    assert [doc['_key'] for doc in result] == ['3', '4']

    # Test find_in_range without inclusive
    result = col.find_in_range('val', 100, 200, inclusive=False)
    assert [doc['_key'] for doc in result] == []

    # Test find_in_range without inclusive
    result = col.find_in_range('val', 100, 300, inclusive=False)
    assert [doc['_key'] for doc in result] == ['4']

    # Test find_in_range in missing collection
    with pytest.raises(DocumentGetError):
        bad_col.find_in_range(field='val', lower=100, upper=200, offset=2)


# TODO the WITHIN geo function does not seem to work properly
def test_find_in_radius():
    col.import_bulk([
        {'_key': '1', 'coordinates': [1, 1]},
        {'_key': '2', 'coordinates': [1, 4]},
        {'_key': '3', 'coordinates': [4, 1]},
        {'_key': '4', 'coordinates': [4, 4]},
    ])
    result = list(col.find_in_radius(3, 3, 10, 'distance'))
    for doc in result:
        assert 'distance' in doc

    # Test find_in_radius in missing collection
    with pytest.raises(DocumentGetError):
        bad_col.find_in_radius(3, 3, 10, 'distance')


def test_find_in_box():
    # Set up test documents
    d1 = {'_key': '1', 'coordinates': [1, 1]}
    d2 = {'_key': '2', 'coordinates': [1, 5]}
    d3 = {'_key': '3', 'coordinates': [5, 1]}
    d4 = {'_key': '4', 'coordinates': [5, 5]}
    col.import_bulk([d1, d2, d3, d4])

    # Test find_in_box with default options
    result = col.find_in_box(
        latitude1=0,
        longitude1=0,
        latitude2=6,
        longitude2=3,
        geo_field=geo_index['id']
    )
    assert clean_keys(result) == [d3, d1]

    # Test find_in_box with limit of 0
    result = col.find_in_box(
        latitude1=0,
        longitude1=0,
        latitude2=6,
        longitude2=3,
        limit=0,
        geo_field=geo_index['id']
    )
    assert clean_keys(result) == [d3, d1]

    # Test find_in_box with limit of 1
    result = col.find_in_box(
        latitude1=0,
        longitude1=0,
        latitude2=6,
        longitude2=3,
        limit=1,
    )
    assert clean_keys(result) == [d3]

    # Test find_in_box with limit of 4
    result = col.find_in_box(
        latitude1=0,
        longitude1=0,
        latitude2=10,
        longitude2=10,
        limit=4
    )
    assert clean_keys(result) == [d4, d3, d2, d1]

    # Test find_in_box with skip 1
    result = col.find_in_box(
        latitude1=0,
        longitude1=0,
        latitude2=6,
        longitude2=3,
        skip=1,
    )
    assert clean_keys(result) == [d1]

    # Test find_in_box with skip 3
    result = col.find_in_box(
        latitude1=0,
        longitude1=0,
        latitude2=10,
        longitude2=10,
        skip=2
    )
    assert clean_keys(result) == [d2, d1]

    # Test find_in_box in missing collection
    with pytest.raises(DocumentGetError):
        bad_col.find_in_box(
            latitude1=0,
            longitude1=0,
            latitude2=6,
            longitude2=3,
        )


def test_find_by_text():
    # Set up required index
    col.add_fulltext_index(['text'])

    # Set up test documents
    col.import_bulk(test_docs)

    # Test find_by_text with default options
    result = col.find_by_text(key='text', query='bar,|baz')
    assert clean_keys(list(result)) == [doc2, doc3]

    # Test find_by_text with limit
    result = col.find_by_text(key='text', query='foo', limit=1)
    assert len(list(result)) == 1
    result = col.find_by_text(key='text', query='foo', limit=2)
    assert len(list(result)) == 2
    result = col.find_by_text(key='text', query='foo', limit=3)
    assert len(list(result)) == 3

    # Test find_by_text with invalid queries
    with pytest.raises(DocumentGetError):
        col.find_by_text(key='text', query='+')
    with pytest.raises(DocumentGetError):
        col.find_by_text(key='text', query='|')

    # Test find_by_text with missing column
    with pytest.raises(DocumentGetError):
        col.find_by_text(key='missing', query='foo')


def test_import_bulk():
    # Test import_bulk with default options
    result = col.import_bulk(test_docs)
    assert result['created'] == 5
    assert result['errors'] == 0
    assert 'details' in result
    assert len(col) == 5
    for doc in test_docs:
        key = doc['_key']
        assert key in col
        assert col[key]['_key'] == key
        assert col[key]['val'] == doc['val']
        assert col[key]['coordinates'] == doc['coordinates']
    col.truncate()

    # Test import bulk without details
    result = col.import_bulk(test_docs, details=False)
    assert result['created'] == 5
    assert result['errors'] == 0
    assert 'details' not in result
    assert len(col) == 5
    for doc in test_docs:
        key = doc['_key']
        assert key in col
        assert col[key]['_key'] == key
        assert col[key]['val'] == doc['val']
        assert col[key]['coordinates'] == doc['coordinates']
    col.truncate()

    # Test import_bulk duplicates with halt_on_error
    with pytest.raises(DocumentInsertError):
        col.import_bulk([doc1, doc1], halt_on_error=True)
    assert len(col) == 0

    # Test import bulk duplicates without halt_on_error
    result = col.import_bulk([doc2, doc2], halt_on_error=False)
    assert result['created'] == 1
    assert result['errors'] == 1
    assert len(col) == 1

    # Test import bulk in missing collection
    with pytest.raises(DocumentInsertError):
        bad_col.import_bulk([doc3, doc4], halt_on_error=True)
    assert len(col) == 1
