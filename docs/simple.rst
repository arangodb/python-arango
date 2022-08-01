Simple Queries
--------------

.. caution:: There is no option to add a TTL (Time to live) or batch size optimizations to the Simple Queries due to how Arango is handling simple collection HTTP requests. Your request may time out and you'll see a CursorNextError exception. The AQL queries provide full functionality.

Here is an example of using ArangoDB's **simply queries**:

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Get the API wrapper for "students" collection.
    students = db.collection('students')

    # Get the IDs of all documents in the collection.
    students.ids()

    # Get the keys of all documents in the collection.
    students.keys()

    # Get all documents in the collection with skip and limit.
    students.all(skip=0, limit=100)

    # Find documents that match the given filters.
    students.find({'name': 'Mary'}, skip=0, limit=100)

    # Get documents from the collection by IDs or keys.
    students.get_many(['id1', 'id2', 'key1'])

    # Get a random document from the collection.
    students.random()

    # Update all documents that match the given filters.
    students.update_match({'name': 'Kim'}, {'age': 20})

    # Replace all documents that match the given filters.
    students.replace_match({'name': 'Ben'}, {'age': 20})

    # Delete all documents that match the given filters.
    students.delete_match({'name': 'John'})

Here are all simple query (and other utility) methods available:

* :func:`arango.collection.Collection.all`
* :func:`arango.collection.Collection.find`
* :func:`arango.collection.Collection.find_near`
* :func:`arango.collection.Collection.find_in_range`
* :func:`arango.collection.Collection.find_in_radius`
* :func:`arango.collection.Collection.find_in_box`
* :func:`arango.collection.Collection.find_by_text`
* :func:`arango.collection.Collection.get_many`
* :func:`arango.collection.Collection.ids`
* :func:`arango.collection.Collection.keys`
* :func:`arango.collection.Collection.random`
* :func:`arango.collection.StandardCollection.update_match`
* :func:`arango.collection.StandardCollection.replace_match`
* :func:`arango.collection.StandardCollection.delete_match`
* :func:`arango.collection.StandardCollection.import_bulk`
