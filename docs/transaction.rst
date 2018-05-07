Transactions
------------

Python-arango supports **transactions**, where requests to ArangoDB server are
placed in client-side in-memory queue, and committed as a single, logical unit
of work (ACID compliant). After a successful commit, results can be retrieved
from :ref:`TransactionJob` objects.

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Get the API wrapper for "students" collection.
    students = db.collection('students')

    # Begin a transaction via context manager. This returns an instance of
    # TransactionDatabase, a database-level API wrapper tailored specifically
    # for executing transactions. The transaction is automatically committed
    # when exiting the context. The TransactionDatabase wrapper cannot be
    # reused after commit and may be discarded after.
    with db.begin_transaction() as txn_db:

        # Child wrappers are also tailored for transactions.
        txn_col = txn_db.collection('students')

        # API execution context is always set to "transaction".
        assert txn_db.context == 'transaction'
        assert txn_col.context == 'transaction'

        # TransactionJob objects are returned instead of results.
        job1 = txn_col.insert({'_key': 'Abby'})
        job2 = txn_col.insert({'_key': 'John'})
        job3 = txn_col.insert({'_key': 'Mary'})

    # Upon exiting context, transaction is automatically committed.
    assert 'Abby' in students
    assert 'John' in students
    assert 'Mary' in students

    # Retrieve the status of each transaction job.
    for job in txn_db.queued_jobs():
        # Status is set to either "pending" (transaction is not committed yet
        # and result is not available) or "done" (transaction is committed and
        # result is available).
        assert job.status() in {'pending', 'done'}

    # Retrieve the job results.
    metadata = job1.result()
    assert metadata['_id'] == 'students/Abby'

    metadata = job2.result()
    assert metadata['_id'] == 'students/John'

    metadata = job3.result()
    assert metadata['_id'] == 'students/Mary'

    # Transactions can be initiated without using a context manager.
    # If return_result parameter is set to False, no jobs are returned.
    txn_db = db.begin_transaction(return_result=False)
    txn_db.collection('students').insert({'_key': 'Jake'})
    txn_db.collection('students').insert({'_key': 'Jill'})

    # The commit must be called explicitly.
    txn_db.commit()
    assert 'Jake' in students
    assert 'Jill' in students

.. note::
    * Be mindful of client-side memory capacity when issuing a large number of
      requests in a single transaction.
    * :ref:`TransactionDatabase` and :ref:`TransactionJob` instances are
      stateful objects, and should not be shared across multiple threads.
    * :ref:`TransactionDatabase` instance cannot be reused after commit.

See :ref:`TransactionDatabase` and :ref:`TransactionJob` for API specification.

Error Handling
==============

Unlike :doc:`batch <batch>` or :doc:`async <async>` execution, job-specific
error handling is not possible for transactions. As soon as a job fails, the
entire transaction is halted, all previous successful jobs are rolled back,
and :class:`arango.exceptions.TransactionExecuteError` is raised. The exception
describes the first failed job, and all :ref:`TransactionJob` objects are left
at "pending" status (they may be discarded).

**Example:**

.. testcode::

    from arango import ArangoClient, TransactionExecuteError

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Get the API wrapper for "students" collection.
    students = db.collection('students')

    # Begin a new transaction.
    txn_db = db.begin_transaction()
    txn_col = txn_db.collection('students')

    job1 = txn_col.insert({'_key': 'Karl'})  # Is going to be rolled back.
    job2 = txn_col.insert({'_key': 'Karl'})  # Fails due to duplicate key.
    job3 = txn_col.insert({'_key': 'Josh'})  # Never executed on the server.

    try:
        txn_db.commit()
    except TransactionExecuteError as err:
        assert err.http_code == 409
        assert err.error_code == 1210
        assert err.message.endswith('conflicting key: Karl')

    # All operations in the transaction are rolled back.
    assert 'Karl' not in students
    assert 'Josh' not in students

    # All transaction jobs are left at "pending "status and may be discarded.
    for job in txn_db.queued_jobs():
        assert job.status() == 'pending'

Restrictions
============

This section covers important restrictions that you must keep in mind before
choosing to use transactions.

:ref:`TransactionJob` results are available only *after* commit, and are not
accessible during execution. If you need to implement a logic which depends on
intermediate, in-transaction values, you can instead call the method
:func:`arango.database.Database.execute_transaction` which takes raw Javascript
command as its argument.

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Get the API wrapper for "students" collection.
    students = db.collection('students')

    # Execute transaction in raw Javascript.
    result = db.execute_transaction(
        command='''
        function () {{
            var db = require('internal').db;
            db.students.save(params.student1);
            if (db.students.count() > 1) {
                db.students.save(params.student2);
            } else {
                db.students.save(params.student3);
            }
            return true;
        }}
        ''',
        params={
            'student1': {'_key': 'Lucy'},
            'student2': {'_key': 'Greg'},
            'student3': {'_key': 'Dona'}
        },
        read='students',  # Specify the collections read.
        write='students'  # Specify the collections written.
    )
    assert result is True
    assert 'Lucy' in students
    assert 'Greg' in students
    assert 'Dona' not in students

