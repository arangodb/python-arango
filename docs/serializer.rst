JSON Serialization
------------------

You can provide your own JSON serializer and deserializer during client
initialization. They must be callables that take a single argument.

**Example:**

.. testcode::

    import json

    from arango import ArangoClient

    # Initialize the ArangoDB client with custom serializer and deserializer.
    client = ArangoClient(
        hosts='http://localhost:8529',
        serializer=json.dumps,
        deserializer=json.loads
    )

See :ref:`ArangoClient` for API specification.
