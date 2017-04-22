.. _client-page:

Getting Started
---------------

Here is an example showing how a **python-arango** client can be initialized
and used:

.. code-block:: python

    from arango import ArangoClient

    # Initialize the client for ArangoDB
    client = ArangoClient(
        protocol='http',
        host='localhost',
        port=8529,
        username='root',
        password='',
        enable_logging=True
    )

    # Create a new database named "my_database"
    db = client.create_database('my_database')

    # Create a new user with access to "my_database"
    client.create_user('admin', 'password')
    client.grant_user_access('admin', 'my_database')

    # Create a new collection named "students"
    students = db.create_collection('students')

    # Add a hash index to the collection
    students.add_hash_index(fields=['name'], unique=True)

    # Insert new documents into the collection
    students.insert({'name': 'jane', 'age': 19})
    students.insert({'name': 'josh', 'age': 18})
    students.insert({'name': 'jake', 'age': 21})

    # Execute an AQL query
    result = db.aql.execute('FOR s IN students RETURN s')
    print([student['name'] for student in result])

Read the rest of the documentation to discover much more!
