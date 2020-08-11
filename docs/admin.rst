Server Administration
---------------------

Python-arango provides operations for server administration and monitoring.
Most of these operations can only be performed by admin users via ``_system``
database.

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "_system" database as root user.
    sys_db = client.db('_system', username='root', password='passwd')

    # Retrieve the server version.
    sys_db.version()

    # Retrieve the server details.
    sys_db.details()

    # Retrieve the target DB version.
    sys_db.required_db_version()

    # Retrieve the database engine.
    sys_db.engine()

    # Retrieve the server time.
    sys_db.time()

    # Retrieve the server role in a cluster.
    sys_db.role()

    # Retrieve the server statistics.
    sys_db.statistics()

    # Read the server log.
    sys_db.read_log(level="debug")

    # Retrieve the log levels.
    sys_db.log_levels()

    # Set the log .
    sys_db.set_log_levels(
        agency='DEBUG',
        collector='INFO',
        threads='WARNING'
    )

    # Echo the last request.
    sys_db.echo()

    # Reload the routing collection.
    sys_db.reload_routing()

    # Retrieve server metrics.
    sys_db.metrics()


Features available in enterprise edition only:

.. code-block:: python

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "_system" database as root user using JWT authentication.
    sys_db = client.db(
        '_system',
        username='root',
        password='passwd',
        auth_method='jwt'
    )

    # Retrieve JWT secrets.
    sys_db.jwt_secrets()

    # Hot-reload JWT secrets.
    sys_db.reload_jwt_secrets()

    # Rotate the user-supplied keys for encryption.
    sys_db.encryption()


See :ref:`StandardDatabase` for API specification.
