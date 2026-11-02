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

JWTs are sent in the HTTP ``Authorization`` header as Bearer tokens. Token
renewal depends on whether the driver obtains tokens using username/password
or the application supplies them.

Driver-managed tokens
~~~~~~~~~~~~~~~~~~~~~

With ``auth_method='jwt'``, the driver obtains an initial token using the
configured username and password when ``client.db()`` is called. It retains
those credentials to obtain replacement tokens. If initial acquisition fails,
``client.db()`` raises an error instead of returning a database wrapper.

For each database request, the authentication policy is:

1. Send the request with the current token.
2. If the response has both HTTP status 401 and ArangoDB error code 11, attempt
   to obtain a replacement token using the configured credentials.
3. If renewal succeeds, retry the original request once with the replacement
   token.

   * If that retry fails, the application receives the error. The driver does
     not renew the token or retry the request again.

4. If obtaining a replacement token fails, the original request is not retried.
   The error from that renewal attempt is raised to the caller.

Both the HTTP status and ArangoDB error code must match to trigger renewal.
Other responses, including HTTP 403, do not trigger JWT renewal or an
authentication retry. For example, a rejected version request raises
:class:`arango.exceptions.ServerVersionError`.

HTTP 401/error code 11 does not prove that the token expired. The same renewal
and retry policy applies if the server rejects a locally unexpired token.
Renewal authenticates the same user and does not grant additional permissions;
if access is still denied, the retried request fails normally.

Renewal is reactive: it happens after a qualifying server rejection, not on a
timer or proactively before expiration. The driver does not fall back to Basic
authentication when JWT authentication fails.

Keep client and server clocks synchronized because the driver checks token
expiration when accepting a token.

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

Application-managed tokens
~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``user_token`` or ``superuser_token`` to supply a token obtained outside
the driver. These tokens are not renewed automatically: the application is
responsible for obtaining replacements. Supplied username/password and
``auth_method`` are ignored when either token argument is used, so they cannot
provide renewal credentials for that connection.

The credentials-based renewal policy above does not apply to these tokens.
``user_token`` is checked for expiration locally when the connection is
created. ``superuser_token`` is accepted without a local expiry check at
construction; the server can reject it on the first request. With
``verify=True``, that first request occurs during ``client.db()`` and a rejected
token causes :class:`arango.exceptions.ServerConnectionError`.

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
    )

    # Connect to "test" database as superuser using the token.
    db = client.db('test', superuser_token=token)

    # Connect to "test" database as user using the token.
    db = client.db('test', user_token=token)

Replace an application-managed token using ``db.conn.set_token(new_token)``.
This changes the token used by the database wrapper and existing collection
wrappers sharing its connection. Separate connections created by other
``client.db()`` calls are unaffected. For both user and superuser connections,
``set_token()`` checks expiration locally and raises
:class:`arango.exceptions.JWTExpiredError` if the replacement has expired.

**Example:**

.. code-block:: python

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as a user using the token.
    db = client.db('test', user_token='token')

    # Set the user token on the connection object.
    db.conn.set_token('new token')

    # Connect to "test" database as superuser using the token.
    db = client.db('test', superuser_token='superuser token')

    # Set the user token on the connection object.
    db.conn.set_token('new superuser token')
