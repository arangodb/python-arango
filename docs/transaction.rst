.. _transaction-page:

Transactions
------------

Python-arango provides partial support for **transactions**, where incoming
requests are queued in client-side memory and executed as a single, logical
unit of work (ACID compliant). Due to the limitations of ArangoDB's REST API,
:ref:`Transaction` currently supports only writes, unless raw Javascript is
executed (see example below).

.. note::
    The user should be mindful of the client-side memory while executing
    transactions with a large number of requests.

.. warning::
    :ref:`Transaction` is still experimental and prone to API changes.

Here is an example showing how transactions can be executed:

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.db('my_database')

    # Initialize the Transaction object via a context manager
    with db.transaction(write='students') as txn:

        # Transaction has a similar interface as that of Database, but
        # no results are returned on method calls (only queued in memory).
        txn.collection('students').insert({'_key': 'Abby'})
        txn.collection('students').insert({'_key': 'John'})
        txn.collection('students').insert({'_key': 'Mary'})

    # Upon exiting context, the queued requests are committed
    assert 'Abby' in db.collection('students')
    assert 'John' in db.collection('students')
    assert 'Mary' in db.collection('students')

    # Transaction can also be initialized without a context manager
    txn = db.transaction(write='students')
    job5 = txn.collection('students').insert({'_key': 'Jake'})
    job6 = txn.collection('students').insert({'_key': 'Jill'})
    txn.commit()  # In which case commit must be called explicitly

    assert 'Jake' in db.collection('students')
    assert 'Jill' in db.collection('students')

    # Raw javascript can also be executed (these are committed immediately)
    result = db.transaction(write='students').execute(
        command='''
        function () {{
            var db = require('internal').db;
            db.students.save(params.student1);
            db.students.save(params.student2);
            return true;
        }}
        ''',
        params={
            'student1': {'_key': 'Katy'},
            'student2': {'_key': 'Greg'}
        }
    )
    assert 'Katy' in db.collection('students')
    assert 'Greg' in db.collection('students')
    assert result is True

Refer to :ref:`Transaction` class for more details.
