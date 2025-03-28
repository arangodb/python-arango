.. image:: /static/logo.png

|

Python-Arango
-------------

Welcome to the documentation for **python-arango**, a Python driver for ArangoDB_.

If you're interested in using asyncio, please check python-arango-async_ driver.

Requirements
=============

- ArangoDB version 3.11+
- Python version 3.9+

Installation
============

.. code-block:: bash

    ~$ pip install python-arango --upgrade

Contents
========

Basics

.. toctree::
    :maxdepth: 1

    overview
    database
    collection
    indexes
    document
    graph
    simple
    aql

Specialized Features

.. toctree::
    :maxdepth: 1

    pregel
    foxx
    replication
    transaction
    cluster
    analyzer
    view
    wal

API Executions

.. toctree::
    :maxdepth: 1

    async
    batch
    overload

Administration

.. toctree::
    :maxdepth: 1

    admin
    user

Miscellaneous

.. toctree::
    :maxdepth: 1

    task
    threading
    certificates
    errors
    logging
    auth
    http
    compression
    serializer
    schema
    cursor
    backup
    errno

Development

.. toctree::
    :maxdepth: 1

    contributing
    specs

.. _ArangoDB: https://www.arangodb.com
.. _python-arango-async: https://python-arango-async.readthedocs.io
