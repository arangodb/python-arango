from __future__ import absolute_import, unicode_literals

import pytest

from arango import ArangoClient
from arango.collections import Collection
from arango.exceptions import TransactionError

from tests.utils import (
    generate_db_name,
    generate_col_name,
)

arango_client = ArangoClient()
db_name = generate_db_name()
db = arango_client.create_database(db_name)
col_name = generate_col_name()
col = db.create_collection(col_name)

doc1 = {'_key': '1', 'data': {'val': 100}}
doc2 = {'_key': '2', 'data': {'val': 200}}
doc3 = {'_key': '3', 'data': {'val': 300}}
doc4 = {'_key': '4', 'data': {'val': 400}}
doc5 = {'_key': '5', 'data': {'val': 500}}
test_docs = [doc1, doc2, doc3, doc4, doc5]
test_doc_keys = [d['_key'] for d in test_docs]


def get_test_docs():
    return [t.copy() for t in test_docs]


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)


def setup_function(*_):
    col.truncate()


def test_init():
    txn = db.transaction(
        read=col_name,
        write=col_name,
        sync=True,
        timeout=1000,
    )
    assert txn.type == 'transaction'
    assert 'ArangoDB transaction {}'.format(txn.id) in repr(txn)
    assert isinstance(txn.collection('test'), Collection)


def test_execute_without_params():
    txn = db.transaction(write=col_name)
    result = txn.execute(
        command='''
        function () {{
            var db = require('internal').db;
            db.{col}.save({{ '_key': '1', 'val': 1}});
            db.{col}.save({{ '_key': '2', 'val': 2}});
            return 'success without params!';
        }}
        '''.format(col=col_name),
        sync=False,
        timeout=1000
    )
    assert result == 'success without params!'
    assert '1' in col and col['1']['val'] == 1
    assert '2' in col and col['2']['val'] == 2


def test_execute_with_params():
    txn = db.transaction(write=col_name)
    result = txn.execute(
        command='''
        function (params) {{
            var db = require('internal').db;
            db.{col}.save({{ '_key': '1', 'val': params.one }});
            db.{col}.save({{ '_key': '2', 'val': params.two }});
            return 'success with params!';
        }}'''.format(col=col_name),
        params={'one': 3, 'two': 4}
    )
    assert result == 'success with params!'
    assert col['1']['val'] == 3
    assert col['2']['val'] == 4


def test_execute_with_errors():
    txn = db.transaction(write=col_name)
    bad_col_name = generate_col_name()
    with pytest.raises(TransactionError):
        txn.execute(
            command='''
                function (params) {{
                var db = require('internal').db;
                db.{col}.save({{ '_key': '1', 'val': params.one }});
                db.{col}.save({{ '_key': '2', 'val': params.two }});
                return 'this transaction should fail!';
            }}'''.format(col=bad_col_name),
            params={'one': 3, 'two': 4}
        )


def test_unsupported_methods():
    txn = db.transaction(write=col_name)

    with pytest.raises(TransactionError):
        txn.collection(col_name).statistics()

    with pytest.raises(TransactionError):
        txn.collection(col_name).properties()

    with pytest.raises(TransactionError):
        txn.collection(col_name).checksum()


def test_transaction_error():
    with pytest.raises(TransactionError):
        with db.transaction(write=col_name) as txn:
            txn_col = txn.collection(col_name)
            txn_col.truncate()
            txn_col.insert(doc1)
            txn_col.insert(doc1)


def test_commit_on_error():
    try:
        with db.transaction(write=col_name, commit_on_error=True) as txn:
            txn_col = txn.collection(col_name)
            txn_col.insert(doc1)
            txn_col.insert(doc2)
            raise ValueError
    except ValueError:
        pass
    assert len(col) == 2
    assert doc1['_key'] in col
    assert doc2['_key'] in col
    assert doc3['_key'] not in col


def test_collection_methods():
    # Set up test documents
    col.import_bulk(test_docs)

    with db.transaction(write=col_name) as txn:
        txn.collection(col_name).truncate()
    assert len(col) == 0


