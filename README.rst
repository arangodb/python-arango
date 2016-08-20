.. image:: https://cloud.githubusercontent.com/assets/2701938/17761717/892d37c0-64d7-11e6-84a8-665adc9f4cfc.png

.. image:: https://travis-ci.org/joowani/python-arango.svg?branch=master
    :target: https://travis-ci.org/joowani/python-arango
    :alt: Travis Build Status

.. image:: https://readthedocs.org/projects/python-driver-for-arangodb/badge/?version=master
    :target: http://python-driver-for-arangodb.readthedocs.io/en/master/?badge=master
    :alt: Documentation Status

.. image:: https://badge.fury.io/py/python-arango.svg
    :target: https://badge.fury.io/py/python-arango
    :alt: Package Version

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
`ArangoDB's REST API <https://www.arangodb.com/>`__.

Features
========

- Clean, Pythonic interface
- Lightweight
- 95%+ API coverage

Compatibility
=============

- Python versions 2.7.x, 3.4.x and 3.5.x are supported
- Latest version of python-arango (3.x) supports ArangoDB 3.x only
- Older versions of python-arango (2.x) support ArangoDB 2.x only

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

You may need to use ``sudo`` depending on your environment.

.. _PyPi: https://pypi.python.org/pypi/python-arango
.. _GitHub: https://github.com/joowani/python-arango

Getting Started
===============

Here is simple usage example:

.. code-block:: python

    from arango import ArangoClient

    # Initialize the client for ArangoDB
    client = ArangoClient(
        protocol='http',
        host="localhost",
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
    students.insert({'name': 'josh', 'age': 13})
    students.insert({'name': 'jake', 'age': 21})

    # Execute an AQL query and iterate through the result cursor
    cursor = db.aql.execute('FOR s IN students RETURN s')
    print(student['name'] for student in cursor)

Please read the full `API documentation`_ for more details!

.. _API documentation:
    http://python-driver-for-arangodb.readthedocs.io/en/master/intro.html
