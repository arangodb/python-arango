from __future__ import absolute_import, unicode_literals

import pytest

from threading import Thread, Event
import time

from arango import ArangoClient
from arango.aql import AQL
from arango.collections.standard import Collection
from arango.exceptions import (
    DocumentRevisionError,
    DocumentInsertError,
    BatchExecuteError,
    JobResultError
)
from arango.graph import Graph

from tests.utils import (
    generate_db_name,
    generate_col_name
)

arango_client = ArangoClient()
db_name = generate_db_name()
db = arango_client.create_database(db_name)
bad_db_name = generate_db_name()
bad_db = arango_client.db(bad_db_name)
col_name = generate_col_name()
col = db.create_collection(col_name)


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)


def setup_function(*_):
    col.truncate()


def test_init():
    batch = db.batch()
    assert batch.type == 'batch'
    assert 'ArangoDB batch execution {}'.format(batch.id) in repr(batch)
    assert isinstance(batch.aql, AQL)
    assert isinstance(batch.graph('test'), Graph)
    assert isinstance(batch.collection('test'), Collection)


def test_batch_job_properties():
    with db.batch(return_result=True) as batch:
        batch_col = batch.collection(col_name)
        job = batch_col.insert({'_key': '1', 'val': 1})

    assert 'ArangoDB batch job {}'.format(job.id) in repr(job)


def test_batch_empty_commit():
    batch = db.batch(return_result=True)
    assert batch.commit() is None


def test_batch_invalid_commit():
    assert len(col) == 0
    batch = bad_db.batch(return_result=True)
    batch_col = batch.collection(col_name)
    batch_col.insert({'_key': '1', 'val': 1})
    batch_col.insert({'_key': '2', 'val': 2})
    batch_col.insert({'_key': '2', 'val': 3})

    with pytest.raises(BatchExecuteError):
        batch.commit()
    assert len(col) == 0


def test_batch_insert_context_manager_with_result():
    assert len(col) == 0
    with db.batch(return_result=True) as batch:
        batch_col = batch.collection(col_name)
        job1 = batch_col.insert({'_key': '1', 'val': 1})
        job2 = batch_col.insert({'_key': '2', 'val': 2})
        job3 = batch_col.insert({'_key': '2', 'val': 3})
        job4 = batch_col.get(key='2', rev='9999')

    assert len(col) == 2
    assert col['1']['val'] == 1
    assert col['2']['val'] == 2

    assert job1.status() == 'done'
    assert job1.result()['_key'] == '1'

    assert job2.status() == 'done'
    assert job2.result()['_key'] == '2'

    assert job3.status() == 'error'
    assert isinstance(job3.result(), DocumentInsertError)

    assert job4.status() == 'error'
    assert isinstance(job4.result(), DocumentRevisionError)


def test_batch_insert_context_manager_without_result():
    assert len(col) == 0
    with db.batch(return_result=False) as batch:
        batch_col = batch.collection(col_name)
        job1 = batch_col.insert({'_key': '1', 'val': 1})
        job2 = batch_col.insert({'_key': '2', 'val': 2})
        job3 = batch_col.insert({'_key': '2', 'val': 3})
    assert len(col) == 2
    assert col['1']['val'] == 1
    assert col['2']['val'] == 2
    assert job1 is None
    assert job2 is None
    assert job3 is None


def test_batch_insert_context_manager_commit_on_error():
    assert len(col) == 0
    try:
        with db.batch(return_result=True, commit_on_error=True) as batch:
            batch_col = batch.collection(col_name)
            job1 = batch_col.insert({'_key': '1', 'val': 1})
            raise ValueError('Error!')
    except ValueError:
        assert col['1']['val'] == 1
        assert job1.status() == 'done'
        assert job1.result()['_key'] == '1'


def test_batch_insert_context_manager_no_commit_on_error():
    assert len(col) == 0
    try:
        with db.batch(return_result=True, commit_on_error=False) as batch:
            batch_col = batch.collection(col_name)
            job1 = batch_col.insert({'_key': '1', 'val': 1})
            raise ValueError('Error!')
    except ValueError:
        assert len(col) == 0
        assert job1.status() == 'pending'
        # TODO CHANGED Behavior: Result of jobs without a response fails on
        # error
        with pytest.raises(JobResultError):
            job1.result()


