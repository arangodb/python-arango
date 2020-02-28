.. image:: /static/logo.png

|

Welcome to the documentation for **python-arango**, a Python driver for ArangoDB_.


Features
========

- Pythonic interface
- Lightweight
- High API coverage

Compatibility
=============

- Python versions 2.7, 3.5, 3.6 and 3.7 are supported
- Python-arango 5.x supports ArangoDB 3.5+
- Python-arango 4.x supports ArangoDB 3.3 ~ 3.4 only
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

.. _ArangoDB: https://www.arangodb.com
.. _PyPi: https://pypi.python.org/pypi/python-arango
.. _GitHub: https://github.com/joowani/python-arango


Contents
========

.. toctree::
    :maxdepth: 1

    overview
    database
    collection
    document
    indexes
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
    pregel
    foxx
    view
    analyzer
    threading
    errors
    logging
    http
    replication
    cluster
    serializer
    errno
    contributing
    specs
