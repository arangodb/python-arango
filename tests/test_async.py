from __future__ import absolute_import, unicode_literals

from time import sleep, time

import pytest
from six import string_types

from arango import ArangoClient
from arango.api.wrappers.aql import AQL
from arango.api.collections import Collection
from arango.exceptions import (
    AsyncExecuteError,
    AsyncJobClearError,
    AsyncJobResultError,
    AsyncJobStatusError,
    AsyncJobListError,
)
from arango.api.wrappers.graph import Graph
from arango.jobs import AsyncJob

from tests.utils import (
    generate_db_name,
    generate_col_name
)

arango_client = ArangoClient()
db_name = generate_db_name()
db = arango_client.create_database(db_name)
col_name = generate_col_name()
col = db.create_collection(col_name)
col.add_fulltext_index(fields=['val'])


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)


def setup_function(*_):
    col.truncate()


def wait_on_job(job):
    # TODO CHANGED to allow errored out results to process again, added sleep
    while job.status() != 'done':
        sleep(.01)


@pytest.mark.order1
def test_init():
    asynchronous = db.asynchronous(return_result=True)

    assert asynchronous.type == 'async'
    assert 'ArangoDB asynchronous execution' in repr(asynchronous)
    assert isinstance(asynchronous.aql, AQL)
    assert isinstance(asynchronous.graph('test'), Graph)
    assert isinstance(asynchronous.collection('test'), Collection)


@pytest.mark.order2
def test_async_execute_error():
    bad_db = arango_client.db(
        name=db_name,
        username='root',
        password='incorrect'
    )
    asynchronous = bad_db.asynchronous(return_result=False)
    with pytest.raises(AsyncExecuteError):
        asynchronous.collection(col_name).insert({'_key': '1', 'val': 1})
    with pytest.raises(AsyncExecuteError):
        asynchronous.collection(col_name).properties()
    with pytest.raises(AsyncExecuteError):
        asynchronous.aql.execute('FOR d IN {} RETURN d'.format(col_name))


@pytest.mark.order3
def test_async_inserts_without_result():
    # Test precondition
    assert len(col) == 0

    # Insert test documents asynchronously with return_result False
    asynchronous = db.asynchronous(return_result=False)
    job1 = asynchronous.collection(col_name).insert({'_key': '1', 'val': 1})
    job2 = asynchronous.collection(col_name).insert({'_key': '2', 'val': 2})
    job3 = asynchronous.collection(col_name).insert({'_key': '3', 'val': 3})

    # Ensure that no jobs were returned
    for job in [job1, job2, job3]:
        # TODO CHANGED
        assert job.result() is None

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

    # TODO CHANGED Race condition, added more docs
    num_docs = 50000

    # Insert test documents asynchronously with return_result True
    async_col = db.asynchronous(return_result=True).collection(col_name)
    test_docs = [{'_key': str(i), 'val': str(i * 42)} for i in range(num_docs)]
    job1 = async_col.insert_many(test_docs, sync=True)
    job2 = async_col.insert_many(test_docs, sync=True)
    job3 = async_col.insert_many(test_docs, sync=True)
    job4 = async_col.insert_many(test_docs, sync=True)
    job5 = async_col.insert_many(test_docs, sync=True)

    # Test get result from a pending job
    with pytest.raises(AsyncJobResultError) as err:
        job3.result(raise_errors=True)
    assert 'Job {} not done'.format(job3.id) in err.value.message

    # Test get result from finished but with existing jobs
    for job in [job1, job2, job3]:
        assert 'ArangoDB asynchronous job {}'.format(job.id) in repr(job)
        assert isinstance(job.id, string_types)
        wait_on_job(job)
        print(job.result())
        assert len(job.result(raise_errors=True)) == num_docs

    # Test get result from missing jobs
    # TODO CHANGED removed due to enforcement of constant behavior of jobs
    # for job in [job1, job2, job3]:
    # with pytest.raises(AsyncJobResultError) as err:
    # job.result()
    # assert 'Job {} missing'.format(job.id) in err.value.message

    # TODO CHANGED reordered
    # Retrieve the results of the jobs
    assert len(col) == num_docs

    # Test get result without authentication
    # TODO CHANGED This originally failed with for a different reason- the
    # result had already been calculated.  A fourth job has been created to
    # test this.

    bad_db = arango_client.db(
        name=db_name,
        username='root',
        password='incorrect'
    )

    job4._conn = bad_db._conn
    with pytest.raises(AsyncJobResultError) as err:
        job4.result(raise_errors=True)
    assert '401' in err.value.message

    # Test get result that does not exist
    job5._job_id = "BADJOBID"
    with pytest.raises(AsyncJobResultError):
        job5.result(raise_errors=True)


