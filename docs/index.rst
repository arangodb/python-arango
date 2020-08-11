.. image:: /static/logo.png

|

Welcome to the documentation for **python-arango**, a Python driver for ArangoDB_.

Compatibility
=============

- Python versions 3.5+ are supported
- Python-arango 6.x supports ArangoDB 3.7+
- Python-arango 5.x supports ArangoDB 3.5 ~ 3.6
- Python-arango 4.x supports ArangoDB 3.3 ~ 3.4
- Python-arango 3.x supports ArangoDB 3.0 ~ 3.2
- Python-arango 2.x supports ArangoDB 1.x ~ 2.x

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
    simple
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
    auth
    http
    replication
    cluster
    serializer
    backup
    errno
    contributing
    specs
