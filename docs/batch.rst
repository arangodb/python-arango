.. _batch-page:

Batch Execution
---------------

Python-arango provides support for **batch executions**, where incoming
requests are queued in client-side memory and executed in a single HTTP call.
After the batch is committed, the results of the queued requests can be
retrieved via :ref:`BatchJob` objects.

.. note::
    The user should be mindful of the client-side memory while using batch
    executions with a large number of requests.

.. warning::
    Batch execution is currently an experimental feature and is not
    thread-safe.

Here is an example showing how batch executions can be used:

.. code-block:: python

    from arango import ArangoClient, ArangoError

    client = ArangoClient()
    db = client.db('my_database')

    # Initialize the BatchExecution object via a context manager
    with db.batch(return_result=True) as batch:

        # BatchExecution has a similar interface as that of Database, but
        # BatchJob objects are returned instead of results on method calls
        job1 = batch.aql.execute('FOR d IN students RETURN d')
        job2 = batch.collection('students').insert({'_key': 'Abby'})
        job3 = batch.collection('students').insert({'_key': 'John'})
        job4 = batch.collection('students').insert({'_key': 'John'})

    # Upon exiting context, the queued requests are committed
    for job in [job1, job2, job3, job4]:
        print(job.status())

    # Retrieve the result of a job
    job1.result()

    # If a job fails, the exception object is returned (not raised)
    assert isinstance(job4.result(), ArangoError)

    # BatchExecution can also be initialized without a context manager
    batch = db.batch(return_result=True)
    students = batch.collection('students')
    job5 = batch.collection('students').insert({'_key': 'Jake'})
    job6 = batch.collection('students').insert({'_key': 'Jill'})
    batch.commit()  # In which case the commit must be called explicitly

Refer to :ref:`BatchExecution` and :ref:`BatchJob` classes for more details.