@pytest.mark.order5
def test_async_query():
    # Set up test documents
    asynchronous = db.asynchronous(return_result=True)
    wait_on_job(asynchronous.collection(col_name).import_bulk([
        {'_key': '1', 'val': 1},
        {'_key': '2', 'val': 2},
        {'_key': '3', 'val': 3},
    ]))

    # TODO CHANGED removed due to enforcement of constant behavior of async
    # job errors
    # Test asynchronous execution of an invalid AQL query
    job = asynchronous.aql.execute('THIS IS AN INVALID QUERY')
    wait_on_job(job)
    assert isinstance(job.result(), AsyncJobResultError)

    # Test asynchronous execution of a valid AQL query
    job = asynchronous.aql.execute(
        'FOR d IN {} RETURN d'.format(col_name),
        count=True,
        batch_size=1,
        ttl=10,
        optimizer_rules=['+all']
    )
    wait_on_job(job)
    assert set(d['_key'] for d in job.result()) == {'1', '2', '3'}

    # Test asynchronous execution of another valid AQL query
    job = asynchronous.aql.execute(
        'FOR d IN {} FILTER d.val == @value RETURN d'.format(col_name),
        bind_vars={'value': 1},
        count=True
    )
    wait_on_job(job)
    assert set(d['_key'] for d in job.result()) == {'1'}


@pytest.mark.order6
def test_async_get_status():
    async_col = db.asynchronous(return_result=True).collection(col_name)
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
    bad_db = arango_client.db(
        name=db_name,
        username='root',
        password='incorrect'
    )

    job._conn = bad_db._conn
    with pytest.raises(AsyncJobStatusError) as err:
        job.status()
    assert 'HTTP 401' in err.value.message


# @pytest.mark.order7
# def test_cancel_async_job():
#     async_col = db.asynchronous(return_result=True).collection(col_name)
#     test_docs = [{'_key': str(i), 'val': str(i * 42)} for i in range(1)]
#
#     job1 = async_col.insert_many(test_docs, sync=True)
#     job2 = async_col.insert_many(test_docs, sync=True)
#     job3 = async_col.insert_many(test_docs, sync=True)
#
#     # Test cancel a pending job
#     assert job3.cancel() is True
#
#     # Test cancel a finished job
#     for job in [job1, job2]:
#         wait_on_job(job)
#         assert job.status() == 'done'
#         with pytest.raises(AsyncJobCancelError) as err:
#             job.cancel()
#         assert 'Job {} missing'.format(job.id) in err.value.message
#         assert job.cancel(ignore_missing=True) is False
#
#     # Test cancel a cancelled job
#     sleep(0.5)
#     with pytest.raises(AsyncJobCancelError) as err:
#         job3.cancel(ignore_missing=False)
#     assert 'Job {} missing'.format(job3.id) in err.value.message
#     assert job3.cancel(ignore_missing=True) is False
#
#     # Test cancel without authentication
#     setattr(getattr(job1, '_conn'), '_password', 'incorrect')
#     with pytest.raises(AsyncJobCancelError) as err:
#         job1.cancel(ignore_missing=False)
#     assert 'HTTP 401' in err.value.message


@pytest.mark.order8
def test_clear_async_job():
    # Setup test asynchronous jobs
    asynchronous = db.asynchronous(return_result=True)
    job1 = asynchronous.collection(col_name).insert({'_key': '1', 'val': 1})
    job2 = asynchronous.collection(col_name).insert({'_key': '2', 'val': 2})
    job3 = asynchronous.collection(col_name).insert({'_key': '3', 'val': 3})
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
    bad_db = arango_client.db(
        name=db_name,
        username='root',
        password='incorrect'
    )

    job1._conn = bad_db._conn
    with pytest.raises(AsyncJobClearError) as err:
        job1.clear(ignore_missing=False)
    assert 'HTTP 401' in err.value.message


