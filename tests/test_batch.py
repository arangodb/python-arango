import pytest

from arango.database import BatchDatabase
from arango.exceptions import BatchJobResultError, BatchStateError, DocumentInsertError
from arango.job import BatchJob
from tests.helpers import clean_doc, extract


def test_batch_wrapper_attributes(db, col, username):
    batch_db = db.begin_batch_execution()
    assert isinstance(batch_db, BatchDatabase)
    assert batch_db.username == username
    assert batch_db.context == "batch"
    assert batch_db.db_name == db.name
    assert batch_db.name == db.name
    assert repr(batch_db) == f"<BatchDatabase {db.name}>"

    batch_col = batch_db.collection(col.name)
    assert batch_col.username == username
    assert batch_col.context == "batch"
    assert batch_col.db_name == db.name
    assert batch_col.name == col.name

    batch_aql = batch_db.aql
    assert batch_aql.username == username
    assert batch_aql.context == "batch"
    assert batch_aql.db_name == db.name

    job = batch_aql.execute("INVALID QUERY")
    assert isinstance(job, BatchJob)
    assert isinstance(job.id, str)
    assert repr(job) == f"<BatchJob {job.id}>"


def test_batch_execute_without_result(db, col, docs):
    with db.begin_batch_execution(return_result=False) as batch_db:
        batch_col = batch_db.collection(col.name)

        # Ensure that no jobs are returned
        assert batch_col.insert(docs[0]) is None
        assert batch_col.delete(docs[0]) is None
        assert batch_col.insert(docs[1]) is None
        assert batch_col.delete(docs[1]) is None
        assert batch_col.insert(docs[2]) is None
        assert batch_col.get(docs[2]) is None
        assert batch_db.queued_jobs() is None

    # Ensure that the operations went through
    assert batch_db.queued_jobs() is None
    assert extract("_key", col.all()) == [docs[2]["_key"]]


def test_batch_execute_with_result(db, col, docs):
    with db.begin_batch_execution(return_result=True) as batch_db:
        batch_col = batch_db.collection(col.name)
        job1 = batch_col.insert(docs[0])
        job2 = batch_col.insert(docs[1])
        job3 = batch_col.insert(docs[1])  # duplicate
        jobs = batch_db.queued_jobs()
        assert jobs == [job1, job2, job3]
        assert all(job.status() == "pending" for job in jobs)

    assert batch_db.queued_jobs() == [job1, job2, job3]
    assert all(job.status() == "done" for job in batch_db.queued_jobs())
    assert extract("_key", col.all()) == extract("_key", docs[:2])

    # Test successful results
    assert job1.result()["_key"] == docs[0]["_key"]

    # Test insert error result
    # job2 and job3 are concurrent, either one can fail
    with pytest.raises(DocumentInsertError) as err:
        job2.result()
        job3.result()
    assert err.value.error_code == 1210


def test_batch_empty_commit(db):
    batch_db = db.begin_batch_execution(return_result=False)
    assert batch_db.commit() is None

    batch_db = db.begin_batch_execution(return_result=True)
    assert batch_db.commit() == []


def test_batch_double_commit(db, col, docs):
    batch_db = db.begin_batch_execution()
    job = batch_db.collection(col.name).insert(docs[0])

    # Test first commit
    assert batch_db.commit() == [job]
    assert job.status() == "done"
    assert len(col) == 1
    assert clean_doc(col.random()) == docs[0]

    # Test second commit which should fail
    with pytest.raises(BatchStateError) as err:
        batch_db.commit()
    assert "already committed" in str(err.value)
    assert len(col) == 1
    assert clean_doc(col.random()) == docs[0]


def test_batch_action_after_commit(db, col):
    with db.begin_batch_execution() as batch_db:
        batch_db.collection(col.name).insert({})

    # Test insert after the batch has been committed
    with pytest.raises(BatchStateError) as err:
        batch_db.collection(col.name).insert({})
    assert "already committed" in str(err.value)
    assert len(col) == 1


def test_batch_execute_error(bad_db, col, docs):
    batch_db = bad_db.begin_batch_execution(return_result=True)
    job = batch_db.collection(col.name).insert_many(docs)
    batch_db.commit()
    assert len(col) == 0
    assert job.status() == "done"


def test_batch_job_result_not_ready(db, col, docs):
    batch_db = db.begin_batch_execution(return_result=True)
    job = batch_db.collection(col.name).insert_many(docs)

    # Test get job result before commit
    with pytest.raises(BatchJobResultError) as err:
        job.result()
    assert str(err.value) == "result not available yet"

    # Test commit to make sure it still works after the errors
    assert batch_db.commit() == [job]
    assert len(job.result()) == len(docs)
    assert extract("_key", col.all()) == extract("_key", docs)
