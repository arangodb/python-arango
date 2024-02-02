Indexes
-------

**Indexes** can be added to collections to speed up document lookups. Every
collection has a primary hash index on ``_key`` field by default. This index
cannot be deleted or modified. Every edge collection has additional indexes
on fields ``_from`` and ``_to``. For more information on indexes, refer to
`ArangoDB manual`_.

.. _ArangoDB manual: https://docs.arangodb.com

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Create a new collection named "cities".
    cities = db.create_collection('cities')

    # List the indexes in the collection.
    cities.indexes()

    # Add a new hash index on document fields "continent" and "country".
    hash_index = {'type': 'hash', 'fields': ['continent', 'country'], 'unique': True}
    index = cities.add_index(hash_index)

    # Add new fulltext indexes on fields "continent" and "country".
    index = cities.add_index({'type': 'fulltext', 'fields': ['continent']})
    index = cities.add_index({'type': 'fulltext', 'fields': ['country']})

    # Add a new skiplist index on field 'population'.
    skiplist_index = {'type': 'skiplist', 'fields': ['population'], 'sparse': False}
    index = cities.add_index(skiplist_index)

    # Add a new geo-spatial index on field 'coordinates'.
    geo_index = {'type': 'geo', 'fields': ['coordinates']}
    index = cities.add_index(geo_index)

    # Add a new persistent index on field 'currency'.
    persistent_index = {'type': 'persistent', 'fields': ['currency'], 'sparse': True}
    index = cities.add_index(persistent_index)

    # Add a new TTL (time-to-live) index on field 'currency'.
    ttl_index = {'type': 'ttl', 'fields': ['currency'], 'expireAfter': 200}
    index = cities.add_index(ttl_index)

    # Add MDI (multi-dimensional) index on field 'x' and 'y'.
    mdi_index = {'type': 'mdi', 'fields': ['x', 'y'], 'field_value_types': ['double']}
    index = cities.add_index(mdi_index) 

    # Indexes may be added with a name that can be referred to in AQL queries.
    hash_index = {'type': 'hash', 'fields': ['country'], 'unique': True, 'name': 'my_hash_index'}
    index = cities.add_index(hash_index)

    # Delete the last index from the collection.
    cities.delete_index(index['id'])

See :ref:`StandardCollection` for API specification.
