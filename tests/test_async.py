import time

import pytest

from arango.database import AsyncDatabase
from arango.exceptions import (
    AQLQueryExecuteError,
    AsyncExecuteError,
    AsyncJobCancelError,
    AsyncJobClearError,
    AsyncJobListError,
    AsyncJobResultError,
    AsyncJobStatusError,
)
from arango.job import AsyncJob
from tests.helpers import extract


def wait_on_job(job):
    """Block until the async job is done."""
    while job.status() != "done":
        time.sleep(0.05)  # pragma: no cover
    return job


def wait_on_jobs(db):
    """Block until all async jobs are finished."""
    while len(db.async_jobs("pending")) > 0:
        time.sleep(0.05)  # pragma: no cover


def test_async_wrapper_attributes(db, col, username):
    async_db = db.begin_async_execution()
    assert isinstance(async_db, AsyncDatabase)
    assert async_db.username == username
    assert async_db.context == "async"
    assert async_db.db_name == db.name
    assert async_db.name == db.name
    assert repr(async_db) == f"<AsyncDatabase {db.name}>"

    async_col = async_db.collection(col.name)
    assert async_col.username == username
    assert async_col.context == "async"
    assert async_col.db_name == db.name
    assert async_col.name == col.name

    async_aql = async_db.aql
    assert async_aql.username == username
    assert async_aql.context == "async"
    assert async_aql.db_name == db.name

    job = async_aql.execute("INVALID QUERY")
    assert isinstance(job, AsyncJob)
    assert isinstance(job.id, str)
    assert repr(job) == f"<AsyncJob {job.id}>"


def test_async_execute_without_result(db, col, docs):
    # Insert test documents asynchronously with return_result set to False
    async_col = db.begin_async_execution(return_result=False).collection(col.name)

    # Ensure that no jobs were returned
    assert async_col.insert(docs[0]) is None
    assert async_col.insert(docs[1]) is None
    assert async_col.insert(docs[2]) is None

    # Ensure that the operations went through
    wait_on_jobs(db)
    assert extract("_key", col.all()) == ["1", "2", "3"]


def test_async_execute_error_in_result(db, col, docs):
    db.collection(col.name).import_bulk(docs)
    async_db = db.begin_async_execution(return_result=True)

    # Test async execution of a bad AQL query
    job = wait_on_job(async_db.aql.execute("INVALID QUERY"))
    with pytest.raises(AQLQueryExecuteError) as err:
        job.result()
    assert err.value.error_code == 1501


def test_async_get_job_status(db, bad_db):
    async_db = db.begin_async_execution(return_result=True)

    # Test get status of a pending job
    job = async_db.aql.execute("RETURN SLEEP(0.1)", count=True)
    assert job.status() == "pending"

    # Test get status of a finished job
    assert wait_on_job(job).status() == "done"
    assert job.result().count() == 1

    # Test get status of a missing job
    with pytest.raises(AsyncJobStatusError) as err:
        job.status()
    assert err.value.error_code == 404

    # Test get status from invalid job
    bad_job = wait_on_job(async_db.aql.execute("INVALID QUERY"))
    bad_job._conn = bad_db._conn
    with pytest.raises(AsyncJobStatusError) as err:
        bad_job.status()
    assert err.value.error_code in {11, 1228}


def test_async_get_job_result(db, bad_db):
    async_db = db.begin_async_execution(return_result=True)

    # Test get result from a pending job
    job = async_db.aql.execute("RETURN SLEEP(0.1)", count=True)
    with pytest.raises(AsyncJobResultError) as err:
        job.result()
    assert err.value.http_code == 204
    assert f"{job.id} not done" in str(err.value)

    # Test get result from a finished job
    assert wait_on_job(job).result().count() == 1

    # Test get result from a cleared job
    with pytest.raises(AsyncJobResultError) as err:
        job.result()
    assert err.value.error_code == 404

    # Test get result from an invalid job
    bad_job = async_db.aql.execute("INVALID QUERY")
    bad_job._conn = bad_db._conn
    with pytest.raises(AsyncJobResultError) as err:
        bad_job.result()
    assert err.value.error_code in {11, 1228}


