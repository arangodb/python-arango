Batch Execution
---------------

Python-arango provides support for **batch execution**, where incoming requests
are queued in client-side memory and executed in a single HTTP call. After the
batch is committed/executed, the results of the requests can be retrieved via
:ref:`BatchJob` objects.

For more information on the HTTP REST API for batch requests visit this
`page <https://docs.arangodb.com/HTTP/BatchRequest>`_.


**Example:**

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.db('my_database')

    # Initialize a BatchExecution object via a context manager
    with db.batch(return_result=True) as batch:

        # BatchExecution has a similar interface as that of Database, but
        # BatchJob objects are returned instead of results on API calls
        job1 = batch.aql.execute('FOR d IN students RETURN d')
        job2 = batch.collection('students').insert({'_key': 'Abby'})
        job3 = batch.collection('students').insert({'_key': 'John'})
        job4 = batch.collection('students').insert({'_key': 'John'})

    # Upon exiting context, the queued requests are committed
    for job in [job1, job2, job3, job4]:
        print(job, job.status())

    # Retrieve the result of a job
    print(job1.result())

    # If a job fails the error is returned as opposed to being raised
    assert isinstance(job4.result(), Exception)

    # BatchExecution can also be initialized without a context manager
    batch = db.batch(return_result=True)
    students = batch.collection('students')
    job5 = batch.collection('students').insert({'_key': 'Jake'})
    job6 = batch.collection('students').insert({'_key': 'Jill'})
    batch.commit()  # The commit must be called manually


Refer to the :ref:`BatchExecution` and :ref:`BatchJob` classes for more
details.
