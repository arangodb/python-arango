Pregel
------

Python-arango provides support for **Pregel**, ArangoDB module for distributed
iterative graph processing. For more information, refer to `ArangoDB manual`_.

.. _ArangoDB manual: https://docs.arangodb.com

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Get the Pregel API wrapper.
    pregel = db.pregel

    # Start a new Pregel job in "school" graph.
    job_id = db.pregel.create_job(
        graph='school',
        algorithm='pagerank',
        store=False,
        max_gss=100,
        thread_count=1,
        async_mode=False,
        result_field='result',
        algorithm_params={'threshold': 0.000001}
    )

    # Retrieve details of a Pregel job by ID.
    job = pregel.job(job_id)

    # Delete a Pregel job by ID.
    pregel.delete_job(job_id)

See :ref:`Pregel` for API specification.