Note that in above example, :func:`arango.database.Database.execute_transaction`
requires names of *read* and *write* collections as python-arango has no way of
reliably figuring out which collections are used. This is also the case when
executing AQL queries.

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Begin a new transaction via context manager.
    with db.begin_transaction() as txn_db:
        job = txn_db.aql.execute(
            'INSERT {_key: "Judy", age: @age} IN students RETURN true',
            bind_vars={'age': 19},
            # You must specify the "read" and "write" collections.
            read_collections=[],
            write_collections=['students']
        )
    cursor = job.result()
    assert cursor.next() is True
    assert db.collection('students').get('Judy')['age'] == 19

Due to limitations of ArangoDB's REST API, only the following methods are
supported in transactions:

* :func:`arango.aql.AQL.execute`
* :func:`arango.collection.StandardCollection.get`
* :func:`arango.collection.StandardCollection.get_many`
* :func:`arango.collection.StandardCollection.insert`
* :func:`arango.collection.StandardCollection.insert_many`
* :func:`arango.collection.StandardCollection.update`
* :func:`arango.collection.StandardCollection.update_many`
* :func:`arango.collection.StandardCollection.update_match`
* :func:`arango.collection.StandardCollection.replace`
* :func:`arango.collection.StandardCollection.replace_many`
* :func:`arango.collection.StandardCollection.replace_match`
* :func:`arango.collection.StandardCollection.delete`
* :func:`arango.collection.StandardCollection.delete_many`
* :func:`arango.collection.StandardCollection.delete_match`
* :func:`arango.collection.StandardCollection.properties`
* :func:`arango.collection.StandardCollection.statistics`
* :func:`arango.collection.StandardCollection.revision`
* :func:`arango.collection.StandardCollection.checksum`
* :func:`arango.collection.StandardCollection.rotate`
* :func:`arango.collection.StandardCollection.truncate`
* :func:`arango.collection.StandardCollection.count`
* :func:`arango.collection.StandardCollection.has`
* :func:`arango.collection.StandardCollection.ids`
* :func:`arango.collection.StandardCollection.keys`
* :func:`arango.collection.StandardCollection.all`
* :func:`arango.collection.StandardCollection.find`
* :func:`arango.collection.StandardCollection.find_near`
* :func:`arango.collection.StandardCollection.find_in_range`
* :func:`arango.collection.StandardCollection.find_in_radius`
* :func:`arango.collection.StandardCollection.find_in_box`
* :func:`arango.collection.StandardCollection.find_by_text`
* :func:`arango.collection.StandardCollection.get_many`
* :func:`arango.collection.StandardCollection.random`
* :func:`arango.collection.StandardCollection.indexes`
* :func:`arango.collection.VertexCollection.get`
* :func:`arango.collection.VertexCollection.insert`
* :func:`arango.collection.VertexCollection.update`
* :func:`arango.collection.VertexCollection.replace`
* :func:`arango.collection.VertexCollection.delete`
* :func:`arango.collection.EdgeCollection.get`
* :func:`arango.collection.EdgeCollection.insert`
* :func:`arango.collection.EdgeCollection.update`
* :func:`arango.collection.EdgeCollection.replace`
* :func:`arango.collection.EdgeCollection.delete`

If an unsupported method is called, :class:`arango.exceptions.TransactionStateError`
is raised.

**Example:**

.. testcode::

    from arango import ArangoClient, TransactionStateError

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Begin a new transaction.
    txn_db = db.begin_transaction()

    # API method "databases()" is not supported and an exception is raised.
    try:
        txn_db.databases()
    except TransactionStateError as err:
        assert err.source == 'client'
        assert err.message == 'action not allowed in transaction'

When running queries in transactions, the :doc:`cursors <cursor>` are loaded
with the entire result set right away. This is regardless of the parameters
passed in when executing the query (e.g batch_size). You must be mindful of
client-side memory capacity when executing queries that can potentially return
a large result set.

**Example:**

.. testcode::

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Get the total document count in "students" collection.
    document_count = db.collection('students').count()

    # Execute an AQL query normally (without using transactions).
    cursor1 = db.aql.execute('FOR doc IN students RETURN doc', batch_size=1)

    # Execute the same AQL query in a transaction.
    with db.begin_transaction() as txn_db:
        job = txn_db.aql.execute('FOR doc IN students RETURN doc', batch_size=1)
    cursor2 = job.result()

    # The first cursor acts as expected. Its current batch contains only 1 item
    # and it still needs to fetch the rest of its result set from the server.
    assert len(cursor1.batch()) == 1
    assert cursor1.has_more() is True

    # The second cursor is pre-loaded with the entire result set, and does not
    # require further communication with ArangoDB server. Note that value of
    # parameter "batch_size" was ignored.
    assert len(cursor2.batch()) == document_count
    assert cursor2.has_more() is False
