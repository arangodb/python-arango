from __future__ import absolute_import, unicode_literals

import pytest

from arango import ArangoClient
from arango.exceptions import (
    PregelJobCreateError,
    PregelJobGetError,
    PregelJobDeleteError
)

from tests.utils import (
    generate_db_name,
    generate_col_name,
    generate_graph_name,
)

arango_client = ArangoClient()
db_name = generate_db_name()
db = arango_client.create_database(db_name)
graph_name = generate_graph_name()
graph = db.create_graph(graph_name)
from_col_name = generate_col_name()
to_col_name = generate_col_name()
edge_col_name = generate_col_name()
graph.create_vertex_collection(from_col_name)
graph.create_vertex_collection(to_col_name)
graph.create_edge_definition(
    edge_col_name, [from_col_name], [to_col_name]
)


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)


@pytest.mark.order1
def test_start_pregel_job():
    # Test start_pregel_job with page rank algorithm (happy path)
    job_id = db.create_pregel_job('pagerank', graph_name)
    assert isinstance(job_id, int)

    # Test start_pregel_job with unsupported algorithm
    with pytest.raises(PregelJobCreateError):
        db.create_pregel_job('unsupported_algorithm', graph_name)


@pytest.mark.order2
def test_get_pregel_job():
    # Create a test Pregel job
    job_id = db.create_pregel_job(
        "pagerank",
        graph_name,
        store=False,
        max_gss=100,
        thread_count=1,
        async_mode=False,
        result_field="result",
        algorithm_params={"threshold": 0.0000001}
    )
    # Test pregel_job with existing job ID (happy path)
    job = db.pregel_job(job_id)
    assert isinstance(job['aggregators'], dict)
    assert isinstance(job['gss'], int)
    assert isinstance(job['received_count'], int)
    assert isinstance(job['send_count'], int)
    assert isinstance(job['total_runtime'], float)
    # TODO CHANGED to prevent race condition
    assert job['state'] in {'running', 'done'}

    # Test pregel_job with an invalid job ID
    with pytest.raises(PregelJobGetError):
        db.pregel_job(-1)


@pytest.mark.order3
def test_delete_pregel_job():
    # Create a test Pregel job
    job_id = db.create_pregel_job(
        "pagerank",
        graph_name,
        store=False,
        max_gss=999,
        thread_count=1,
        async_mode=False,
        result_field="result",
        algorithm_params={"threshold": 0.0000001}
    )

    # Get the newly created job
    job = db.pregel_job(job_id)
    assert job['state'] in {'running', 'done'}

    # Test delete_pregel_job with existing job ID (happy path)
    assert db.delete_pregel_job(job_id)

    # The fetch for the same job should now fail
    with pytest.raises(PregelJobGetError):
        db.pregel_job(job_id)

    # Test delete_pregel_job with an invalid job ID
    with pytest.raises(PregelJobDeleteError):
        db.delete_pregel_job(-1)
