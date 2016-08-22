.. _collection-page:

Collections
-----------

A **collection** consists of :ref:`documents <document-page>`. It is uniquely
identified by its name which must consist only of alphanumeric, hyphen and
underscore characters.

There are two types of collections: **document collections** which contain
:ref:`documents <document-page>` (standard) or **edge collections** which
contain :ref:`edges <edge-documents>`. By default, collections use the
**traditional** key generator which generates key values in a non-deterministic
fashion. A deterministic, auto-increment key generator can be used as well.

For more information on the HTTP REST API for collection management visit this
`page <https://docs.arangodb.com/HTTP/Collection>`__.

**Example:**

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.db('my_database')

    # List all available collections
    db.collections()

    # Create a new collection
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

