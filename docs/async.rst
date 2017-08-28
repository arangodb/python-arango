.. _async-page:

Async Execution
---------------

Python-arango provides support for **asynchronous executions**, where incoming
requests are placed in a server-side, in-memory task queue and executed in a
fire-and-forget style. The results of the requests can be retrieved later via
:ref:`AsyncJob` objects.

.. note::
    The user should be mindful of the server-side memory while using
    asynchronous executions with a large number of requests.

.. warning::
    Asynchronous execution is currently an experimental feature and is not
    thread-safe.

Here is an example showing how asynchronous executions can be used:

.. code-block:: python

    from arango import ArangoClient, ArangoError

    client = ArangoClient()
    db = client.db('my_database')

    # Initialize an AsyncExecution object to make asynchronous requests
    asynchronous = db.asynchronous(return_result=True)

    # AsyncExecution has a similar interface as that of Database, but
    # AsyncJob objects are returned instead of results on method calls
    job1 = asynchronous.collection('students').insert({'_key': 'Abby'})
    job2 = asynchronous.collection('students').insert({'_key': 'John'})
    job3 = asynchronous.collection('students').insert({'_key': 'John'})
    job4 = asynchronous.aql.execute('FOR d IN students RETURN d')

    # Check the statuses of the asynchronous jobs
    for job in [job1, job2, job3, job4]:
        print(job.status())

    # Retrieve the result of a job
    result = job1.result()

    # If a job fails, the exception object is returned (not raised)
    result = job3.result()
    assert isinstance(result, ArangoError)

    # Cancel a pending job
    job3.cancel()

    # Delete a result of a job from the server to free up resources
    job4.clear()

    # List the first 100 jobs completed (root user only)
    client.async_jobs(status='done', count=100)

    # List the first 100 jobs still pending in the queue (root user only)
    client.async_jobs(status='pending', count=100)

    # Non-root users can only list jobs in a database they have access to
    client.db('database-the-user-has-access-to').async_jobs()

    # Clear all jobs from the server (root user only)
    client.clear_async_jobs()

    # Non-root users can only clear jobs in a databases they have access to
    client.db('database-the-user-has-access-to').clear_async_jobs()


Refer to :ref:`ArangoClient`, :ref:`AsyncExecution` and :ref:`AsyncJob`
classes for more details.
