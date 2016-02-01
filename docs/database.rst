Databases
---------

A single ArangoDB instance can house multiple databases. Each database in turn
can have its own set of collections, graphs, and dedicated worker processes.
There is always a default database named ``_system`` which cannot be dropped,
can only be accessed with root privileges, and provides special operations for
creating, deleting and enumerating other user-defined databases.

For more information on the HTTP REST API for database management visit this
`page <https://docs.arangodb.com/HTTP/Database/NotesOnDatabases.html>`_.

**Example:**

.. code-block:: python

    from arango import ArangoClient

    # Initialize the ArangoDB client as user "greg"
    client = ArangoClient(username='greg', password='pass')

    # List all existing databases
    client.databases()

    # Create a database with default user, which in this case would be "greg"
    db1 = client.create_database('test_db_01')

    # Create another database with new users "jane", "john" and "anna"
    db2 = client.create_database(
        name='test_db_02',
        users=[
            {'username': 'jane', 'password': 'foo', 'active': True},
            {'username': 'john', 'password': 'bar', 'active': True},
            {'username': 'anna', 'password': 'baz', 'active': True},
        ]
    )

    # Retrieve the database properties
    print(db1.properties())
    print(db2.properties())

    # Retrieve an existing database as user "john"
    db2 = client.db('test_db_02', username='john', password='bar')

    # Delete an existing database
    client.delete_database('test_db_01')

Refer to the :ref:`ArangoClient` and :ref:`Database` classes for more details
on database management, and the :doc:`user` page for more details on how to
create, update, replace or delete database users separately.
