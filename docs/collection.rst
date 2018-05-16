Collections
-----------

A **collection** contains :doc:`documents <document>`. It is uniquely identified
by its name, which must consist only of hyphen, underscore and alphanumeric
characters. There are *three* types of collections in python-arango:

* Standard Collection: contains regular :doc:`documents <document>`.
* :ref:`Vertex Collection <vertex-collections>`: contains vertex documents used
  in graphs.
* :ref:`Edge Collection <edge-collections>`: contains edge documents used in
  graphs.

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # List all collections in the database.
    db.collections()

    # Create a new collection named "students" if it does not exist.
    # This returns an API wrapper for "students" collection.
    if db.has_collection('students'):
        students = db.collection('students')
    else:
        students = db.create_collection('students')

    # Retrieve collection properties.
    students.name
    students.db_name
    students.properties()
    students.revision()
    students.statistics()
    students.checksum()
    students.count()

    # Perform various operations.
    students.load()
    students.unload()
    students.truncate()
    students.configure(journal_size=3000000)

    # Delete the collection.
    db.delete_collection('students')

See :ref:`StandardDatabase` and :ref:`StandardCollection` for API specification.
