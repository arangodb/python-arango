Cursors
-------

Many operations provided by python-arango (e.g. executing :doc:`aql` queries)
return result **cursors** to batch the network communication between ArangoDB
server and python-arango client. Each HTTP request from a cursor fetches the
next batch of results (usually documents). Depending on the query, the total
number of items in the result set may or may not be known in advance.

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Set up some test data to query against.
    db.collection('students').insert_many([
        {'_key': 'Abby', 'age': 22},
        {'_key': 'John', 'age': 18},
        {'_key': 'Mary', 'age': 21},
        {'_key': 'Suzy', 'age': 23},
        {'_key': 'Dave', 'age': 20}
    ])

    # Execute an AQL query which returns a cursor object.
    cursor = db.aql.execute(
        'FOR doc IN students FILTER doc.age > @val RETURN doc',
        bind_vars={'val': 17},
        batch_size=2,
        count=True
    )

    # Get the cursor ID.
    cursor.id

    # Get the items in the current batch.
    cursor.batch()

    # Check if the current batch is empty.
    cursor.empty()

    # Get the total count of the result set.
    cursor.count()

    # Flag indicating if there are more to be fetched from server.
    cursor.has_more()

    # Flag indicating if the results are cached.
    cursor.cached()

    # Get the cursor statistics.
    cursor.statistics()

    # Get the performance profile.
    cursor.profile()

    # Get any warnings produced from the query.
    cursor.warnings()

    # Return the next item from the cursor. If current batch is depleted, the
    # next batch if fetched from the server automatically.
    cursor.next()

    # Return the next item from the cursor. If current batch is depleted, an
    # exception is thrown. You need to fetch the next batch manually.
    cursor.pop()

    # Fetch the next batch and add them to the cursor object.
    cursor.fetch()

    # Delete the cursor from the server.
    cursor.close()

See :ref:`Cursor` for API specification.

If the fetched result batch is depleted while you are iterating over a cursor
(or while calling the method :func:`arango.cursor.Cursor.next`), python-arango
automatically sends an HTTP request to the server to fetch the next batch
(just-in-time style). To control exactly when the fetches occur, you can use
methods :func:`arango.cursor.Cursor.fetch` and :func:`arango.cursor.Cursor.pop`
instead.

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Set up some test data to query against.
    db.collection('students').insert_many([
        {'_key': 'Abby', 'age': 22},
        {'_key': 'John', 'age': 18},
        {'_key': 'Mary', 'age': 21}
    ])

    # If you iterate over the cursor or call cursor.next(), batches are
    # fetched automatically from the server just-in-time style.
    cursor = db.aql.execute('FOR doc IN students RETURN doc', batch_size=1)
    result = [doc for doc in cursor]

    # Alternatively, you can manually fetch and pop for finer control.
    cursor = db.aql.execute('FOR doc IN students RETURN doc', batch_size=1)
    while cursor.has_more(): # Fetch until nothing is left on the server.
        cursor.fetch()
    while not cursor.empty(): # Pop until nothing is left on the cursor.
        cursor.pop()

With ArangoDB 3.11.0 or higher, you can also use the `allow_retry`
parameter of :func:`arango.aql.AQL.execute` to automatically retry
the request if the cursor encountered any issues during the previous
fetch operation. Note that this feature causes the server to cache the
last batch. To allow re-fetching of the very last batch of the query,
the server cannot automatically delete the cursor. Once you have successfully
received the last batch, you should call :func:`arango.cursor.Cursor.close`.

**Example:**

.. code-block:: python

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Set up some test data to query against.
    db.collection('students').insert_many([
        {'_key': 'Abby', 'age': 22},
        {'_key': 'John', 'age': 18},
        {'_key': 'Mary', 'age': 21},
        {'_key': 'Suzy', 'age': 23},
        {'_key': 'Dave', 'age': 20}
    ])

    # Execute an AQL query which returns a cursor object.
    cursor = db.aql.execute(
        'FOR doc IN students FILTER doc.age > @val RETURN doc',
        bind_vars={'val': 17},
        batch_size=2,
        count=True,
        allow_retry=True
    )

    while cursor.has_more():
        try:
            cursor.fetch()
        except ConnectionError:
            # Retry the request.
            continue

    while not cursor.empty():
        cursor.pop()

    # Delete the cursor from the server.
    cursor.close()
