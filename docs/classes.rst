Class Specifications
--------------------

This page contains the specifications for all classes and methods available in
python-arango.

.. _ArangoClient:

ArangoClient
============

.. autoclass:: arango.client.ArangoClient
    :members:

.. _AsyncExecution:

AsyncExecution
==============

.. autoclass:: arango.async.AsyncExecution
    :members:
    :exclude-members: handle_request

.. _AsyncJob:

AsyncJob
========

.. autoclass:: arango.async.AsyncJob
    :members:

.. _AQL:

AQL
====

.. autoclass:: arango.aql.AQL
    :members:

.. _AQLQueryCache:

AQLQueryCache
=============

.. autoclass:: arango.aql.AQLQueryCache
    :members:

.. _BaseHTTPClient:

BaseHTTPClient
==============

.. autoclass:: arango.http_clients.base.BaseHTTPClient
    :members:


.. _BatchExecution:

BatchExecution
==============

.. autoclass:: arango.batch.BatchExecution
    :members:
    :exclude-members: handle_request

.. _BatchJob:

BatchJob
========

.. autoclass:: arango.batch.BatchJob
    :members:
    :exclude-members: update

.. _Cursor:

Cursor
======

.. autoclass:: arango.cursor.Cursor
    :members:

.. _Collection:

Collection
==========

.. autoclass:: arango.collections.Collection
    :inherited-members:
    :members:

.. _Database:

Database
========

.. autoclass:: arango.database.Database
    :members:

.. _EdgeCollection:

EdgeCollection
==============

.. autoclass:: arango.collections.EdgeCollection
    :inherited-members:
    :members:

.. _Graph:

Graph
=====

.. autoclass:: arango.graph.Graph
    :members:

.. _Response:

Response
========

.. autoclass:: arango.response.Response
    :members:

.. _Transaction:

Transaction
===========

.. autoclass:: arango.transaction.Transaction
    :members:
    :exclude-members: handle_request

.. _VertexCollection:

VertexCollection
================

.. autoclass:: arango.collections.VertexCollection
    :inherited-members:
    :members:

.. _WriteAheadLog:

WriteAheadLog
=============

.. autoclass:: arango.wal.WriteAheadLog
    :members:
