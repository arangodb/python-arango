Graphs
------

A **graph** consists of vertices and edges. Vertices are stored as documents in
:ref:`vertex collections <vertex-collections>` and edges stored as documents in
:ref:`edge collections <edge-collections>`. The collections used in a graph and
their relations are specified with :ref:`edge definitions <edge-definitions>`.
For more information, refer to `ArangoDB manual`_.

.. _ArangoDB manual: https://docs.arangodb.com

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # List existing graphs in the database.
    db.graphs()

    # Create a new graph named "school" if it does not already exist.
    # This returns an API wrapper for "school" graph.
    if db.has_graph('school'):
        school = db.graph('school')
    else:
        school = db.create_graph('school')

    # Retrieve various graph properties.
    school.name
    school.db_name
    school.vertex_collections()
    school.edge_definitions()

    # Delete the graph.
    db.delete_graph('school')

.. _edge-definitions:

Edge Definitions
================

An **edge definition** specifies a directed relation in a graph. A graph can
have arbitrary number of edge definitions. Each edge definition consists of the
following components:

* **From Vertex Collections:** contain "from" vertices referencing "to" vertices.
* **To Vertex Collections:** contain "to" vertices referenced by "from" vertices.
* **Edge Collection:** contains edges that link "from" and "to" vertices.

Here is an example body of an edge definition:

.. testcode::

    {
        'edge_collection': 'teach',
        'from_vertex_collections': ['teachers'],
        'to_vertex_collections': ['lectures']
    }

Here is an example showing how edge definitions are managed:

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Get the API wrapper for graph "school".
    if db.has_graph('school'):
        school = db.graph('school')
    else:
        school = db.create_graph('school')

    # Create an edge definition named "teach". This creates any missing
    # collections and returns an API wrapper for "teach" edge collection.
    if not school.has_edge_definition('teach'):
        teach = school.create_edge_definition(
            edge_collection='teach',
            from_vertex_collections=['teachers'],
            to_vertex_collections=['teachers']
        )

    # List edge definitions.
    school.edge_definitions()

    # Replace the edge definition.
    school.replace_edge_definition(
        edge_collection='teach',
        from_vertex_collections=['teachers'],
        to_vertex_collections=['lectures']
    )

    # Delete the edge definition (and its collections).
    school.delete_edge_definition('teach', purge=True)

.. _vertex-collections:

Vertex Collections
==================

A **vertex collection** contains vertex documents, and shares its namespace
with all other types of collections. Each graph can have an arbitrary number of
vertex collections. Vertex collections that are not part of any edge definition
are called **orphan collections**. You can manage vertex documents via standard
collection API wrappers, but using vertex collection API wrappers provides
additional safeguards:

* All modifications are executed in transactions.
* If a vertex is deleted, all connected edges are also automatically deleted.

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Get the API wrapper for graph "school".
    school = db.graph('school')

    # Create a new vertex collection named "teachers" if it does not exist.
    # This returns an API wrapper for "teachers" vertex collection.
    if school.has_vertex_collection('teachers'):
        teachers = school.vertex_collection('teachers')
    else:
        teachers = school.create_vertex_collection('teachers')

    # List vertex collections in the graph.
    school.vertex_collections()

    # Vertex collections have similar interface as standard collections.
    teachers.properties()
    teachers.insert({'_key': 'jon', 'name': 'Jon'})
    teachers.update({'_key': 'jon', 'age': 35})
    teachers.replace({'_key': 'jon', 'name': 'Jon', 'age': 36})
    teachers.get('jon')
    teachers.has('jon')
    teachers.delete('jon')

You can manage vertices via graph API wrappers also, but you must use document
IDs instead of keys where applicable.

**Example:**

.. testcode::

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Get the API wrapper for graph "school".
    school = db.graph('school')

    # Create a new vertex collection named "lectures" if it does not exist.
    # This returns an API wrapper for "lectures" vertex collection.
    if school.has_vertex_collection('lectures'):
        school.vertex_collection('lectures')
    else:
        school.create_vertex_collection('lectures')

    # The "_id" field is required instead of "_key" field (except for insert).
    school.insert_vertex('lectures', {'_key': 'CSC101'})
    school.update_vertex({'_id': 'lectures/CSC101', 'difficulty': 'easy'})
    school.replace_vertex({'_id': 'lectures/CSC101', 'difficulty': 'hard'})
    school.has_vertex('lectures/CSC101')
    school.vertex('lectures/CSC101')
    school.delete_vertex('lectures/CSC101')

See :ref:`Graph` and :ref:`VertexCollection` for API specification.

.. _edge-collections:

Edge Collections
================

An **edge collection** contains :ref:`edge documents <edge-documents>`, and
shares its namespace with all other types of collections. You can manage edge
documents via standard collection API wrappers, but using edge collection API
wrappers provides additional safeguards:

* All modifications are executed in transactions.
* Edge documents are checked against the edge definitions on insert.

