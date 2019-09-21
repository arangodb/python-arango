Write-Ahead Log (WAL)
---------------------

**Write-Ahead Log (WAL)** is a set of append-only files recording all writes
on ArangoDB server. It is typically used to perform data recovery after a crash
or synchronize slave databases with master databases in replicated environments.
WAL operations can only be performed by admin users via ``_system`` database.

**Example:**

.. code-block:: python

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "_system" database as root user.
    sys_db = client.db('_system', username='root', password='passwd')

    # Get the WAL API wrapper.
    wal = sys_db.wal

    # Configure WAL properties.
    wal.configure(
        historic_logs=15,
        oversized_ops=False,
        log_size=30000000,
        reserve_logs=5,
        throttle_limit=0,
        throttle_wait=16000
    )

    # Retrieve WAL properties.
    wal.properties()

    # List WAL transactions.
    wal.transactions()

    # Flush WAL with garbage collection.
    wal.flush(garbage_collect=True)

    # Get the available ranges of tick values.
    wal.tick_ranges()

    # Get the last available tick value.
    wal.last_tick()

    # Get recent WAL operations.
    wal.tail()

See :class:`WriteAheadLog` for API specification.
