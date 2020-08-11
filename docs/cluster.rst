Clusters
--------

Python-arango provides APIs for working with ArangoDB clusters. For more
information on the design and architecture, refer to `ArangoDB manual`_.

.. _ArangoDB manual: https://docs.arangodb.com

Coordinators
============

To connect to multiple ArangoDB coordinators, you must provide either a list of
host strings or a comma-separated string during client initialization.

**Example:**

.. testcode::

    from arango import ArangoClient

    # Single host
    client = ArangoClient(hosts='http://localhost:8529')

    # Multiple hosts (option 1: list)
    client = ArangoClient(hosts=['http://host1:8529', 'http://host2:8529'])

    # Multiple hosts (option 2: comma-separated string)
    client = ArangoClient(hosts='http://host1:8529,http://host2:8529')

By default, a `requests.Session`_ instance is created per coordinator. HTTP
requests to a host are sent using only its corresponding session. For more
information on how to override this behaviour, see :doc:`http`.

.. _requests.Session: http://docs.python-requests.org/en/master/user/advanced/#session-objects

Load-Balancing Strategies
=========================

There are two load-balancing strategies available: "roundrobin" and "random"
(defaults to "roundrobin" if unspecified).

**Example:**

.. testcode::

    from arango import ArangoClient

    hosts = ['http://host1:8529', 'http://host2:8529']

    # Round-robin
    client = ArangoClient(hosts=hosts, host_resolver='roundrobin')

    # Random
    client = ArangoClient(hosts=hosts, host_resolver='random')

Administration
==============

Below is an example on how to manage clusters using python-arango.

.. code-block:: python

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "_system" database as root user.
    sys_db = client.db('_system', username='root', password='passwd')

    # Get the Cluster API wrapper.
    cluster = sys_db.cluster

    # Get this server's ID.
    cluster.server_id()

    # Get this server's role.
    cluster.server_role()

    # Get the cluster health.
    cluster.health()

    # Get cluster server details.
    cluster.server_count()
    server_id = cluster.server_id()
    cluster.server_engine(server_id)
    cluster.server_version(server_id)
    cluster.server_statistics(server_id)

    # Toggle maintenance mode (allowed values are "on" and "off").
    cluster.toggle_maintenance_mode('on')
    cluster.toggle_maintenance_mode('off')

See :ref:`ArangoClient` and :ref:`Cluster` for API specification.
