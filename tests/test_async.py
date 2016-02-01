from __future__ import absolute_import, unicode_literals

import pytest

from arango import ArangoClient
from arango.exceptions import (
    AQLQueryExecuteError
)

from .utils import (
    generate_db_name,
    generate_col_name,
    generate_graph_name
)

arango_client = ArangoClient()
db_name = generate_db_name(arango_client)
db = arango_client.create_database(db_name)
col_name = generate_col_name(db)
col = db.create_collection(col_name)
graph_name = generate_graph_name(db)
graph = db.create_graph(graph_name)
vcol_name = generate_col_name(db)
graph.create_vertex_collection(vcol_name)


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)


def setup_function(*_):
    col.truncate()


def wait_on_job(job):
    while True:
        if job.status() == 'done':
            break
    return job.result()


@pytest.mark.order1
def test_async_inserts():
    assert len(col) == 0
    async = db.async(return_result=True)
    job1 = async.collection(col_name).insert({'_key': '1', 'val': 1})
    job2 = async.collection(col_name).insert({'_key': '2', 'val': 2})
    job3 = async.collection(col_name).insert({'_key': '3', 'val': 3})

    assert len(col) == 3
    assert job1.result()['_key'] == '1'
    assert job2.result()['_key'] == '2'
    assert job3.result()['_key'] == '3'


@pytest.mark.order1
def test_async_query():
    async = db.async(return_result=True)
    wait_on_job(async.collection(col_name).import_bulk([
        {'_key': '1', 'val': 1},
        {'_key': '2', 'val': 2},
        {'_key': '3', 'val': 3},
    ]))
    result = wait_on_job(async.aql.execute('THIS IS AN INVALID QUERY'))
    assert isinstance(result, AQLQueryExecuteError)

    result = wait_on_job(async.aql.execute(
        'FOR d IN {} RETURN d'.format(col_name),
        count=True,
        batch_size=1,
        ttl=10,
        optimizer_rules=['+all']
    ))
    assert set(d['_key'] for d in result) == {'1', '2', '3'}

    result = wait_on_job(async.aql.execute(
        'FOR d IN {} FILTER d.val == @value RETURN d'.format(col_name),
        bind_vars={'value': 1},
        count=True
    ))
    assert set(d['_key'] for d in result) == {'1'}
