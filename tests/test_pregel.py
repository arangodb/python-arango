from __future__ import absolute_import, unicode_literals

from six import string_types

from arango.exceptions import (
    PregelJobCreateError,
    PregelJobGetError,
    PregelJobDeleteError
)
from tests.helpers import (
    assert_raises,
    generate_string
)


def test_pregel_attributes(db, username):
    assert db.pregel.context in ['default', 'async', 'batch', 'transaction']
    assert db.pregel.username == username
    assert db.pregel.db_name == db.name
    assert repr(db.pregel) == '<Pregel in {}>'.format(db.name)


def test_pregel_management(db, graph):
    # Test create pregel job
    job_id = db.pregel.create_job(
        graph.name,
        'pagerank',
        store=False,
        max_gss=100,
        thread_count=1,
        async_mode=False,
        result_field='result',
        algorithm_params={'threshold': 0.000001}
    )
    assert isinstance(job_id, int)

    # Test create pregel job with unsupported algorithm
    with assert_raises(PregelJobCreateError) as err:
        db.pregel.create_job(graph.name, 'invalid')
    assert err.value.error_code in {4, 10}

    # Test get existing pregel job
    job = db.pregel.job(job_id)
    assert isinstance(job['state'], string_types)
    assert isinstance(job['aggregators'], dict)
    assert isinstance(job['gss'], int)
    assert isinstance(job['received_count'], int)
    assert isinstance(job['send_count'], int)
    assert isinstance(job['total_runtime'], float)

    # Test delete existing pregel job
    assert db.pregel.delete_job(job_id) is True
    with assert_raises(PregelJobGetError) as err:
        db.pregel.job(job_id)
    assert err.value.error_code in {4, 10}

    # Test delete missing pregel job
    with assert_raises(PregelJobDeleteError) as err:
        db.pregel.delete_job(generate_string())
    assert err.value.error_code in {4, 10}
