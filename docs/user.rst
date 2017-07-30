.. _user-page:

User and Access Management
--------------------------

Python-arango provides operations for managing users and database/collection
access.

Example:

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()

    # List all users
    client.users()

    # Create a new user
    client.create_user(
        username='johndoe@gmail.com',
        password='first_password',
        extra={'team': 'backend', 'title': 'engineer'}
    )
    # Update an existing user
    client.update_user(
        username='johndoe@gmail.com',
        password='second_password',
        extra={'team': 'frontend'}
    )
    # Replace an existing user
    client.replace_user(
        username='johndoe@gmail.com',
        password='third_password',
        extra={'team': 'frontend', 'title': 'architect'}
    )
    # Grant database access to an existing user
    client.grant_user_access(
        username='johndoe@gmail.com',
        database='my_database'
    )
    # Get full database and collection access details of an existing user
    client.user_access('johndoe@gmail.com', full=True)

    # Revoke database access from an existing user
    client.revoke_user_access(
        username='johndoe@gmail.com',
        database='my_database'
    )

    # Delete an existing user
    client.delete_user(username='johndoe@gmail.com')


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

    # List all users
    db.users()

    # Create a new user
    db.create_user(
        username='johndoe@gmail.com',
        password='first_password',
        extra={'team': 'backend', 'title': 'engineer'}
    )
    # Update an existing user
    db.update_user(
        username='johndoe@gmail.com',
        password='second_password',
        extra={'team': 'frontend'}
    )
    # Replace an existing user
    db.replace_user(
        username='johndoe@gmail.com',
        password='third_password',
        extra={'team': 'frontend', 'title': 'architect'}
    )
    # Grant database access to an existing user
    db.grant_user_access('johndoe@gmail.com')

    # Get database access details of an existing user
    db.user_access('johndoe@gmail.com')

    # Revoke database access from an existing user
    db.revoke_user_access('johndoe@gmail.com')

    # Delete an existing user
    client.delete_user(username='johndoe@gmail.com')

Collection-specific user access management is also possible:

.. code-block:: python

    col = db.collection('some-collection')

    # Grant collection access to an existing user
    col.grant_user_access('johndoe@gmail.com')

    # Get collection access details of an existing user
    col.user_access('johndoe@gmail.com')

    # Revoke collection access from an existing user
    col.revoke_user_access('johndoe@gmail.com')


Refer to classes :class:`arango.client.ArangoClient`,
:class:`arango.database.Database`, and :class:`arango.collections.Collection`
classes for more details.
