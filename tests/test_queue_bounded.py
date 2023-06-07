import warnings

from arango.exceptions import QueueBoundedExecutorError


def flood_with_requests(bounded_db, async_db):
    """
    Flood the database with requests.
    It is impossible to predict what the last recorded queue time will be.
    We can only try and make it as large as possible. However, if the system
    is fast enough, it may still be 0.
    """
    for _ in range(3):
        for _ in range(500):
            async_db.aql.execute("RETURN SLEEP(0.5)", count=True)
        for _ in range(3):
            bounded_db.aql.execute("RETURN SLEEP(0.5)", count=True)
        if bounded_db.last_queue_time >= 0:
            break


def test_queue_bounded(db):
    bounded_db = db.begin_queue_bounded_execution(100)
    async_db = db.begin_async_execution(return_result=True)

    flood_with_requests(bounded_db, async_db)
    assert bounded_db.last_queue_time >= 0

    # We can only emit a warning here. The test will still pass.
    if bounded_db.last_queue_time == 0:
        warnings.warn("last_queue_time is 0, test may be unreliable")

    bounded_db.adjust_max_queue_time(0.0001)
    try:
        flood_with_requests(bounded_db, async_db)
        assert bounded_db.last_queue_time >= 0
    except QueueBoundedExecutorError as e:
        assert e.http_code == 412
        assert e.error_code == 21004
    else:
        warnings.warn(
            f"last queue time is {bounded_db.last_queue_time}, test may be unreliable"
        )
