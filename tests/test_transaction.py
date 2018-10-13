from __future__ import absolute_import, unicode_literals

import pytest
from six import string_types

from arango.database import TransactionDatabase
from arango.exceptions import (
    TransactionStateError,
    TransactionExecuteError,
    TransactionJobResultError
)
from arango.job import TransactionJob
from tests.helpers import clean_doc, extract, generate_string


# noinspection PyUnresolvedReferences
def test_transaction_wrapper_attributes(db, col, username):
    txn_db = db.begin_transaction(timeout=100, sync=True)
    assert txn_db._executor._sync is True
    assert txn_db._executor._timeout == 100
    assert isinstance(txn_db, TransactionDatabase)
    assert txn_db.username == username
    assert txn_db.context == 'transaction'
    assert txn_db.db_name == db.name
    assert txn_db.name == db.name
    assert repr(txn_db) == '<TransactionDatabase {}>'.format(db.name)

    txn_col = txn_db.collection(col.name)
    assert txn_col.username == username
    assert txn_col.context == 'transaction'
    assert txn_col.db_name == db.name
    assert txn_col.name == col.name

    txn_aql = txn_db.aql
    assert txn_aql.username == username
    assert txn_aql.context == 'transaction'
    assert txn_aql.db_name == db.name

    job = txn_col.get(generate_string())
    assert isinstance(job, TransactionJob)
    assert isinstance(job.id, string_types)
    assert repr(job) == '<TransactionJob {}>'.format(job.id)


def test_transaction_execute_without_result(db, col, docs):
    with db.begin_transaction(return_result=False) as txn_db:
        txn_col = txn_db.collection(col.name)

        # Ensure that no jobs are returned
        assert txn_col.insert(docs[0]) is None
        assert txn_col.delete(docs[0]) is None
        assert txn_col.insert(docs[1]) is None
        assert txn_col.delete(docs[1]) is None
        assert txn_col.insert(docs[2]) is None
        assert txn_col.get(docs[2]) is None
        assert txn_db.queued_jobs() is None

    # Ensure that the operations went through
    assert txn_db.queued_jobs() is None
    assert extract('_key', col.all()) == [docs[2]['_key']]


def test_transaction_execute_with_result(db, col, docs):
    with db.begin_transaction(return_result=True) as txn_db:
        txn_col = txn_db.collection(col.name)
        job1 = txn_col.insert(docs[0])
        job2 = txn_col.insert(docs[1])
        job3 = txn_col.get(docs[1])
        jobs = txn_db.queued_jobs()
        assert jobs == [job1, job2, job3]
        assert all(job.status() == 'pending' for job in jobs)

    assert txn_db.queued_jobs() == [job1, job2, job3]
    assert all(job.status() == 'done' for job in txn_db.queued_jobs())
    assert extract('_key', col.all()) == extract('_key', docs[:2])

    # Test successful results
    assert job1.result()['_key'] == docs[0]['_key']
    assert job2.result()['_key'] == docs[1]['_key']
    assert job3.result()['_key'] == docs[1]['_key']


def test_transaction_execute_aql(db, col, docs):
    with db.begin_transaction(
            return_result=True, read=[col.name], write=[col.name]) as txn_db:
        job1 = txn_db.aql.execute(
            'INSERT @data IN @@collection',
            bind_vars={'data': docs[0], '@collection': col.name})
        job2 = txn_db.aql.execute(
            'INSERT @data IN @@collection',
            bind_vars={'data': docs[1], '@collection': col.name})
        job3 = txn_db.aql.execute(
            'RETURN DOCUMENT(@@collection, @key)',
            bind_vars={'key': docs[1]['_key'], '@collection': col.name})
        jobs = txn_db.queued_jobs()
        assert jobs == [job1, job2, job3]
        assert all(job.status() == 'pending' for job in jobs)

    assert txn_db.queued_jobs() == [job1, job2, job3]
    assert all(job.status() == 'done' for job in txn_db.queued_jobs())
    assert extract('_key', col.all()) == extract('_key', docs[:2])

    # Test successful results
    assert extract('_key', job3.result()) == [docs[1]['_key']]


