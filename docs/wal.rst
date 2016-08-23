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

    # Configure the properties of the WAL
    client.wal.configure(oversized_ops=10000)

    # Retrieve the properties of the WAL
    client.wal.properties()

    # List currently running WAL transactions
    client.wal.transactions()

    # Flush the WAL with garbage collection
    client.wal.flush(garbage_collect=True)

Refer to :ref:`WriteAheadLog` class for more details.
