from __future__ import absolute_import, unicode_literals

from arango import ArangoClient
from arango.exceptions import (
    DocumentInsertError
)

from .utils import (
    generate_db_name,
    generate_col_name,
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


def test_batch_insert_context_manager_with_result():
    assert len(col) == 0
    with db.batch(return_result=True) as batch:
        batch_col = batch.collection(col_name)
        batch_job1 = batch_col.insert({'_key': '1', 'val': 1})
        batch_job2 = batch_col.insert({'_key': '2', 'val': 2})
        batch_job3 = batch_col.insert({'_key': '2', 'val': 3})

    assert len(col) == 2
    assert col['1']['val'] == 1
    assert col['2']['val'] == 2

    assert batch_job1.status() == 'done'
    assert batch_job1.result()['_key'] == '1'

    assert batch_job2.status() == 'done'
    assert batch_job2.result()['_key'] == '2'

    assert batch_job3.status() == 'error'
    assert isinstance(batch_job3.result(), DocumentInsertError)


def test_batch_insert_context_manager_without_result():
    assert len(col) == 0
    with db.batch(return_result=False) as batch:
        batch_col = batch.collection(col_name)
        batch_job1 = batch_col.insert({'_key': '1', 'val': 1})
        batch_job2 = batch_col.insert({'_key': '2', 'val': 2})
        batch_job3 = batch_col.insert({'_key': '2', 'val': 3})
    assert len(col) == 2
    assert col['1']['val'] == 1
    assert col['2']['val'] == 2
    assert batch_job1 is None
    assert batch_job2 is None
    assert batch_job3 is None


def test_batch_insert_context_manager_commit_on_error():
    assert len(col) == 0
    try:
        with db.batch(return_result=True, commit_on_error=True) as batch:
            batch_col = batch.collection(col_name)
            batch_job1 = batch_col.insert({'_key': '1', 'val': 1})
            raise ValueError('Error!')
    except ValueError:
        assert col['1']['val'] == 1
        assert batch_job1.status() == 'done'
        assert batch_job1.result()['_key'] == '1'


def test_batch_insert_context_manager_no_commit_on_error():
    assert len(col) == 0
    try:
        with db.batch(return_result=True, commit_on_error=False) as batch:
            batch_col = batch.collection(col_name)
            batch_job1 = batch_col.insert({'_key': '1', 'val': 1})
            raise ValueError('Error!')
    except ValueError:
        assert len(col) == 0
        assert batch_job1.status() == 'pending'
        assert batch_job1.result() is None


def test_batch_insert_no_context_manager_with_result():
    assert len(col) == 0
    batch = db.batch(return_result=True)
    batch_col = batch.collection(col_name)
    batch_job1 = batch_col.insert({'_key': '1', 'val': 1})
    batch_job2 = batch_col.insert({'_key': '2', 'val': 2})
    batch_job3 = batch_col.insert({'_key': '2', 'val': 3})

    assert len(col) == 0
    assert batch_job1.status() == 'pending'
    assert batch_job1.result() is None

    assert batch_job2.status() == 'pending'
    assert batch_job2.result() is None

    assert batch_job3.status() == 'pending'
    assert batch_job3.result() is None

    batch.commit()
    assert len(col) == 2
    assert col['1']['val'] == 1
    assert col['2']['val'] == 2

    assert batch_job1.status() == 'done'
    assert batch_job1.result()['_key'] == '1'

    assert batch_job2.status() == 'done'
    assert batch_job2.result()['_key'] == '2'

    assert batch_job3.status() == 'error'
    assert isinstance(batch_job3.result(), DocumentInsertError)


def test_batch_insert_no_context_manager_without_result():
    assert len(col) == 0
    batch = db.batch(return_result=False)
    batch_col = batch.collection(col_name)
    batch_job1 = batch_col.insert({'_key': '1', 'val': 1})
    batch_job2 = batch_col.insert({'_key': '2', 'val': 2})
    batch_job3 = batch_col.insert({'_key': '2', 'val': 3})

    assert batch_job1 is None
    assert batch_job2 is None
    assert batch_job3 is None

    batch.commit()
    assert len(col) == 2
    assert col['1']['val'] == 1
    assert col['2']['val'] == 2


def test_batch_query_context_manager_with_result():
    with db.batch(return_result=True, commit_on_error=False) as batch:
        batch_job1 = batch.collection(col_name).import_bulk([
            {'_key': '1', 'val': 1},
            {'_key': '2', 'val': 2},
            {'_key': '3', 'val': 3},
        ])
        batch_job2 = batch.aql.execute(
            'FOR d IN {} RETURN d'.format(col_name),
            count=True,
            batch_size=1,
            ttl=10,
            optimizer_rules=['+all']
        )
        batch_job3 = batch.aql.execute(
            'FOR d IN {} FILTER d.val == @value RETURN d'.format(col_name),
            bind_vars={'value': 1},
            count=True
        )
    assert batch_job1.result()['created'] == 3
    assert set(d['_key'] for d in batch_job2.result()) == {'1', '2', '3'}
    assert set(d['_key'] for d in batch_job3.result()) == {'1'}
