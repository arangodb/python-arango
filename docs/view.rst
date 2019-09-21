Views and ArangoSearch
----------------------

Python-arango supports **view** management. For more information on view
properties, refer to `ArangoDB manual`_.

.. _ArangoDB manual: https://docs.arangodb.com

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Retrieve list of views.
    db.views()

    # Create a view.
    db.create_view(
        name='foo',
        view_type='arangosearch',
        properties={
            'cleanupIntervalStep': 0,
            'consolidationIntervalMsec': 0
        }
    )

    # Rename a view.
    db.rename_view('foo', 'bar')

    # Retrieve view properties.
    db.view('bar')

    # Partially update view properties.
    db.update_view(
        name='bar',
        properties={
            'cleanupIntervalStep': 1000,
            'consolidationIntervalMsec': 200
        }
    )

    # Replace view properties. Unspecified ones are reset to default.
    db.replace_view(
        name='bar',
        properties={'cleanupIntervalStep': 2000}
    )

    # Delete a view.
    db.delete_view('bar')


Python-arango also supports **ArangoSearch** views.

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Create an ArangoSearch view.
    db.create_arangosearch_view(
        name='arangosearch_view',
        properties={'cleanupIntervalStep': 0}
    )

    # Partially update an ArangoSearch view.
    db.update_arangosearch_view(
        name='arangosearch_view',
        properties={'cleanupIntervalStep': 1000}
    )

    # Replace an ArangoSearch view.
    db.replace_arangosearch_view(
        name='arangosearch_view',
        properties={'cleanupIntervalStep': 2000}
    )

    # ArangoSearch views can be retrieved or deleted using regular view API
    db.view('arangosearch_view')
    db.delete_view('arangosearch_view')


For more information on the content of view **properties**, see
https://www.arangodb.com/docs/stable/http/views-arangosearch.html

Refer to :ref:`StandardDatabase` class for API specification.