def test_insert_documents():
    # Test document insert in transaction
    with db.transaction(write=col_name) as txn:
        txn_col = txn.collection(col_name)
        txn_col.insert(doc1)
        txn_col.insert(doc2)
        txn_col.insert(doc3)

    assert len(col) == 3
    assert col['1']['data']['val'] == 100
    assert col['2']['data']['val'] == 200
    assert col['3']['data']['val'] == 300

    # Test document insert_many in transaction
    with db.transaction(write=col_name) as txn:
        txn_col = txn.collection(col_name)
        txn_col.truncate()
        txn_col.insert_many(test_docs, sync=True)
    assert len(col) == 5
    assert col['1']['data']['val'] == 100
    assert col['2']['data']['val'] == 200
    assert col['3']['data']['val'] == 300
    assert col['4']['data']['val'] == 400
    assert col['5']['data']['val'] == 500

    # Test document insert_many in transaction
    with pytest.raises(TransactionError):
        with db.transaction(write=col_name) as txn:
            txn_col = txn.collection(col_name)
            txn_col.truncate()
            txn_col.insert(doc1)
            # This should thrown an error
            txn_col.insert(doc1)
    # Transaction should be rolled back
    assert len(col) == 5
    assert col['1']['data']['val'] == 100
    assert col['2']['data']['val'] == 200
    assert col['3']['data']['val'] == 300
    assert col['4']['data']['val'] == 400
    assert col['5']['data']['val'] == 500


def test_update_documents():
    # Test document update in transaction
    with db.transaction(write=col_name) as txn:
        txn_col = txn.collection(col_name)
        txn_col.insert_many(test_docs)
        d1, d2, d3, _, _ = get_test_docs()
        d1['data'] = None
        d2['data'] = {'foo': 600}
        d3['data'] = {'foo': 600}
        txn_col.update(d1, keep_none=False, sync=True)
        txn_col.update(d2, merge=False, sync=True)
        txn_col.update(d3, merge=True, sync=True)
    assert len(col) == 5
    assert 'data' not in col['1']
    assert col['2']['data'] == {'foo': 600}
    assert col['3']['data'] == {'val': 300, 'foo': 600}

    # Test document update_many in transaction
    with db.transaction(write=col_name) as txn:
        txn_col = txn.collection(col_name)
        txn_col.truncate()
        txn_col.insert_many(test_docs)
        d1, d2, d3, _, _ = get_test_docs()
        d1['data'] = None
        d2['data'] = {'foo': 600}
        d3['data'] = {'foo': 600}
        txn_col.update_many([d1, d2], keep_none=False, merge=False)
        txn_col.update_many([d3], keep_none=False, merge=True)
    assert len(col) == 5
    assert 'data' not in col['1']
    assert col['2']['data'] == {'foo': 600}
    assert col['3']['data'] == {'val': 300, 'foo': 600}

    # Test document update_match in transaction
    with db.transaction(write=col_name) as txn:
        txn_col = txn.collection(col_name)
        txn_col.truncate()
        txn_col.insert_many(test_docs)
        txn_col.update_match({'_key': '1'}, {'data': 700})
        txn_col.update_match({'_key': '5'}, {'data': 800})
        txn_col.update_match({'_key': '7'}, {'data': 900})
    assert len(col) == 5
    assert col['1']['data'] == 700
    assert col['5']['data'] == 800


def test_update_documents_with_revisions():
    # Set up test document
    col.insert(doc1)

    # Test document update with revision check
    with db.transaction(write=col_name) as txn:
        txn_col = txn.collection(col_name)
        new_doc = doc1.copy()
        new_doc['data'] = {'val': 999}
        old_rev = col['1']['_rev']
        new_doc['_rev'] = old_rev + '000'
        txn_col.update(new_doc, check_rev=False)
    assert col['1']['_rev'] != old_rev
    assert col['1']['data'] == {'val': 999}

    # Test document update without revision check
    with pytest.raises(TransactionError):
        col.insert(doc2)
        with db.transaction(write=col_name) as txn:
            txn_col = txn.collection(col_name)
            new_doc = doc2.copy()
            new_doc['data'] = {'bar': 'baz'}
            old_rev = col['2']['_rev']
            new_doc['_rev'] = old_rev + '000'
            txn_col.update(new_doc, check_rev=True)
    assert col['2']['_rev'] == old_rev
    assert col['2']['data'] != {'bar': 'baz'}


def test_replace_documents():
    # Test document replace in transaction
    with db.transaction(write=col_name) as txn:
        txn_col = txn.collection(col_name)
        txn_col.insert_many(test_docs)
        d1, d2, d3, _, _ = get_test_docs()
        d1['data'] = None
        d2['data'] = {'foo': 600}
        d3['data'] = {'bar': 600}
        txn_col.replace(d1, sync=True)
        txn_col.replace(d2, sync=True)
        txn_col.replace(d3, sync=True)
    assert len(col) == 5
    assert col['1']['data'] is None
    assert col['2']['data'] == {'foo': 600}
    assert col['3']['data'] == {'bar': 600}

    # Test document replace_many in transaction
    with db.transaction(write=col_name) as txn:
        txn_col = txn.collection(col_name)
        txn_col.truncate()
        txn_col.insert_many(test_docs)
        d1, d2, d3, _, _ = get_test_docs()
        d1['data'] = None
        d2['data'] = {'foo': 600}
        d3['data'] = {'bar': 600}
        txn_col.replace_many([d1, d2])
        txn_col.replace_many([d3])
    assert len(col) == 5
    assert col['1']['data'] is None
    assert col['2']['data'] == {'foo': 600}
    assert col['3']['data'] == {'bar': 600}

    # Test document replace_match in transaction
    with db.transaction(write=col_name) as txn:
        txn_col = txn.collection(col_name)
        txn_col.truncate()
        txn_col.insert_many(test_docs)
        txn_col.replace_match({'_key': '1'}, {'data': 700})
        txn_col.replace_match({'_key': '5'}, {'data': 800})
        txn_col.replace_match({'_key': '7'}, {'data': 900})
    assert len(col) == 5
    assert col['1']['data'] == 700
    assert col['5']['data'] == 800


