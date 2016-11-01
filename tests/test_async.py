from __future__ import absolute_import, unicode_literals

from time import sleep, time

import pytest
from six import string_types

from arango import ArangoClient
from arango.aql import AQL
from arango.collections import Collection
from arango.exceptions import (
    AsyncExecuteError,
    AsyncJobCancelError,
    AsyncJobClearError,
    AsyncJobResultError,
    AsyncJobStatusError,
    AsyncJobListError,
    AQLQueryExecuteError
)
from arango.graph import Graph

from .utils import (
    generate_db_name,
    generate_col_name
)

arango_client = ArangoClient()
db_name = generate_db_name(arango_client)
db = arango_client.create_database(db_name)
col_name = generate_col_name(db)
col = db.create_collection(col_name)
col.add_fulltext_index(fields=['val'])


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)


def setup_function(*_):
    col.truncate()


def wait_on_job(job):
    while job.status() == 'pending':
        pass


@pytest.mark.order1
def test_init():
    async = db.async(return_result=True)

    assert async.type == 'async'
    assert 'ArangoDB asynchronous execution' in repr(async)
    assert isinstance(async.aql, AQL)
    assert isinstance(async.graph('test'), Graph)
    assert isinstance(async.collection('test'), Collection)


@pytest.mark.order2
def test_async_execute_error():
    bad_db = arango_client.db(
        name=db_name,
        username='root',
        password='incorrect'
    )
    async = bad_db.async(return_result=False)
    with pytest.raises(AsyncExecuteError):
        async.collection(col_name).insert({'_key': '1', 'val': 1})
    with pytest.raises(AsyncExecuteError):
        async.collection(col_name).properties()
    with pytest.raises(AsyncExecuteError):
        async.aql.execute('FOR d IN {} RETURN d'.format(col_name))


@pytest.mark.order3
def test_async_inserts_without_result():
    # Test precondition
    assert len(col) == 0

    # Insert test documents asynchronously with return_result False
    async = db.async(return_result=False)
    job1 = async.collection(col_name).insert({'_key': '1', 'val': 1})
    job2 = async.collection(col_name).insert({'_key': '2', 'val': 2})
    job3 = async.collection(col_name).insert({'_key': '3', 'val': 3})

    # Ensure that no jobs were returned
    for job in [job1, job2, job3]:
        assert job is None

    # Ensure that the asynchronously requests went through
    sleep(0.5)
    assert len(col) == 3
    assert col['1']['val'] == 1
    assert col['2']['val'] == 2
    assert col['3']['val'] == 3


@pytest.mark.order4
def test_async_inserts_with_result():
    # Test precondition
    assert len(col) == 0

    # Insert test documents asynchronously with return_result True
    async_col = db.async(return_result=True).collection(col_name)
    test_docs = [{'_key': str(i), 'val': str(i * 42)} for i in range(10000)]
    job1 = async_col.insert_many(test_docs, sync=True)
    job2 = async_col.insert_many(test_docs, sync=True)
    job3 = async_col.insert_many(test_docs, sync=True)

    # Test get result from a pending job
    with pytest.raises(AsyncJobResultError) as err:
        job3.result()
    assert 'Job {} not done'.format(job3.id) in err.value.message

    # Test get result from finished but with existing jobs
    for job in [job1, job2, job3]:
        assert 'ArangoDB asynchronous job {}'.format(job.id) in repr(job)
        assert isinstance(job.id, string_types)
        wait_on_job(job)
        assert len(job.result()) == 10000

    # Test get result from missing jobs
    for job in [job1, job2, job3]:
        with pytest.raises(AsyncJobResultError) as err:
            job.result()
        assert 'Job {} missing'.format(job.id) in err.value.message

    # Test get result without authentication
    setattr(getattr(job1, '_conn'), '_password', 'incorrect')
    with pytest.raises(AsyncJobResultError) as err:
        job.result()
    assert '401' in err.value.message

    # Retrieve the results of the jobs
    assert len(col) == 10000


@pytest.mark.order5
def test_async_query():
    # Set up test documents
    async = db.async(return_result=True)
    wait_on_job(async.collection(col_name).import_bulk([
        {'_key': '1', 'val': 1},
        {'_key': '2', 'val': 2},
        {'_key': '3', 'val': 3},
    ]))

    # Test asynchronous execution of an invalid AQL query
    job = async.aql.execute('THIS IS AN INVALID QUERY')
    wait_on_job(job)
    assert isinstance(job.result(), AQLQueryExecuteError)

    # Test asynchronous execution of a valid AQL query
    job = async.aql.execute(
        'FOR d IN {} RETURN d'.format(col_name),
        count=True,
        batch_size=1,
        ttl=10,
        optimizer_rules=['+all']
    )
    wait_on_job(job)
    assert set(d['_key'] for d in job.result()) == {'1', '2', '3'}

    # Test asynchronous execution of another valid AQL query
    job = async.aql.execute(
        'FOR d IN {} FILTER d.val == @value RETURN d'.format(col_name),
        bind_vars={'value': 1},
        count=True
    )
    wait_on_job(job)
    assert set(d['_key'] for d in job.result()) == {'1'}


@pytest.mark.order6
def test_async_get_status():
    async_col = db.async(return_result=True).collection(col_name)
    test_docs = [{'_key': str(i), 'val': str(i * 42)} for i in range(10000)]

    # Test get status of a pending job
    job = async_col.insert_many(test_docs, sync=True)
    assert job.status() == 'pending'

    # Test get status of a finished job
    wait_on_job(job)
    assert job.status() == 'done'
    assert len(job.result()) == len(test_docs)

    # Test get status of a missing job
    with pytest.raises(AsyncJobStatusError) as err:
        job.status()
    assert 'Job {} missing'.format(job.id) in err.value.message

    # Test get status without authentication
    setattr(getattr(job, '_conn'), '_password', 'incorrect')
    with pytest.raises(AsyncJobStatusError) as err:
        job.status()
    assert 'HTTP 401' in err.value.message


