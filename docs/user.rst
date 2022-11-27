Users and Permissions
---------------------

Python-arango provides operations for managing users and permissions. Most of
these operations can only be performed by admin users via ``_system`` database.

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "_system" database as root user.
    sys_db = client.db('_system', username='root', password='passwd')

    # List all users.
    sys_db.users()

    # Create a new user.
    sys_db.create_user(
        username='johndoe@gmail.com',
        password='first_password',
        active=True,
        extra={'team': 'backend', 'title': 'engineer'}
    )

    # Check if a user exists.
    sys_db.has_user('johndoe@gmail.com')

    # Retrieve details of a user.
    sys_db.user('johndoe@gmail.com')

    # Update an existing user.
    sys_db.update_user(
        username='johndoe@gmail.com',
        password='second_password',
        active=True,
        extra={'team': 'frontend', 'title': 'engineer'}
    )

    # Replace an existing user.
    sys_db.replace_user(
        username='johndoe@gmail.com',
        password='third_password',
        active=True,
        extra={'team': 'frontend', 'title': 'architect'}
    )

    # Retrieve user permissions for all databases and collections.
    sys_db.permissions('johndoe@gmail.com')

    # Retrieve user permission for "test" database.
    sys_db.permission(
        username='johndoe@gmail.com',
        database='test'
    )

    # Retrieve user permission for "students" collection in "test" database.
    sys_db.permission(
        username='johndoe@gmail.com',
        database='test',
        collection='students'
    )

    # Update user permission for "test" database.
    sys_db.update_permission(
        username='johndoe@gmail.com',
        permission='rw',
        database='test'
    )

    # Update user permission for "students" collection in "test" database.
    sys_db.update_permission(
        username='johndoe@gmail.com',
        permission='ro',
        database='test',
        collection='students'
    )

    # Reset user permission for "test" database.
    sys_db.reset_permission(
        username='johndoe@gmail.com',
        database='test'
    )

    # Reset user permission for "students" collection in "test" database.
    sys_db.reset_permission(
        username='johndoe@gmail.com',
        database='test',
        collection='students'
    )

See :ref:`StandardDatabase` for API specification.