def test_async_cancel_job(db, bad_db):
    async_db = db.begin_async_execution(return_result=True)

    # Start a long running request to ensure that job can be cancelled
    job = async_db.aql.execute("RETURN SLEEP(5)")

    # Test cancel a pending job
    assert job.cancel() is True

    # Test cancel a missing job
    job._id = "invalid_id"
    with pytest.raises(AsyncJobCancelError) as err:
        job.cancel(ignore_missing=False)
    assert err.value.error_code == 404
    assert job.cancel(ignore_missing=True) is False

    # Test cancel an invalid job
    job = async_db.aql.execute("RETURN SLEEP(5)")
    job._conn = bad_db._conn
    with pytest.raises(AsyncJobCancelError) as err:
        job.cancel()
    assert err.value.error_code in {11, 1228}


def test_async_clear_job(db, bad_db):
    async_db = db.begin_async_execution(return_result=True)

    job = async_db.aql.execute("RETURN 1")

    # Test clear finished job
    assert job.clear(ignore_missing=True) is True

    # Test clear missing job
    with pytest.raises(AsyncJobClearError) as err:
        job.clear(ignore_missing=False)
    assert err.value.error_code == 404
    assert job.clear(ignore_missing=True) is False

    # Test clear with an invalid job
    job._conn = bad_db._conn
    with pytest.raises(AsyncJobClearError) as err:
        job.clear()
    assert err.value.error_code in {11, 1228}


def test_async_execute_errors(bad_db):
    bad_async_db = bad_db.begin_async_execution(return_result=False)
    with pytest.raises(AsyncExecuteError) as err:
        bad_async_db.aql.execute("RETURN 1")
    assert err.value.error_code in {11, 1228}

    bad_async_db = bad_db.begin_async_execution(return_result=True)
    with pytest.raises(AsyncExecuteError) as err:
        bad_async_db.aql.execute("RETURN 1")
    assert err.value.error_code in {11, 1228}


def test_async_clear_jobs(db, bad_db, col, docs):
    async_db = db.begin_async_execution(return_result=True)
    async_col = async_db.collection(col.name)

    job1 = wait_on_job(async_col.insert(docs[0]))
    job2 = wait_on_job(async_col.insert(docs[1]))
    job3 = wait_on_job(async_col.insert(docs[2]))

    # Test clear all async jobs
    assert db.clear_async_jobs() is True
    for job in [job1, job2, job3]:
        with pytest.raises(AsyncJobStatusError) as err:
            job.status()
        assert err.value.error_code == 404

    # Set up test documents again
    job1 = wait_on_job(async_col.insert(docs[0]))
    job2 = wait_on_job(async_col.insert(docs[1]))
    job3 = wait_on_job(async_col.insert(docs[2]))

    # Test clear jobs that have expired
    past = int(time.time()) - 1000000
    assert db.clear_async_jobs(threshold=past) is True
    for job in [job1, job2, job3]:
        assert job.status() == "done"

    # Test clear jobs that have not expired yet
    future = int(time.time()) + 1000000
    assert db.clear_async_jobs(threshold=future) is True
    for job in [job1, job2, job3]:
        with pytest.raises(AsyncJobStatusError) as err:
            job.status()
        assert err.value.error_code == 404

    # Test clear job with bad database
    with pytest.raises(AsyncJobClearError) as err:
        bad_db.clear_async_jobs()
    assert err.value.error_code in {11, 1228}


def test_async_list_jobs(db, col, docs):
    async_db = db.begin_async_execution(return_result=True)
    async_col = async_db.collection(col.name)

    job1 = wait_on_job(async_col.insert(docs[0]))
    job2 = wait_on_job(async_col.insert(docs[1]))
    job3 = wait_on_job(async_col.insert(docs[2]))

    # Test list async jobs that are done
    job_ids = db.async_jobs(status="done")
    assert job1.id in job_ids
    assert job2.id in job_ids
    assert job3.id in job_ids

    # Test list async jobs that are pending
    job4 = async_db.aql.execute("RETURN SLEEP(0.3)")
    assert db.async_jobs(status="pending") == [job4.id]
    wait_on_job(job4)  # Make sure the job is done

    # Test list async jobs with invalid status
    with pytest.raises(AsyncJobListError) as err:
        db.async_jobs(status="bad_status")
    assert err.value.error_code == 400

    # Test list jobs with count
    job_ids = db.async_jobs(status="done", count=1)
    assert len(job_ids) == 1
    assert job_ids[0] in [job1.id, job2.id, job3.id, job4.id]
