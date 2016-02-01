Graphs
------

An ArangoDB **graph** consists of **vertices** and **edges**. Edges are stored
as documents in :ref:`edge collections <edge-collections>`, whereas vertices
are stored as documents in :ref:`vertex collections <vertex-collections>`
(edges can be vertices also). The combination of edge and vertex collections
involved in a graph is defined :ref:`edge definitions <edge-definitions>`. For
more general information on graphs, vertices and edges refer to this
`page <https://docs.arangodb.com/Manual/Graphs>`__.

**Example:**

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.db('my_database')

    # List existing graphs
    db.graphs()

    # Create a new graph
    schedule = db.create_graph('schedule')

    # Retrieve the graph properties
    schedule.properties()

    # Delete an existing graph
    db.delete_graph('schedule')

.. _vertex-collections:

Vertex Collections
==================

A **vertex collection** consists of vertex documents. It is uniquely identified
by its name, which must consist only of alphanumeric characters, hyphen and
the underscore characters. Vertex collections share their namespace with other
types of collections.

The documents in a vertex collection are fully accessible from a standard
collection. Managing documents through a vertex collection, however, adds
additional *guarantees*: all modifications are executed in transactions, and
if a vertex is deleted all connected edges are also deleted automatically.

For more information on the HTTP REST API for vertices and vertex collections
refer to this `page <https://docs.arangodb.com/HTTP/Gharial/Vertices.html>`__.


**Example:**

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.db('my_database')
    schedule = db.graph('schedule')

    # Create a new vertex collection
    profs = schedule.create_vertex_collection('profs')

    # List orphan vertex collections (without edges)
    schedule.orphan_collections()

    # List existing vertex collections
    schedule.vertex_collections()

    # Retrieve an existing vertex collection
    profs = schedule.vertex_collection('profs')

    # Vertex collections have a similar interface to standard collections
    profs.insert({'_key': 'donald', 'name': 'Professor Donald'})
    profs.get('donald')
    profs.properties()

    # Delete an existing vertex collection
    schedule.delete_vertex_collection('profs', purge=True)

Refer to the :ref:`Graph` and :ref:`VertexCollection` classes for more details.

.. _edge-definitions:

Edge Definitions
================

An **edge definition** specifies which vertex and edge collections are used in
a particular graph (see example below).

.. _edge-collections:

An **edge collection** consists of edge documents. Same as vertex collections
it is uniquely identified by its name which must consist only of alphanumeric
characters, hyphen and the underscore characters. Edge collections share their
namespace with other types of collections.

The documents in an edge collection are fully accessible from a standard
collection. Managing documents through an edge collection, however, adds
additional *guarantees*: all modifications are executed in transactions and
edge documents are checked against the edge definitions on *insert*.

For more information on the HTTP REST API for edge definitions and collections
refer to this `page <https://docs.arangodb.com/HTTP/Gharial/Edges.html>`__.

**Example:**

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.db('my_database')
    schedule = db.graph('schedule')

    # Create some vertex collections
    schedule.create_vertex_collection('profs')
    schedule.create_vertex_collection('courses')

    # Create a new edge definition (and a new edge collection)
    schedule.create_edge_collection(
        name='teaches',
        from_collections=['profs'],
        to_collections=['courses']
    )

    # List existing edge definitions
    schedule.edge_definitions()

    # Retrieve an existing edge collection
    teaches = schedule.edge_collection('teaches')

    # Edge collections have a similar interface to standard collections
    teaches.insert({
        '_key': 'michelle-CSC101'
        '_from': 'profs/michelle',
        '_to': 'courses/CSC101'
    })
    print(teaches.get('michelle-CSC101'))

    # Delete an existing edge definition (and the collection)
    schedule.delete_edge_definition('teaches', purge=False)

Refer to the :ref:`Graph` and :ref:`EdgeCollection` classes for more details.

.. _graph-traversals:

Graph Traversals
================

**Graph traversals** (which are executed on the server) can be initiated using
the :func:`~arango.graph.Graph.traverse` method in python-arango. A traversal
can span across multiple vertex collections but only a single edge collection,
and walk over the documents in a variety of ways (see example below). For more
information on the HTTP REST API for executing graph traversals refer to this
`page <https://docs.arangodb.com/HTTP/Traversal/index.html>`__.

**Example:**

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.db('my_database')
    schedule = db.create_graph('schedule')

    # Define the vertex collections and edge definitions
    profs = schedule.create_vertex_collection('profs')
    courses = schedule.create_vertex_collection('courses')
    teaches = schedule.create_edge_collection(
        name='teaches',
        from_collections=['profs'],
        to_collections=['courses']
    )
    # Insert vertices
    profs.insert({'_key': 'michelle', 'name': 'Professor Michelle'})
    courses.insert({'_key': 'CSC101', 'name': 'Introduction to CS'})
    courses.insert({'_key': 'MAT223', 'name': 'Linear Algebra'})
    courses.insert({'_key': 'STA201', 'name': 'Statistics'})

    # Insert edges
    teaches.insert({'_from': 'profs/michelle', '_to': 'courses/CSC101'})
    teaches.insert({'_from': 'profs/michelle', '_to': 'courses/STA201'})
    teaches.insert({'_from': 'profs/michelle', '_to': 'courses/MAT223'})

    # Traverse the graph in outbound direction, breath-first
    traversal_results = schedule.traverse(
        start_vertex='profs/michelle',
        direction='outbound',
        strategy='bfs',
        edge_uniqueness='global',
        vertex_uniqueness='global',
    )
    print(traversal_results['visited'])

Refer to the :ref:`Graph` class for more details.