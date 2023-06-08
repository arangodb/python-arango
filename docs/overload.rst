Overload API Execution
----------------------
:ref:`OverloadControlDatabase` is designed to handle time-bound requests. It allows setting a maximum server-side
queuing time for client requests via the *max_queue_time_seconds* parameter. If the server's queueing time for a
request surpasses this defined limit, the request will be rejected. This mechanism provides you with more control over
request handling, enabling your application to react effectively to potential server overloads.

Additionally, the response from ArangoDB will always include the most recent request queuing/dequeuing time from the
server's perspective. This can be accessed via the :attr:`~.OverloadControlDatabase.last_queue_time` property.

**Example:**

.. testcode::

    from arango import errno
    from arango import ArangoClient
    from arango.exceptions import OverloadControlExecutorError

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Begin controlled execution.
    controlled_db = db.begin_controlled_execution(max_queue_time_seconds=7.5)

    # All requests surpassing the specified limit will be rejected.
    controlled_aql = controlled_db.aql
    controlled_col = controlled_db.collection('students')

    # On API execution, the last_queue_time property gets updated.
    controlled_col.insert({'_key': 'Neal'})

    # Retrieve the last recorded queue time.
    assert controlled_db.last_queue_time >= 0

    try:
        controlled_aql.execute('RETURN 100000')
    except OverloadControlExecutorError as err:
        assert err.http_code == errno.HTTP_PRECONDITION_FAILED
        assert err.error_code == errno.QUEUE_TIME_REQUIREMENT_VIOLATED

    # Retrieve the maximum allowed queue time.
    assert controlled_db.max_queue_time == 7.5

    # Adjust the maximum allowed queue time.
    controlled_db.adjust_max_queue_time(0.0001)

    # Disable the maximum allowed queue time.
    controlled_db.adjust_max_queue_time(None)

.. note::
    Setting *max_queue_time_seconds* to 0 or a non-numeric value will cause ArangoDB to ignore the header.

See :ref:`OverloadControlDatabase` for API specification.
See the `official documentation <https://www.arangodb.com/docs/stable/http/general.html#overload-control>`_ for
details on ArangoDB's overload control options.
