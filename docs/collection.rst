.. _collection-page:

Collections
-----------

A **collection** contains :ref:`documents <document-page>`. It is uniquely
identified by its name which must consist only of alphanumeric, hyphen and
underscore characters. There are *three* types of collections: standard
**document collections** which contain normal documents, **vertex collections**
which also contain normal documents, and **edge collections** which contain
:ref:`edges <edge-documents>`.

Here is an example showing how collections can be managed:

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.db('my_database')

    # List all collections in "my_database"
    db.collections()

    # Create a new collection named "students"
    students = db.create_collection('students')

    # Retrieve an existing collection
    students = db.collection('students')

    # Retrieve collection information
    students.properties()
    students.revision()
    students.statistics()
    students.checksum()
    students.count()

    # Perform actions on a collection
    students.load()
    students.unload()
    students.truncate()
    students.configure(journal_size=3000000)

Refer to :ref:`Collection` class for more details.
