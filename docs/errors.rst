Error Handling
--------------

All python-arango exceptions inherit :class:`arango.exceptions.ArangoError`,
which splits into subclasses :class:`arango.exceptions.ArangoServerError` and
:class:`arango.exceptions.ArangoClientError`.

Server Errors
=============

:class:`arango.exceptions.ArangoServerError` exceptions lightly wrap non-2xx
HTTP responses coming from ArangoDB. Each exception object contains the error
message, error code and HTTP request response details.

**Example:**

.. testcode::

    from arango import ArangoClient, ArangoServerError, DocumentInsertError

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Get the API wrapper for "students" collection.
    students = db.collection('students')

    try:
        students.insert({'_key': 'John'})
        students.insert({'_key': 'John'})  # duplicate key error

    except DocumentInsertError as exc:

        assert isinstance(exc, ArangoServerError)
        assert exc.source == 'server'

        exc.message           # Exception message usually from ArangoDB
        exc.error_message     # Raw error message from ArangoDB
        exc.error_code        # Error code from ArangoDB
        exc.url               # URL (API endpoint)
        exc.http_method       # HTTP method (e.g. "POST")
        exc.http_headers      # Response headers
        exc.http_code         # Status code (e.g. 200)

        # You can inspect the ArangoDB response directly.
        response = exc.response
        response.method       # HTTP method (e.g. "POST")
        response.headers      # Response headers
        response.url          # Full request URL
        response.is_success   # Set to True if HTTP code is 2XX
        response.body         # JSON-deserialized response body
        response.raw_body     # Raw string response body
        response.status_text  # Status text (e.g "OK")
        response.status_code  # Status code (e.g. 200)
        response.error_code   # Error code from ArangoDB

        # You can also inspect the request sent to ArangoDB.
        request = exc.request
        request.method        # HTTP method (e.g. "post")
        request.endpoint      # API endpoint starting with "/_api"
        request.headers       # Request headers
        request.params        # URL parameters
        request.data          # Request payload

See :ref:`Response` and :ref:`Request` for reference.

Client Errors
=============

:class:`arango.exceptions.ArangoClientError` exceptions originate from
python-arango client itself. They do not contain error codes nor HTTP request
response details.

**Example:**

.. testcode::

    from arango import ArangoClient, ArangoClientError, DocumentParseError

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Get the API wrapper for "students" collection.
    students = db.collection('students')

    try:
        students.get({'_id': 'invalid_id'})  # malformed document

    except DocumentParseError as exc:

        assert isinstance(exc, ArangoClientError)
        assert exc.source == 'client'

        # Only the error message is set.
        error_message = exc.message
        assert exc.error_code is None
        assert exc.error_message is None
        assert exc.url is None
        assert exc.http_method is None
        assert exc.http_code is None
        assert exc.http_headers is None
        assert exc.response is None
        assert exc.request is None

Exceptions
==========

Below are all exceptions from python-arango.

.. automodule:: arango.exceptions
    :members:


Error Codes
===========

The `errno` module contains a constant mapping to `ArangoDB's error codes
<https://www.arangodb.com/docs/stable/appendix-error-codes.html>`_.

.. automodule:: arango.errno
    :members:
