.. _cursor-page:

Cursors
-------

Many operations defined in python-arango (including :ref:`aql-page` queries)
return :ref:`Cursor` objects to batch the network communication between the
server and the client. Each request from the cursor fetches the next set of
documents, where the total number of documents in the result set may or may not
be known in advance depending on the query. For more information on the HTTP
REST API for using cursors visit this
`page <https://docs.arangodb.com/HTTP/AqlQueryCursor/AccessingCursors.html>`__.

.. note::
    In order to free the server resources, python-arango deletes a cursor as
    soon as its document result set is depleted.

**Example:**

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