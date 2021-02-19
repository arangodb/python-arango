Async API Execution
-------------------

In **asynchronous API executions**, python-arango sends API requests to ArangoDB in
fire-and-forget style. The server processes the requests in the background, and
the results can be retrieved once available via :ref:`AsyncJob` objects.

**Example:**

.. testcode::

    import time

    from arango import (
        ArangoClient,
        AQLQueryExecuteError,
        AsyncJobCancelError,
        AsyncJobClearError
    )

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Begin async execution. This returns an instance of AsyncDatabase, a
    # database-level API wrapper tailored specifically for async execution.
    async_db = db.begin_async_execution(return_result=True)

    # Child wrappers are also tailored for async execution.
    async_aql = async_db.aql
    async_col = async_db.collection('students')

    # API execution context is always set to "async".
    assert async_db.context == 'async'
    assert async_aql.context == 'async'
    assert async_col.context == 'async'

    # On API execution, AsyncJob objects are returned instead of results.
    job1 = async_col.insert({'_key': 'Neal'})
    job2 = async_col.insert({'_key': 'Lily'})
    job3 = async_aql.execute('RETURN 100000')
    job4 = async_aql.execute('INVALID QUERY')  # Fails due to syntax error.

    # Retrieve the status of each async job.
    for job in [job1, job2, job3, job4]:
        # Job status can be "pending", "done" or "cancelled".
        assert job.status() in {'pending', 'done', 'cancelled'}

        # Let's wait until the jobs are finished.
        while job.status() != 'done':
            time.sleep(0.1)

    # Retrieve the results of successful jobs.
    metadata = job1.result()
    assert metadata['_id'] == 'students/Neal'

    metadata = job2.result()
    assert metadata['_id'] == 'students/Lily'

    cursor = job3.result()
    assert cursor.next() == 100000

    # If a job fails, the exception is propagated up during result retrieval.
    try:
        result = job4.result()
    except AQLQueryExecuteError as err:
        assert err.http_code == 400
        assert err.error_code == 1501
        assert 'syntax error' in err.message

    # Cancel a job. Only pending jobs still in queue may be cancelled.
    # Since job3 is done, there is nothing to cancel and an exception is raised.
    try:
        job3.cancel()
    except AsyncJobCancelError as err:
        assert err.message.endswith(f'job {job3.id} not found')

    # Clear the result of a job from ArangoDB server to free up resources.
    # Result of job4 was removed from the server automatically upon retrieval,
    # so attempt to clear it raises an exception.
    try:
        job4.clear()
    except AsyncJobClearError as err:
        assert err.message.endswith(f'job {job4.id} not found')

    # List the IDs of the first 100 async jobs completed.
    db.async_jobs(status='done', count=100)

    # List the IDs of the first 100 async jobs still pending.
    db.async_jobs(status='pending', count=100)

    # Clear all async jobs still sitting on the server.
    db.clear_async_jobs()

.. note::
    Be mindful of server-side memory capacity when issuing a large number of
    async requests in small time interval.

See :ref:`AsyncDatabase` and :ref:`AsyncJob` for API specification.
