.. _document-page:

Documents
---------

**Documents** in python-arango are Python dictionaries. They can be nested to
an arbitrary depth and contain lists. Each document must have the ``"_key"``
field, whose value identifies the document uniquely within a collection. There
is also the ``"_id"`` field, whose value identifies the document uniquely across
*all* collections within a database.

ArangoDB supports MVCC (Multiple Version Concurrency Control) and is capable
of storing each document in multiple revisions. The revision of a document is
distinguished by the value of the ``"_rev"`` field. For more information on
documents and their associated terminologies visit this
`page <https://docs.arangodb.com/HTTP/Document/AddressAndEtag.html>`__.

Here is an example of a valid document:

.. code-block:: python

    {
        '_id': 'students/john',
        '_key': 'john',
        '_rev': '14253647',
        'first_name': 'John',
        'last_name': 'Doe',
        'address': {
            'city': 'Gotham',
            'zip': 'M1NS93',
            'street' : '300 Beverly St.'
        },
        'courses': ['CSC101', 'STA101']
    }

.. _edge-documents:

**Edge documents** or **edges** are similar to documents but with additional
required fields ``"_from"`` and ``"_to"``. The values of these fields are the
values of the ``"_id"`` field of the "from" and "to" vertex documents (see
:ref:`graphs <graph-page>` for more details). Edge documents are contained in
:ref:`edge collections <edge-collections>`.

Here is an example of a valid edge document:

.. code-block:: python

    {
        '_id': 'knows/001',
        '_key': '001',
        '_rev': '23891346',
        '_from': 'students/john',
        '_to': 'students/jane',
        'friends': True,
        'family': False
    }


Here is an example showing how documents can be managed:

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.db('my_database')
    students = db.collection('students')

    lola = {'_key': 'lola', 'GPA': 3.5, 'first': 'Lola', 'last': 'Martin'}
    abby = {'_key': 'abby', 'GPA': 3.2, 'first': 'Abby', 'last': 'Page'}
    john = {'_key': 'john', 'GPA': 3.6, 'first': 'John', 'last': 'Kim'}
    emma = {'_key': 'emma', 'GPA': 4.0, 'first': 'Emma', 'last': 'Park'}

    # Insert a new document
    result = students.insert(lola)
    print(result['_id'], result['_key'], result['_rev'])

    # Retrieve document information
    students.has('lola') and 'john' in students
    students.count()
    len(students) > 5

    # Insert multiple documents in bulk
    students.import_bulk([abby, john, emma])

    # Retrieve one or more matching documents
    for student in students.find({'first': 'John'}):
        print(student['_key'], student['GPA'])

    # Retrieve a single document
    students.get('john')

    # Retrieve multiple documents
    students.get_many(['abby', 'lola'])

    # Update a single document
    lola['GPA'] = 2.6
    students.update(lola)

    # Update one or more matching documents
    students.update_match({'last': 'Park'}, {'GPA': 3.0})

    # Replace documents by filters
    becky = {'first': 'Becky', 'last': 'Solis', 'GPA': '3.3'}
    students.replace_match({'first': 'Emma'}, becky)

    # Replace a single document
    emma['GPA'] = 3.1
    students.replace(emma)

    # Iterate through all documents and update
    for student in students:
        student['GPA'] = 4.0
        student['happy'] = True
        students.update(student)

Refer to :ref:`Collection` class for more details on the operations shown
above.
