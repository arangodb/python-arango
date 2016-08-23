.. _user-page:

User Management
---------------

ArangoDB users can be easily created, modified or deleted using python-arango.
Operations to grant or revoke user access to specific databases are provided
as well. For more information on the HTTP REST API for user management visit
this `page <https://docs.arangodb.com/HTTP/UserManagement>`__.

.. note::
    Some operations in the example below require root privileges (i.e. the
    user must have access to the ``_system`` database).

**Examples:**

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()

    # List all existing users
    client.users()

    # Create a new user
    client.create_user(username='lisa', password='foo')

    # Update an existing user and force password change by disallowing the
    # user from issuing API calls until his/her password is changed
    client.update_user(username='emma', password='bar', change_password=True)

    # Replace an existing user
    client.replace_user(username='greg', password='baz', extra={'dept': 'IT'})

    # Grant database access to an existing user
    client.grant_user_access(username='kate', database='students')

    # Revoke database access from an existing user
    client.revoke_user_access(username='jake', database='students')

    # Delete an existing user
    client.delete_user(username='jill')

Refer to :ref:`ArangoClient` class for more details.
