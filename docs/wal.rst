.. _wal-page:

Write-Ahead Log
---------------

A **write-ahead log (WAL)** is a sequence of append-only files which contain
all write operations executed on ArangoDB server. It is typically used to
perform data recovery after a server crash or synchronize slave databases with
master databases in replicated environments. The WAL operations provided by
python-arango require root privileges (i.e. access to the ``_system`` database).
For more general information on ArangoDB's write-ahead logs visit this
`page <https://docs.arangodb.com/Manual/Architecture/WriteAheadLog.html>`_.


Example:

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()

    wal = client.wal

    # Configure the properties of the WAL
    wal.configure(oversized_ops=True)

    # Retrieve the properties of the WAL
    wal.properties()

    # List currently running WAL transactions
    wal.transactions()

    # Flush the WAL with garbage collection
    wal.flush(garbage_collect=True)


Note that the methods of :attr:`arango.client.ArangoClient.wal` above can only
be called by root user with access to ``_system`` database. Non-root users can
call the methods of :attr:`arango.database.Database.wal` using a database they
have access to instead. For example:

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.database(
        name='database-the-user-has-access-to',
        username='username',
        password='password'
    )

    # The WAL object now knows of the user and the database
    wal = db.wal

    # Configure the properties of the WAL
    wal.configure(oversized_ops=True)

    # Retrieve the properties of the WAL
    wal.properties()

    # List currently running WAL transactions
    wal.transactions()

    # Flush the WAL with garbage collection
    wal.flush(garbage_collect=True)


Refer to :class:`arango.wal.WriteAheadLog` for more details on the methods.
