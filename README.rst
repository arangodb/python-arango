.. image:: https://cloud.githubusercontent.com/assets/2701938/18018900/668e15d2-6ba7-11e6-85a9-7997b3c6218a.png

|

.. image:: https://travis-ci.org/joowani/python-arango.svg?branch=master
    :target: https://travis-ci.org/joowani/python-arango
    :alt: Travis Build Status

.. image:: https://readthedocs.org/projects/python-driver-for-arangodb/badge/?version=master
    :target: http://python-driver-for-arangodb.readthedocs.io/en/master/?badge=master
    :alt: Documentation Status

.. image:: https://badge.fury.io/py/python-arango.svg
    :target: https://badge.fury.io/py/python-arango
    :alt: Package Version

.. image:: https://img.shields.io/badge/python-2.7%2C%203.4%2C%203.5%2C%203.6-blue.svg
    :target: https://github.com/joowani/python-arango
    :alt: Python Versions

.. image:: https://coveralls.io/repos/github/joowani/python-arango/badge.svg?branch=master
    :target: https://coveralls.io/github/joowani/python-arango?branch=master
    :alt: Test Coverage

.. image:: https://img.shields.io/github/issues/joowani/python-arango.svg   
    :target: https://github.com/joowani/python-arango/issues
    :alt: Issues Open

.. image:: https://img.shields.io/badge/license-MIT-blue.svg   
    :target: https://raw.githubusercontent.com/joowani/python-arango/master/LICENSE
    :alt: MIT License

|

Welcome to the GitHub page for **python-arango**, a Python driver for ArangoDB_.

Announcements
=============

- Python-arango version `4.0.0`_ is now out!
- Please see the releases_ page for details on latest updates.

Features
========

- Clean Pythonic interface
- Lightweight
- High ArangoDB REST API coverage

Compatibility
=============

- Python versions 2.7, 3.4, 3.5 and 3.6 are supported
- Python-arango 4.x supports ArangoDB 3.3+ (recommended)
- Python-arango 3.x supports ArangoDB 3.0 ~ 3.2 only
- Python-arango 2.x supports ArangoDB 1.x ~ 2.x only

Installation
============

To install a stable version from PyPi_:

.. code-block:: bash

    ~$ pip install python-arango


To install the latest version directly from GitHub_:

.. code-block:: bash

    ~$ pip install -e git+git@github.com:joowani/python-arango.git@master#egg=python-arango

You may need to use ``sudo`` depending on your environment.

Getting Started
===============

Here is a simple usage example:

.. code-block:: python

    from arango import ArangoClient

    # Initialize the client for ArangoDB.
    client = ArangoClient(protocol='http', host='localhost', port=8529)

    # Connect to "_system" database as root user.
    sys_db = client.db('_system', username='root', password='passwd')

    # Create a new database named "test".
    sys_db.create_database('test')

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Create a new collection named "students".
    students = db.create_collection('students')

    # Add a hash index to the collection.
    students.add_hash_index(fields=['name'], unique=True)

    # Insert new documents into the collection.
    students.insert({'name': 'jane', 'age': 39})
    students.insert({'name': 'josh', 'age': 18})
    students.insert({'name': 'judy', 'age': 21})

    # Execute an AQL query and iterate through the result cursor.
    cursor = db.aql.execute('FOR doc IN students RETURN doc')
    student_names = [document['name'] for document in cursor]


Here is another example with graphs:

.. code-block:: python

    from arango import ArangoClient

    # Initialize the client for ArangoDB.
    client = ArangoClient(protocol='http', host='localhost', port=8529)

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Create a new graph named "school".
    graph = db.create_graph('school')

    # Create vertex collections for the graph.
    students = graph.create_vertex_collection('students')
    lectures = graph.create_vertex_collection('lectures')

    # Create an edge definition (relation) for the graph.
    register = graph.create_edge_definition(
        edge_collection='register',
        from_vertex_collections=['students'],
        to_vertex_collections=['lectures']
    )

    # Insert vertex documents into "students" (from) vertex collection.
    students.insert({'_key': '01', 'full_name': 'Anna Smith'})
    students.insert({'_key': '02', 'full_name': 'Jake Clark'})
    students.insert({'_key': '03', 'full_name': 'Lisa Jones'})

    # Insert vertex documents into "lectures" (to) vertex collection.
    lectures.insert({'_key': 'MAT101', 'title': 'Calculus'})
    lectures.insert({'_key': 'STA101', 'title': 'Statistics'})
    lectures.insert({'_key': 'CSC101', 'title': 'Algorithms'})

    # Insert edge documents into "register" edge collection.
    register.insert({'_from': 'students/01', '_to': 'lectures/MAT101'})
    register.insert({'_from': 'students/01', '_to': 'lectures/STA101'})
    register.insert({'_from': 'students/01', '_to': 'lectures/CSC101'})
    register.insert({'_from': 'students/02', '_to': 'lectures/MAT101'})
    register.insert({'_from': 'students/02', '_to': 'lectures/STA101'})
    register.insert({'_from': 'students/03', '_to': 'lectures/CSC101'})

    # Traverse the graph in outbound direction, breadth-first.
    result = graph.traverse(
        start_vertex='students/01',
        direction='outbound',
        strategy='breadthfirst'
    )

Check out the documentation_ for more details.

Contributing
============

Please take a look at this page_ before submitting a pull request. Thanks!

.. _ArangoDB: https://www.arangodb.com
.. _4.0.0: https://github.com/joowani/python-arango/releases/tag/4.0.0
.. _releases: https://github.com/joowani/python-arango/releases
.. _PyPi: https://pypi.python.org/pypi/python-arango
.. _GitHub: https://github.com/joowani/python-arango
.. _documentation:
    http://python-driver-for-arangodb.readthedocs.io/en/master/index.html
.. _page:
    http://python-driver-for-arangodb.readthedocs.io/en/master/contributing.html