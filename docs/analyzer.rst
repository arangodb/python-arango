Analyzers
---------

Python-arango supports **analyzers**. For more information on analyzers, refer
to `ArangoDB manual`_.

.. _ArangoDB manual: https://docs.arangodb.com

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Retrieve list of analyzers.
    db.analyzers()

    # Create an analyzer.
    db.create_analyzer(
        name='test_analyzer',
        analyzer_type='identity',
        properties={},
        features=[]
    )

    # Delete an analyzer.
    db.delete_analyzer('test_analyzer', ignore_missing=True)

Refer to :ref:`StandardDatabase` class for API specification.
