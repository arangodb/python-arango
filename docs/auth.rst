Authentication
--------------

Python-arango supports two HTTP authentication methods: basic and JSON Web
Tokens (JWT).

Basic Authentication
====================

This is python-arango's default authentication method.

**Example:**

.. testcode::
    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user using basic auth.
    db = client.db('test', username='root', password='passwd')

    # The authentication method can be given explicitly.
    db = client.db(
        'test',
        username='root',
        password='passwd',
        auth_method='basic'
    )

JSON Web Tokens (JWT)
=====================

Python-arango automatically obtains JSON web tokens from the server using
username and password. It also refreshes expired tokens and retries requests.
The client and server clocks must be synchronized for the automatic refresh
to work correctly.

**Example:**

.. testcode::
    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user using JWT.
    db = client.db(
        'test',
        username='root',
        password='passwd',
        auth_method='jwt'
    )

    # Manually refresh the token.
    db.conn.refresh_token()

    # Override the token expiry compare leeway in seconds (default: 0) to
    # compensate for out-of-sync clocks between the client and server.
    db.conn.ext_leeway = 2

User generated JWT token can be used for superuser access.

**Example:**

.. code-block:: python

    from calendar import timegm
    from datetime import datetime

    import jwt

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Generate the JWT token manually.
    now = timegm(datetime.utcnow().utctimetuple())
    token = jwt.encode(
        payload={
            'iat': now,
            'exp': now + 3600,
            'iss': 'arangodb',
            'server_id': 'client'
        },
        key='secret',
    ).decode('utf-8')

    # Connect to "test" database as superuser using the token.
    db = client.db('test', superuser_token=token)