def test_transaction_execute_aql_string_form(db, col, docs):
    with db.begin_transaction(
            return_result=True, read=col.name, write=col.name) as txn_db:
        job1 = txn_db.aql.execute(
            'INSERT @data IN @@collection',
            bind_vars={'data': docs[0], '@collection': col.name})
        job2 = txn_db.aql.execute(
            'INSERT @data IN @@collection',
            bind_vars={'data': docs[1], '@collection': col.name})
        job3 = txn_db.aql.execute(
            'RETURN DOCUMENT(@@collection, @key)',
            bind_vars={'key': docs[1]['_key'], '@collection': col.name})
        jobs = txn_db.queued_jobs()
        assert jobs == [job1, job2, job3]
        assert all(job.status() == 'pending' for job in jobs)

    assert txn_db.queued_jobs() == [job1, job2, job3]
    assert all(job.status() == 'done' for job in txn_db.queued_jobs())
    assert extract('_key', col.all()) == extract('_key', docs[:2])

    # Test successful results
    assert extract('_key', job3.result()) == [docs[1]['_key']]


def test_transaction_execute_error_in_result(db, col, docs):
    txn_db = db.begin_transaction(timeout=100, sync=True)
    txn_col = txn_db.collection(col.name)
    job1 = txn_col.insert(docs[0])
    job2 = txn_col.insert(docs[1])
    job3 = txn_col.insert(docs[1])  # duplicate

    with pytest.raises(TransactionExecuteError) as err:
        txn_db.commit()
    assert err.value.error_code == 1210

    jobs = [job1, job2, job3]
    assert txn_db.queued_jobs() == jobs
    assert all(job.status() == 'pending' for job in jobs)


def test_transaction_empty_commit(db):
    txn_db = db.begin_transaction(return_result=True)
    assert list(txn_db.commit()) == []

    txn_db = db.begin_transaction(return_result=False)
    assert txn_db.commit() is None


def test_transaction_double_commit(db, col, docs):
    txn_db = db.begin_transaction()
    job = txn_db.collection(col.name).insert(docs[0])

    # Test first commit
    assert txn_db.commit() == [job]
    assert job.status() == 'done'
    assert len(col) == 1
    assert clean_doc(col.random()) == docs[0]

    # Test second commit which should fail
    with pytest.raises(TransactionStateError) as err:
        txn_db.commit()
    assert 'already committed' in str(err.value)
    assert job.status() == 'done'
    assert len(col) == 1
    assert clean_doc(col.random()) == docs[0]


def test_transaction_action_after_commit(db, col):
    with db.begin_transaction() as txn_db:
        txn_db.collection(col.name).insert({})

    # Test insert after the transaction has been committed
    with pytest.raises(TransactionStateError) as err:
        txn_db.collection(col.name).insert({})
    assert 'already committed' in str(err.value)
    assert len(col) == 1


def test_transaction_method_not_allowed(db):
    with pytest.raises(TransactionStateError) as err:
        txn_db = db.begin_transaction()
        txn_db.aql.functions()
    assert str(err.value) == 'action not allowed in transaction'

    with pytest.raises(TransactionStateError) as err:
        with db.begin_transaction() as txn_db:
            txn_db.aql.functions()
    assert str(err.value) == 'action not allowed in transaction'


def test_transaction_execute_error(bad_db, col, docs):
    txn_db = bad_db.begin_transaction(return_result=True)
    job = txn_db.collection(col.name).insert_many(docs)

    # Test transaction execute with bad database
    with pytest.raises(TransactionExecuteError):
        txn_db.commit()
    assert len(col) == 0
    assert job.status() == 'pending'


def test_transaction_job_result_not_ready(db, col, docs):
    txn_db = db.begin_transaction(return_result=True)
    job = txn_db.collection(col.name).insert_many(docs)

    # Test get job result before commit
    with pytest.raises(TransactionJobResultError) as err:
        job.result()
    assert str(err.value) == 'result not available yet'

    # Test commit to make sure it still works after the errors
    assert list(txn_db.commit()) == [job]
    assert len(job.result()) == len(docs)
    assert extract('_key', col.all()) == extract('_key', docs)


def test_transaction_execute_raw(db, col, docs):
    # Test execute raw transaction
    doc = docs[0]
    key = doc['_key']
    result = db.execute_transaction(
        command='''
        function (params) {{
            var db = require('internal').db;
            db.{col}.save({{'_key': params.key, 'val': 1}});
            return true;
        }}
        '''.format(col=col.name),
        params={'key': key},
        write=[col.name],
        read=[col.name],
        sync=False,
        timeout=1000,
        max_size=100000,
        allow_implicit=True,
        intermediate_commit_count=10,
        intermediate_commit_size=10000
    )
    assert result is True
    assert doc in col and col[key]['val'] == 1

    # Test execute invalid transaction
    with pytest.raises(TransactionExecuteError) as err:
        db.execute_transaction(command='INVALID COMMAND')
    assert err.value.error_code == 10
