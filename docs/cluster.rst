Clusters
--------

Python-arango provides support for ArangoDB clusters. For more information on
clusters, refer to `ArangoDB manual`_.

.. _ArangoDB manual: https://docs.arangodb.com

Coordinators
============

To connect to multiple ArangoDB hosts (e.g. coordinators) you must provide
either a list of host strings or a comma-separated string during client
initialization.

**Example:**

.. testcode::

    from arango import ArangoClient

    # Single instance
    client = ArangoClient(hosts='http://localhost:8529')

    # Multiple instances (option 1: list)
    client = ArangoClient(hosts=['http://host1:8529', 'http://host2:8529'])

    # Multiple instances (option 2: comma-separated string)
    client = ArangoClient(hosts='http://host1:8529,http://host2:8529')

Load-Balancing
==============

There are two load-balancing strategies available: "roundrobin" and "random"
(defaults to "roundrobin" if not specified).

**Example:**

.. testcode::

    from arango import ArangoClient

    hosts = ['http://host1:8529', 'http://host2:8529']

    # Round-robin
    client = ArangoClient(hosts=hosts, host_resolver='roundrobin')

    # Random
    client = ArangoClient(hosts=hosts, host_resolver='random')

See :ref:`ArangoClient` for API specification.
