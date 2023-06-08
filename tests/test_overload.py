import warnings

from arango import errno
from arango.exceptions import OverloadControlExecutorError


def flood_with_requests(controlled_db, async_db):
    """
    Flood the database with requests.
    It is impossible to predict what the last recorded queue time will be.
    We can only try and make it as large as possible. However, if the system
    is fast enough, it may still be 0.
    """
    controlled_db.aql.execute("RETURN SLEEP(0.5)", count=True)
    for _ in range(3):
        for _ in range(500):
            async_db.aql.execute("RETURN SLEEP(0.5)", count=True)
        controlled_db.aql.execute("RETURN SLEEP(0.5)", count=True)
        if controlled_db.last_queue_time >= 0:
            break


def test_overload_control(db):
    controlled_db = db.begin_controlled_execution(100)
    assert controlled_db.max_queue_time == 100

    async_db = db.begin_async_execution(return_result=True)

    flood_with_requests(controlled_db, async_db)
    assert controlled_db.last_queue_time >= 0

    # We can only emit a warning here. The test will still pass.
    if controlled_db.last_queue_time == 0:
        warnings.warn(
            f"last_queue_time of {controlled_db} is 0, test may be unreliable"
        )

    controlled_db.adjust_max_queue_time(0.0001)
    try:
        flood_with_requests(controlled_db, async_db)
        assert controlled_db.last_queue_time >= 0
    except OverloadControlExecutorError as e:
        assert e.http_code == errno.HTTP_PRECONDITION_FAILED
        assert e.error_code == errno.QUEUE_TIME_REQUIREMENT_VIOLATED
    else:
        warnings.warn(
            f"last_queue_time of {controlled_db} is {controlled_db.last_queue_time},"
            f"test may be unreliable"
        )