@pytest.mark.order9
def test_clear_async_jobs():
    # Set up test documents
    asynchronous = db.asynchronous(return_result=True)
    job1 = asynchronous.collection(col_name).insert({'_key': '1', 'val': 1})
    job2 = asynchronous.collection(col_name).insert({'_key': '2', 'val': 2})
    job3 = asynchronous.collection(col_name).insert({'_key': '3', 'val': 3})
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
    asynchronous = db.asynchronous(return_result=True)
    job1 = asynchronous.collection(col_name).insert({'_key': '1', 'val': 1})
    job2 = asynchronous.collection(col_name).insert({'_key': '2', 'val': 2})
    job3 = asynchronous.collection(col_name).insert({'_key': '3', 'val': 3})
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
    asynchronous = db.asynchronous(return_result=True)
    job1 = asynchronous.collection(col_name).insert({'_key': '1', 'val': 1})
    job2 = asynchronous.collection(col_name).insert({'_key': '2', 'val': 2})
    job3 = asynchronous.collection(col_name).insert({'_key': '3', 'val': 3})
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


@pytest.mark.order11
def test_clear_async_jobs_db_level():
    # Set up test documents
    asynchronous = db.asynchronous(return_result=True)
    job1 = asynchronous.collection(col_name).insert({'_key': '1', 'val': 1})
    job2 = asynchronous.collection(col_name).insert({'_key': '2', 'val': 2})
    job3 = asynchronous.collection(col_name).insert({'_key': '3', 'val': 3})
    for job in [job1, job2, job3]:
        wait_on_job(job)
        assert job.status() == 'done'

    # Test clear all async jobs
    assert db.clear_async_jobs() is True
    for job in [job1, job2, job3]:
        with pytest.raises(AsyncJobStatusError) as err:
            job.status()
        assert 'Job {} missing'.format(job.id) in err.value.message

    # Set up test documents again
    asynchronous = db.asynchronous(return_result=True)
    job1 = asynchronous.collection(col_name).insert({'_key': '1', 'val': 1})
    job2 = asynchronous.collection(col_name).insert({'_key': '2', 'val': 2})
    job3 = asynchronous.collection(col_name).insert({'_key': '3', 'val': 3})
    for job in [job1, job2, job3]:
        wait_on_job(job)
        assert job.status() == 'done'

    # Test clear jobs that have not expired yet
    past = int(time()) - 1000000
    assert db.clear_async_jobs(threshold=past) is True
    for job in [job1, job2, job3]:
        assert job.status() == 'done'

    future = int(time()) + 1000000
    assert db.clear_async_jobs(threshold=future) is True
    for job in [job1, job2, job3]:
        with pytest.raises(AsyncJobStatusError) as err:
            job.status()
        assert 'Job {} missing'.format(job.id) in err.value.message

    # Test clear job without authentication
    with pytest.raises(AsyncJobClearError) as err:
        ArangoClient(password='incorrect').db(db_name).clear_async_jobs()
    assert 'HTTP 401' in err.value.message


@pytest.mark.order12
def test_list_async_jobs_db_level():
    # Set up test documents
    asynchronous = db.asynchronous(return_result=True)
    job1 = asynchronous.collection(col_name).insert({'_key': '1', 'val': 1})
    job2 = asynchronous.collection(col_name).insert({'_key': '2', 'val': 2})
    job3 = asynchronous.collection(col_name).insert({'_key': '3', 'val': 3})
    jobs = [job1, job2, job3]
    for job in jobs:
        wait_on_job(job)
    expected_job_ids = [job.id for job in jobs]

    # Test list async jobs that are done
    job_ids = db.async_jobs(status='done')
    assert sorted(expected_job_ids) == sorted(job_ids)

    # Test list async jobs that are pending
    assert db.async_jobs(status='pending') == []

    # Test list async jobs with invalid status
    with pytest.raises(AsyncJobListError):
        db.async_jobs(status='bad_status')

    # Test list jobs with count
    job_ids = db.async_jobs(status='done', count=1)
    assert len(job_ids) == 1
    assert job_ids[0] in expected_job_ids


def test_async_job_failure():
    with pytest.raises(ValueError):
        # test failure on missing response
        AsyncJob(lambda *args, **kwargs: True)

    with pytest.raises(ValueError):
        # test failure on missing connection
        AsyncJob(lambda *args, **kwargs: True, response="not null")
