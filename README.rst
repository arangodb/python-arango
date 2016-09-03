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

.. image:: https://img.shields.io/badge/python-2.7%2C%203.4%2C%203.5-blue.svg
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

Welcome to the GitHub page for **python-arango**, a Python driver for
`ArangoDB <https://www.arangodb.com/>`__.

Features
========

- Clean, Pythonic interface
- Lightweight
- 95%+ ArangoDB REST API coverage

Compatibility
=============

- Python versions 2.7.x, 3.4.x and 3.5.x are supported
- Latest version of python-arango (3.x) supports ArangoDB 3.x only
- Older versions of python-arango support ArangoDB 1.x ~ 2.x only

Installation
============

To install a stable version from PyPi_:

.. code-block:: bash

    pip install python-arango


To install the latest version directly from GitHub_:

.. code-block:: bash

    git clone https://github.com/joowani/python-arango.git
    cd python-arango
    python setup.py install

You may need to use ``sudo`` depending on your environment setup.

.. _PyPi: https://pypi.python.org/pypi/python-arango
.. _GitHub: https://github.com/joowani/python-arango

Getting Started
===============

Here is a simple usage example:

.. code-block:: python

    from arango import ArangoClient

    # Initialize the client for ArangoDB
    client = ArangoClient(
        protocol='http',
        host='localhost',
        port=8529,
        username='root',
        password='',
        enable_logging=True
    )

    # Create a new database named "my_database"
    db = client.create_database('my_database')

    # Create a new collection named "students"
    students = db.create_collection('students')

    # Add a hash index to the collection
    students.add_hash_index(fields=['name'], unique=True)

    # Insert new documents into the collection
    students.insert({'name': 'jane', 'age': 19})
    students.insert({'name': 'josh', 'age': 18})
    students.insert({'name': 'jake', 'age': 21})

    # Execute an AQL query
    result = db.aql.execute('FOR s IN students RETURN s')
    print([student['name'] for student in result])


Here is another example involving graphs:

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()

    # Create a new graph
    graph = client.db('my_database').create_graph('my_graph')
    students = graph.create_vertex_collection('students')
    courses = graph.create_vertex_collection('courses')
    takes = graph.create_edge_definition(
        name='takes',
        from_collections=['students'],
        to_collections=['courses']
    )

    # Insert vertices
    students.insert({'_key': '01', 'full_name': 'Anna Smith'})
    students.insert({'_key': '02', 'full_name': 'Jake Clark'})
    students.insert({'_key': '03', 'full_name': 'Lisa Jones'})

    courses.insert({'_key': 'MAT101', 'title': 'Calculus'})
    courses.insert({'_key': 'STA101', 'title': 'Statistics'})
    courses.insert({'_key': 'CSC101', 'title': 'Algorithms'})

    # Insert edges
    takes.insert({'_from': 'students/01', '_to': 'courses/MAT101'})
    takes.insert({'_from': 'students/01', '_to': 'courses/STA101'})
    takes.insert({'_from': 'students/01', '_to': 'courses/CSC101'})
    takes.insert({'_from': 'students/02', '_to': 'courses/MAT101'})
    takes.insert({'_from': 'students/02', '_to': 'courses/STA101'})
    takes.insert({'_from': 'students/03', '_to': 'courses/CSC101'})

    # Traverse the graph in outbound direction, breath-first
    traversal_results = graph.traverse(
        start_vertex='students/01',
        strategy='bfs',
        direction='outbound'
    )
    print(traversal_results['vertices'])

Please read the full `API documentation`_ for more details!

.. _API documentation:
    http://python-driver-for-arangodb.readthedocs.io/en/master/intro.html
