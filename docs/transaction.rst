Transactions
------------

In **transactions**, requests to ArangoDB server are committed as a single,
logical unit of work (ACID compliant).

.. warning::

    New transaction REST API was added to ArangoDB version 3.5. In order to use
    it python-arango's own transaction API had to be overhauled in version
    5.0.0. **The changes are not backward-compatible**: context managers are no
    longer offered (you must always commit the transaction youself), method
    signatures are different when beginning the transaction, and results are
    returned immediately instead of job objects.

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')
    col = db.collection('students')

    # Begin a transaction. Read and write collections must be declared ahead of
    # time. This returns an instance of TransactionDatabase, database-level
    # API wrapper tailored specifically for executing transactions.
    txn_db = db.begin_transaction(read=col.name, write=col.name)

    # The API wrapper is specific to a single transaction with a unique ID.
    txn_db.transaction_id

    # Child wrappers are also tailored only for the specific transaction.
    txn_aql = txn_db.aql
    txn_col = txn_db.collection('students')

    # API execution context is always set to "transaction".
    assert txn_db.context == 'transaction'
    assert txn_aql.context == 'transaction'
    assert txn_col.context == 'transaction'

    # From python-arango version 5+, results are returned immediately instead
    # of job objects on API execution.
    assert '_rev' in txn_col.insert({'_key': 'Abby'})
    assert '_rev' in txn_col.insert({'_key': 'John'})
    assert '_rev' in txn_col.insert({'_key': 'Mary'})

    # Check the transaction status.
    txn_db.transaction_status()

    # Commit the transaction.
    txn_db.commit_transaction()
    assert 'Abby' in col
    assert 'John' in col
    assert 'Mary' in col
    assert len(col) == 3

    # Begin another transaction. Note that the wrappers above are specific to
    # the last transaction and cannot be reused. New ones must be created.
    txn_db = db.begin_transaction(read=col.name, write=col.name)
    txn_col = txn_db.collection('students')
    assert '_rev' in txn_col.insert({'_key': 'Kate'})
    assert '_rev' in txn_col.insert({'_key': 'Mike'})
    assert '_rev' in txn_col.insert({'_key': 'Lily'})
    assert len(txn_col) == 6

    # Abort the transaction
    txn_db.abort_transaction()
    assert 'Kate' not in col
    assert 'Mike' not in col
    assert 'Lily' not in col
    assert len(col) == 3  # transaction is aborted so txn_col cannot be used

See :ref:`TransactionDatabase` for API specification.

Alternatively, you can use
:func:`arango.database.StandardDatabase.execute_transaction` to run raw
Javascript code in a transaction.

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
