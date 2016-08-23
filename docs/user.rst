.. _user-page:

User Management
---------------

Python-arango provides operations for managing users and database access. These
operations require root privileges (i.e. access to the ``_system`` database).

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
    # Get database access details of an existing user
    client.user_access('johndoe@gmail.com')

    # Revoke database access from an existing user
    client.revoke_user_access(
        username='johndoe@gmail.com',
        database='my_database'
    )

    # Delete an existing user
    client.delete_user(username='johndoe@gmail.com')


Refer to :ref:`ArangoClient` class for more details.
