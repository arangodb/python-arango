.. python-arango documentation master file, created by
   sphinx-quickstart on Sun Jul 24 17:17:48 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: /static/logo.png


Welcome to the documentation for **python-arango**, a Python driver for
`ArangoDB's REST API <https://www.arangodb.com/>`__.

Features
========

- Clean, Pythonic interface
- Lightweight
- 95%+ API coverage

Compatibility
=============

- Tested with Python versions 2.7.x, 3.4.x and 3.5.x
- Latest version of python-arango (3.x) works with ArangoDB 3.x only
- Older versions of python-arango (2.x) work with ArangoDB 2.x only

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


Contents
========

.. toctree::
    :maxdepth: 1

    client
    database
    collection
    index
    document
    graph
    aql
    cursor
    async
    batch
    transaction
    admin
    user
    task
    wal
    errors
    classes
