.. _pregel-page:

Pregel
------

**Python-arango** provides APIs for distributed iterative graph processing
(Pregel). For more information, please refer to the ArangoDB manual
`here <https://docs.arangodb.com/Manual/Graphs/Pregel/>`__.

Here is an example showing how Pregel jobs can be started, fetched or cancelled:

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.db('my_database')
    db.create_graph('my_graph')

    # Create and start a new Pregel job
    job_id = db.create_pregel_job(algorithm='pagerank', graph='my_graph')

    # Get the details of a Pregel job by its ID
    job = db.pregel_job(job_id)
    print(job['aggregators'])
    print(job['edge_count'])
    print(job['gss'])
    print(job['received_count'])
    print(job['send_count'])
    print(job['state'])
    print(job['total_runtime'])
    print(job['vertex_count'])

    # Delete/cancel a Pregel job by its ID
    db.delete_pregel_job(job_id)

Refer to class :class:`arango.database.Database` for more details on the methods
for Pregel jobs.
