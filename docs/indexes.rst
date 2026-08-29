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

    # Add a new persistent index on document fields "continent" and "country".
    persistent_index = {'type': 'persistent', 'fields': ['continent', 'country'], 'unique': True}
    index = cities.add_index(persistent_index)

    # Add new fulltext indexes on fields "continent" and "country".
    index = cities.add_index({'type': 'fulltext', 'fields': ['continent']})
    index = cities.add_index({'type': 'fulltext', 'fields': ['country']})

    # Add a new persistent index on field 'population'.
    persistent_index = {'type': 'persistent', 'fields': ['population'], 'sparse': False}
    index = cities.add_index(persistent_index)

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
    mdi_index = {'type': 'mdi', 'fields': ['x', 'y'], 'fieldValueTypes': 'double'}
    index = cities.add_index(mdi_index)

    # Indexes may be added with a name that can be referred to in AQL queries.
    persistent_index = {'type': 'persistent', 'fields': ['country'], 'unique': True, 'name': 'my_hash_index'}
    index = cities.add_index(persistent_index)

    # Delete the last index from the collection.
    cities.delete_index(index['id'])

    # Insert documents with vector embeddings.
    cities.insert_many([
        {
            '_key': f'city{i}',
            'continent': f'continent{i}',
            'country': f'country{i}',
            'population': i,
            'coordinates': [float(i % 180), float(i % 90)],
            'x': float(i),
            'y': float(i),
            'embedding': [float(i), float(i % 7), float(i % 11), 1.0],
        }
        for i in range(100)
    ])

    # Let ArangoDB determine the number of vector-index centroids.
    vector_index = cities.add_index({
        'type': 'vector',
        'fields': ['embedding'],
        'name': 'vector_index',
        'params': {
            'metric': 'cosine',
            'dimension': 4,
        },
    })

    # Index creation may succeed even if vector training fails.
    if vector_index.get('trainingState') != 'ready':
        raise RuntimeError(
            vector_index.get('errorMessage', 'Vector index is not ready')
        )

Omitted or scaling-object ``nLists``, ``numberOfDocsPerCentroid``, factory
placeholders such as ``IVF{},Flat``, and successful-but-unusable creation
behavior require ArangoDB 3.12.10 or later. A successful creation response
means that the index exists, but callers should check ``trainingState`` before
using it. If training fails permanently, the state is ``"unusable"`` and
``errorMessage`` describes the failure.

See :ref:`StandardCollection` for API specification.