@pytest.mark.order7
def test_cancel_async_job():
    async_col = db.async(return_result=True).collection(col_name)
    test_docs = [{'_key': str(i), 'val': str(i * 42)} for i in range(10000)]

    job1 = async_col.insert_many(test_docs, sync=True)
    job2 = async_col.insert_many(test_docs, sync=True)
    job3 = async_col.insert_many(test_docs, sync=True)

    # Test cancel a pending job
    assert job3.cancel() is True

    # Test cancel a finished job
    for job in [job1, job2]:
        wait_on_job(job)
        assert job.status() == 'done'
        with pytest.raises(AsyncJobCancelError) as err:
            job.cancel()
        assert 'Job {} missing'.format(job.id) in err.value.message
        assert job.cancel(ignore_missing=True) is False

    # Test cancel a cancelled job
    sleep(0.5)
    with pytest.raises(AsyncJobCancelError) as err:
        job3.cancel(ignore_missing=False)
    assert 'Job {} missing'.format(job3.id) in err.value.message
    assert job3.cancel(ignore_missing=True) is False

    # Test cancel without authentication
    setattr(getattr(job1, '_conn'), '_password', 'incorrect')
    with pytest.raises(AsyncJobCancelError) as err:
        job1.cancel(ignore_missing=False)
    assert 'HTTP 401' in err.value.message


@pytest.mark.order8
def test_clear_async_job():
    # Setup test asynchronous jobs
    async = db.async(return_result=True)
    job1 = async.collection(col_name).insert({'_key': '1', 'val': 1})
    job2 = async.collection(col_name).insert({'_key': '2', 'val': 2})
    job3 = async.collection(col_name).insert({'_key': '3', 'val': 3})
    for job in [job1, job2, job3]:
        wait_on_job(job)

    # Test clear finished jobs
    assert job1.clear(ignore_missing=True) is True
    assert job2.clear(ignore_missing=True) is True
    assert job3.clear(ignore_missing=False) is True

    # Test clear missing jobs
    for job in [job1, job2, job3]:
        with pytest.raises(AsyncJobClearError) as err:
            job.clear(ignore_missing=False)
        assert 'Job {} missing'.format(job.id) in err.value.message
        assert job.clear(ignore_missing=True) is False

    # Test clear without authentication
    setattr(getattr(job1, '_conn'), '_password', 'incorrect')
    with pytest.raises(AsyncJobClearError) as err:
        job1.clear(ignore_missing=False)
    assert 'HTTP 401' in err.value.message


@pytest.mark.order9
def test_clear_async_jobs():
    # Set up test documents
    async = db.async(return_result=True)
    job1 = async.collection(col_name).insert({'_key': '1', 'val': 1})
    job2 = async.collection(col_name).insert({'_key': '2', 'val': 2})
    job3 = async.collection(col_name).insert({'_key': '3', 'val': 3})
    for job in [job1, job2, job3]:
        wait_on_job(job)
        assert job.status() == 'done'

    # Test clear all async jobs
    assert arango_client.clear_async_jobs() is True
    for job in [job1, job2, job3]:
        with pytest.raises(AsyncJobStatusError) as err:
            job.status()
        assert 'Job {} missing'.format(job.id) in err.value.message

    # Set up test documents again
    async = db.async(return_result=True)
    job1 = async.collection(col_name).insert({'_key': '1', 'val': 1})
    job2 = async.collection(col_name).insert({'_key': '2', 'val': 2})
    job3 = async.collection(col_name).insert({'_key': '3', 'val': 3})
    for job in [job1, job2, job3]:
        wait_on_job(job)
        assert job.status() == 'done'

    # Test clear jobs that have not expired yet
    past = int(time()) - 1000000
    assert arango_client.clear_async_jobs(threshold=past) is True
    for job in [job1, job2, job3]:
        assert job.status() == 'done'

    future = int(time()) + 1000000
    assert arango_client.clear_async_jobs(threshold=future) is True
    for job in [job1, job2, job3]:
        with pytest.raises(AsyncJobStatusError) as err:
            job.status()
        assert 'Job {} missing'.format(job.id) in err.value.message

    # Test clear job without authentication
    with pytest.raises(AsyncJobClearError) as err:
        ArangoClient(password='incorrect').clear_async_jobs()
    assert 'HTTP 401' in err.value.message


@pytest.mark.order10
def test_list_async_jobs():
    # Set up test documents
    async = db.async(return_result=True)
    job1 = async.collection(col_name).insert({'_key': '1', 'val': 1})
    job2 = async.collection(col_name).insert({'_key': '2', 'val': 2})
    job3 = async.collection(col_name).insert({'_key': '3', 'val': 3})
    jobs = [job1, job2, job3]
    for job in jobs:
        wait_on_job(job)
    expected_job_ids = [job.id for job in jobs]

    # Test list async jobs that are done
    job_ids = arango_client.async_jobs(status='done')
    assert sorted(expected_job_ids) == sorted(job_ids)

    # Test list async jobs that are pending
    assert arango_client.async_jobs(status='pending') == []

    # Test list async jobs with invalid status
    with pytest.raises(AsyncJobListError):
        arango_client.async_jobs(status='bad_status')

    # Test list jobs with count
    job_ids = arango_client.async_jobs(status='done', count=1)
    assert len(job_ids) == 1
    assert job_ids[0] in expected_job_ids
