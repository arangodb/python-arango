.. _admin-page:

Server Administration
---------------------

Python-arango provides operations for server administration and monitoring such
as retrieving statistics and reading logs.

Example:

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient(username='root', password='password')

    # Check connection to the server
    client.verify()

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

    # Get the log levels
    client.log_level()

    # Set the log levels
    client.set_log_level(
        agency='DEBUG',
        collector='INFO',
        threads='WARNING'
    )

    # List the endpoints the server is listening on
    client.endpoints()

    # Echo the last request
    client.echo()

    # Suspend the server
    client.sleep(seconds=2)

    # Shutdown the server
    client.shutdown()

    # Reload the routing collection
    client.reload_routing()


Note that the methods of :class:`arango.client.ArangoClient` above can only
be called by root user with access to ``_system`` database. Non-root users can
call the equivalent methods of :class:`arango.database.Database` through a
database they have access to instead. For example:

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.database(
        name='database-the-user-has-access-to',
        username='username',
        password='password'
    )

    # Check connection to the server
    db.verify()

    # Get the server version
    db.version()

    # Get the required DB version
    db.required_db_version()

    # Get the server time
    db.time()

    # Get the server role in a cluster
    db.role()

    # Get the server statistics
    db.statistics()

    # Read the server log
    db.read_log(level="debug")

    # Get the log levels
    db.log_level()

    # Set the log levels
    db.set_log_level(
        agency='DEBUG',
        collector='INFO',
        threads='WARNING'
    )

    # Echo the last request
    db.echo()

    # Suspend the server
    db.sleep(seconds=2)

    # Shutdown the server
    db.shutdown()

    # Reload the routing collection
    db.reload_routing()


Methods :func:`arango.client.ArangoClient.databases` and
:func:`arango.client.ArangoClient.endpoints` are not available to
non-root users. Refer to classes :class:`arango.client.ArangoClient` and
:ref::class:`arango.database.Database` for more details on admin methods.