**Example:**

.. testsetup:: edge_collections

    client = ArangoClient()
    db = client.db('test', username='root', password='passwd')
    school = db.graph('school')

    if school.has_vertex_collection('lectures'):
        school.vertex_collection('lectures')
    else:
        school.create_vertex_collection('lectures')
    school.insert_vertex('lectures', {'_key': 'CSC101'})

    if school.has_vertex_collection('teachers'):
        school.vertex_collection('teachers')
    else:
        school.create_vertex_collection('teachers')
    school.insert_vertex('teachers', {'_key': 'jon'})

.. testcode:: edge_collections

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Get the API wrapper for graph "school".
    school = db.graph('school')

    # Get the API wrapper for edge collection "teach".
    if school.has_edge_definition('teach'):
        teach = school.edge_collection('teach')
    else:
        teach = school.create_edge_definition(
            edge_collection='teach',
            from_vertex_collections=['teachers'],
            to_vertex_collections=['lectures']
        )

    # Edge collections have a similar interface as standard collections.
    teach.insert({
        '_key': 'jon-CSC101',
        '_from': 'teachers/jon',
        '_to': 'lectures/CSC101'
    })
    teach.replace({
        '_key': 'jon-CSC101',
        '_from': 'teachers/jon',
        '_to': 'lectures/CSC101',
        'online': False
    })
    teach.update({
        '_key': 'jon-CSC101',
        'online': True
    })
    teach.has('jon-CSC101')
    teach.get('jon-CSC101')
    teach.delete('jon-CSC101')

    # Create an edge between two vertices (essentially the same as insert).
    teach.link('teachers/jon', 'lectures/CSC101', data={'online': False})

    # List edges going in/out of a vertex.
    teach.edges('teachers/jon', direction='in')
    teach.edges('teachers/jon', direction='out')

You can manage edges via graph API wrappers also, but you must use document
IDs instead of keys where applicable.

**Example:**

.. testcode:: edge_collections

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Get the API wrapper for graph "school".
    school = db.graph('school')

    # The "_id" field is required instead of "_key" field.
    school.insert_edge(
        collection='teach',
        edge={
            '_id': 'teach/jon-CSC101',
            '_from': 'teachers/jon',
            '_to': 'lectures/CSC101'
        }
    )
    school.replace_edge({
        '_id': 'teach/jon-CSC101',
        '_from': 'teachers/jon',
        '_to': 'lectures/CSC101',
        'online': False,
    })
    school.update_edge({
        '_id': 'teach/jon-CSC101',
        'online': True
    })
    school.has_edge('teach/jon-CSC101')
    school.edge('teach/jon-CSC101')
    school.delete_edge('teach/jon-CSC101')
    school.link('teach', 'teachers/jon', 'lectures/CSC101')
    school.edges('teach', 'teachers/jon', direction='in')

See :ref:`Graph` and :ref:`EdgeCollection` for API specification.

.. _graph-traversals:

Graph Traversals
================

**Graph traversals** are executed via the :func:`arango.graph.Graph.traverse`
method. Each traversal can span across multiple vertex collections, and walk
over edges and vertices using various algorithms.

**Example:**

.. testsetup:: traversals

    client = ArangoClient()
    db = client.db('test', username='root', password='passwd')
    school = db.graph('school')

    if school.has_vertex_collection('lectures'):
        school.vertex_collection('lectures')
    else:
        school.create_vertex_collection('lectures')

    if school.has_vertex_collection('teachers'):
        school.vertex_collection('teachers')
    else:
        school.create_vertex_collection('teachers')

.. testcode:: traversals

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Get the API wrapper for graph "school".
    school = db.graph('school')

    # Get API wrappers for "from" and "to" vertex collections.
    teachers = school.vertex_collection('teachers')
    lectures = school.vertex_collection('lectures')

    # Get the API wrapper for the edge collection.:
    teach = school.edge_collection('teach')

    # Insert vertices into the graph.
    teachers.insert({'_key': 'jon', 'name': 'Professor jon'})
    lectures.insert({'_key': 'CSC101', 'name': 'Introduction to CS'})
    lectures.insert({'_key': 'MAT223', 'name': 'Linear Algebra'})
    lectures.insert({'_key': 'STA201', 'name': 'Statistics'})

    # Insert edges into the graph.
    teach.insert({'_from': 'teachers/jon', '_to': 'lectures/CSC101'})
    teach.insert({'_from': 'teachers/jon', '_to': 'lectures/STA201'})
    teach.insert({'_from': 'teachers/jon', '_to': 'lectures/MAT223'})

    # Traverse the graph in outbound direction, breath-first.
    school.traverse(
        start_vertex='teachers/jon',
        direction='outbound',
        strategy='bfs',
        edge_uniqueness='global',
        vertex_uniqueness='global',
    )

See :func:`arango.graph.Graph.traverse` for API specification.
