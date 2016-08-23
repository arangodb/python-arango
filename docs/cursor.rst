.. _cursor-page:

Cursors
-------

Several operations provided by python-arango (e.g. :ref:`aql-page` queries)
return query :ref:`Cursor` objects to batch the network communication between
the server and the client. Each request from the cursor fetches the next set
of documents. Depending on the query, the total number of documents in a result
set may or may not be known in advance.

.. note::
    In order to free the server resources as much as possible, python-arango
    deletes cursors as soon as their result sets are depleted.

Here is an example showing how a query cursor can be used:

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.db('my_database')

    # Set up some test data to query
    db.collection('students').insert_many([
        {'_key': 'Abby', 'age': 22},
        {'_key': 'John', 'age': 18},
        {'_key': 'Mary', 'age': 21}
    ])

    # Execute an AQL query which returns a cursor object
    cursor = db.aql.execute(
        'FOR s IN students FILTER s.age < @val RETURN s',
        bind_vars={'val': 19},
        batch_size=1,
        count=True
    )

    # Retrieve the cursor ID
    cursor.id

    # Retrieve the documents in the current batch
    cursor.batch()

    # Check if there are more documents to be fetched
    cursor.has_more()

    # Retrieve the cursor statistics
    cursor.statistics()

    # Retrieve any warnings produced from the cursor
    cursor.warnings()

    # Return the next document in the batch
    # If the batch is depleted, fetch the next batch
    cursor.next()

    # Delete the cursor from the server
    cursor.close()

Refer to :ref:`Cursor` class for more details.