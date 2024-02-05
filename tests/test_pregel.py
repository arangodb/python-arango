import time

import pytest
from packaging import version

from arango.exceptions import (
    PregelJobCreateError,
    PregelJobDeleteError,
    PregelJobGetError,
)
from tests.helpers import assert_raises, generate_string


def test_pregel_attributes(db, db_version, username):
    if db_version >= version.parse("3.12.0"):
        pytest.skip("Pregel is not tested in 3.12.0+")

    assert db.pregel.context in ["default", "async", "batch", "transaction"]
    assert db.pregel.username == username
    assert db.pregel.db_name == db.name
    assert repr(db.pregel) == f"<Pregel in {db.name}>"


def test_pregel_management(db, db_version, graph, cluster):
    if db_version >= version.parse("3.12.0"):
        pytest.skip("Pregel is not tested in 3.12.0+")

    if cluster:
        pytest.skip("Not tested in a cluster setup")

    # Test create pregel job
    job_id = db.pregel.create_job(
        graph.name,
        "pagerank",
        store=False,
        max_gss=100,
        thread_count=1,
        async_mode=False,
        result_field="result",
        algorithm_params={"threshold": 0.000001},
    )
    assert isinstance(job_id, int)

    # Test create pregel job with unsupported algorithm
    with assert_raises(PregelJobCreateError) as err:
        db.pregel.create_job(graph.name, "invalid")
    assert err.value.error_code in {4, 10, 1600}

    # Test get existing pregel job
    job = db.pregel.job(job_id)
    assert isinstance(job["state"], str)
    assert isinstance(job["aggregators"], dict)
    assert isinstance(job["gss"], int)
    assert isinstance(job["received_count"], int)
    assert isinstance(job["send_count"], int)
    assert "total_runtime" in job

    # Test delete existing pregel job
    assert db.pregel.delete_job(job_id) is True
    time.sleep(0.2)
    if db_version < version.parse("3.11.0"):
        with assert_raises(PregelJobGetError) as err:
            db.pregel.job(job_id)
        assert err.value.error_code in {4, 10, 1600}
    else:
        job = db.pregel.job(job_id)
        assert job["state"] == "canceled"

    # Test delete missing pregel job
    with assert_raises(PregelJobDeleteError) as err:
        db.pregel.delete_job(generate_string())
    assert err.value.error_code in {4, 10, 1600}