def test_batch_insert_no_context_manager_with_result():
    assert len(col) == 0
    batch = db.batch(return_result=True)
    batch_col = batch.collection(col_name)
    job1 = batch_col.insert({'_key': '1', 'val': 1})
    job2 = batch_col.insert({'_key': '2', 'val': 2})
    job3 = batch_col.insert({'_key': '2', 'val': 3})

    assert len(col) == 0
    assert job1.status() == 'pending'
    # TODO CHANGED Behavior: Result of jobs without a response fails on error
    with pytest.raises(JobResultError):
        job1.result()

    assert job2.status() == 'pending'
    with pytest.raises(JobResultError):
        job2.result()

    assert job3.status() == 'pending'
    with pytest.raises(JobResultError):
        job3.result()

    batch.commit()
    assert len(col) == 2
    assert col['1']['val'] == 1
    assert col['2']['val'] == 2

    assert job1.status() == 'done'
    assert job1.result()['_key'] == '1'

    assert job2.status() == 'done'
    assert job2.result()['_key'] == '2'

    assert job3.status() == 'error'
    assert isinstance(job3.result(), DocumentInsertError)


def test_batch_insert_no_context_manager_without_result():
    assert len(col) == 0
    batch = db.batch(return_result=False)
    batch_col = batch.collection(col_name)
    job1 = batch_col.insert({'_key': '1', 'val': 1})
    job2 = batch_col.insert({'_key': '2', 'val': 2})
    job3 = batch_col.insert({'_key': '2', 'val': 3})

    assert job1 is None
    assert job2 is None
    assert job3 is None

    batch.commit()
    assert len(col) == 2
    assert col['1']['val'] == 1
    assert col['2']['val'] == 2


def test_batch_query_context_manager_with_result():
    with db.batch(return_result=True, commit_on_error=False) as batch:
        job1 = batch.collection(col_name).import_bulk([
            {'_key': '1', 'val': 1},
            {'_key': '2', 'val': 2},
            {'_key': '3', 'val': 3},
        ])
        job2 = batch.aql.execute(
            'FOR d IN {} RETURN d'.format(col_name),
            count=True,
            batch_size=1,
            ttl=10,
            optimizer_rules=['+all']
        )
        job3 = batch.aql.execute(
            'FOR d IN {} FILTER d.val == @value RETURN d'.format(col_name),
            bind_vars={'value': 1},
            count=True
        )
    assert job1.result()['created'] == 3
    assert set(d['_key'] for d in job2.result()) == {'1', '2', '3'}
    assert set(d['_key'] for d in job3.result()) == {'1'}


def test_batch_clear():
    assert len(col) == 0
    batch = db.batch(return_result=True)
    batch_col = batch.collection(col_name)
    job1 = batch_col.insert({'_key': '1', 'val': 1})
    job2 = batch_col.insert({'_key': '2', 'val': 2})
    batch.clear()
    batch.commit()

    assert len(col) == 0
    assert job1.status() == 'pending'
    assert job2.status() == 'pending'


def thread_grab_lock(batch, signal_event, stop_event):
    with batch._lock:
        signal_event.set()

        while not stop_event.is_set():
            time.sleep(.1)


def test_batch_threaded_timeout():
    batch = db.batch(return_result=True, submit_timeout=1)

    thread_signal = Event()
    thread_stop = Event()

    thread = Thread(target=thread_grab_lock, args=(batch, thread_signal,
                                                   thread_stop))

    thread.start()

    while not thread_signal.is_set():
        time.sleep(.1)

    with pytest.raises(BatchExecuteError):
        batch.commit()

    thread_stop.set()

    thread.join()


def thread_submit_to_batch(batch, col):
    batch.collection(col).insert({'_key': '1', 'val': 1})


def test_batch_threaded_commit():
    batch = db.batch(return_result=True)

    t1 = Thread(target=thread_submit_to_batch, args=(batch, col_name))
    t2 = Thread(target=thread_submit_to_batch, args=(batch, col_name))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    res = batch.commit()

    assert len(res) == 2
    assert len([x for x in res if x.status() == 'error']) == 1
