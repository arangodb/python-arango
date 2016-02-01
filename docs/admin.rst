Server Administration
---------------------

Python-arango provides operations for server administration and monitoring.
For more information on the HTTP REST API visit this
`page <https://docs.arangodb.com/HTTP/AdministrationAndMonitoring>`__.

.. note::
     Some operations in the example below require root privileges (i.e. the
     user must have access to the ``_system`` database).

.. warning::
    `Replication <https://docs.arangodb.com/HTTP/Replications>`__ and
    `sharding <https://docs.arangodb.com/HTTP/ShardingInterface>`__ are
    currently not supported by python-arango.

**Example:**

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()

    # List the databases
    client.databases()

    # Get the server version
    client.version()

    # Get the required DB version
    client.required_db_version()

    # Get the server time
    client.time()

    # Get the server role in a cluster
    client.role()

    # Get the server statistics
    client.statistics()

    # Read the server log
    client.read_log(level="debug")

    # List the endpoints the server is listening on
    client.endpoints()

    # Echo the last request
    client.echo()

    # Suspend the server (requires root access)
    client.sleep(seconds=2)

    # Shutdown the server (requires root access)
    client.shutdown()

    # Reload the routing collection (requires root access)
    client.reload_routing()


Refer to the :ref:`ArangoClient` class for more details.