def test_replace_documents_with_revisions():
    # Set up test document
    col.insert(doc1)

    # TODO does not seem to work with 3.1
    # Test document replace without revision check
    # with db.transaction(write=col_name) as txn:
    #     txn_col = txn.collection(col_name)
    #     new_doc = doc1.copy()
    #     new_doc['data'] = {'val': 999}
    #     old_rev = col['1']['_rev']
    #     new_doc['_rev'] = old_rev + '000'
    #     txn_col.replace(new_doc, check_rev=False)
    # assert col['1']['_rev'] != old_rev
    # assert col['1']['data'] == {'val': 999}

    # Test document replace with revision check
    with pytest.raises(TransactionError):
        col.insert(doc2)
        with db.transaction(write=col_name) as txn:
            txn_col = txn.collection(col_name)
            new_doc = doc2.copy()
            new_doc['data'] = {'bar': 'baz'}
            old_rev = col['2']['_rev']
            new_doc['_rev'] = old_rev + '000'
            txn_col.replace(new_doc, check_rev=True)
    assert col['2']['_rev'] == old_rev
    assert col['2']['data'] != {'bar': 'baz'}


def test_delete_documents():
    # Test document delete in transaction
    with db.transaction(write=col_name) as txn:
        txn_col = txn.collection(col_name)
        txn_col.insert_many(test_docs)
        d1, d2, d3, _, _ = get_test_docs()
        txn_col.delete(d1, sync=True)
        txn_col.delete(d2['_key'], sync=True)
        txn_col.delete(d3['_key'], sync=False)
    assert len(col) == 2
    assert '4' in col
    assert '5' in col

    # Test document delete_many in transaction
    with db.transaction(
        write=col_name,
        timeout=10000,
        commit_on_error=True
    ) as txn:
        txn_col = txn.collection(col_name)
        txn_col.truncate()
        txn_col.insert_many(test_docs)
        txn_col.delete_many([doc1, doc2, doc3], sync=True)
        txn_col.delete_many([doc3, doc4, doc5], sync=False)
    assert len(col) == 0

    # Test document delete_match in transaction
    with db.transaction(
        write=col_name,
        timeout=10000,
        commit_on_error=True
    ) as txn:
        txn_col = txn.collection(col_name)
        txn_col.truncate()
        txn_col.insert_many(test_docs)
        new_docs = get_test_docs()
        for doc in new_docs:
            doc['val'] = 100
        txn_col.update_many(new_docs)
        txn_col.delete_match({'val': 100}, limit=2, sync=True)
    assert len(col) == 3


def test_delete_documents_with_revision():
    # Set up test document
    col.insert(doc1)

    # TODO does not seem to work in 3.1
    # Test document delete without revision check
    # with db.transaction(write=col_name) as txn:
    #     txn_col = txn.collection(col_name)
    #     new_doc = doc1.copy()
    #     new_doc['_rev'] = col['1']['_rev'] + '000'
    #     txn_col.delete(new_doc, check_rev=False)
    # assert len(col) == 0

    # Test document delete with revision check
    col.insert(doc2)
    with pytest.raises(TransactionError):
        with db.transaction(write=col_name) as txn:
            txn_col = txn.collection(col_name)
            new_doc = doc2.copy()
            new_doc['_rev'] = col['2']['_rev'] + '000'
            txn_col.replace(new_doc, check_rev=True)
    assert len(col) == 2


def test_bad_collections():
    with pytest.raises(TransactionError):
        with db.transaction(
            write=['missing'],
            timeout=10000
        ) as txn:
            txn_col = txn.collection(col_name)
            txn_col.insert(doc1)

    with pytest.raises(TransactionError):
        with db.transaction(
            read=[col_name],
            timeout=10000
        ) as txn:
            txn_col = txn.collection(col_name)
            txn_col.insert(doc2)
