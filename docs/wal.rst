Write-Ahead Log
---------------

A **write-ahead log (WAL)** is a sequence of append-only files containing all
write operations executed on ArangoDB. It can be used to run data recovery
after a server crash, or synchronize slave databases with master databases in
setups with replications.

For more information on the HTTP REST API for write-ahead logs visit this
`page <https://docs.arangodb.com/HTTP/MiscellaneousFunctions>`__ and for more
general information visit this
`page <https://docs.arangodb.com/Manual/Architecture/WriteAheadLog.html>`_.

.. note::
    Some operations in the example below require root privileges (i.e. the
    user must have access to the ``_system`` database).

**Example:**

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()

    # Retrieve the WriteAheadLog object
    client.wal

    # Configure the properties of the WAL
    client.wal.configure(oversized_ops=10000)

    # Retrieve the properties of the WAL
    client.wal.properties()

    # List currently running WAL transactions
    client.wal.transactions()

    # Flush the WAL with garbage collection
    client.wal.flush(garbage_collect=True)

Refer to the :ref:`WriteAheadLog` class for more details.
