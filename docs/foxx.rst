Foxx
----

Python-arango provides support for **Foxx**, a microservice framework which
lets you define custom HTTP endpoints to extend ArangoDB's REST API. For more
information, refer to `ArangoDB manual`_.

.. _ArangoDB manual: https://docs.arangodb.com

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "_system" database as root user.
    db = client.db('_system', username='root', password='passwd')

    # Get the Foxx API wrapper.
    foxx = db.foxx

    # Define the test mount point.
    service_mount = '/test_mount'

    # List services.
    foxx.services()

    # Create a service using source on server.
    foxx.create_service(
        mount=service_mount,
        source='/tests/static/service.zip',
        config={},
        dependencies={},
        development=True,
        setup=True,
        legacy=True
    )

    # Update (upgrade) a service.
    service = db.foxx.update_service(
        mount=service_mount,
        source='/tests/static/service.zip',
        config={},
        dependencies={},
        teardown=True,
        setup=True,
        legacy=False
    )

    # Replace (overwrite) a service.
    service = db.foxx.replace_service(
        mount=service_mount,
        source='/tests/static/service.zip',
        config={},
        dependencies={},
        teardown=True,
        setup=True,
        legacy=True,
        force=False
    )

    # Get service details.
    foxx.service(service_mount)

    # Manage service configuration.
    foxx.config(service_mount)
    foxx.update_config(service_mount, config={})
    foxx.replace_config(service_mount, config={})

    # Manage service dependencies.
    foxx.dependencies(service_mount)
    foxx.update_dependencies(service_mount, dependencies={})
    foxx.replace_dependencies(service_mount, dependencies={})

    # Toggle development mode for a service.
    foxx.enable_development(service_mount)
    foxx.disable_development(service_mount)

    # Other miscellaneous functions.
    foxx.readme(service_mount)
    foxx.swagger(service_mount)
    foxx.download(service_mount)
    foxx.commit(service_mount)
    foxx.scripts(service_mount)
    foxx.run_script(service_mount, 'setup', [])
    foxx.run_tests(service_mount, reporter='xunit', output_format='xml')

    # Delete a service.
    foxx.delete_service(service_mount)

You can also manage Foxx services by using zip or Javascript files directly:

.. code-block:: python

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "_system" database as root user.
    db = client.db('_system', username='root', password='passwd')

    # Get the Foxx API wrapper.
    foxx = db.foxx

    # Define the test mount point.
    service_mount = '/test_mount'

    # Create a service by providing a file directly.
    foxx.create_service_with_file(
        mount=service_mount,
        filename='/home/user/service.zip',
        development=True,
        setup=True,
        legacy=True
    )

    # Update (upgrade) a service by providing a file directly.
    foxx.update_service_with_file(
        mount=service_mount,
        filename='/home/user/service.zip',
        teardown=False,
        setup=True,
        legacy=True,
        force=False
    )

    # Replace a service by providing a file directly.
    foxx.replace_service_with_file(
        mount=service_mount,
        filename='/home/user/service.zip',
        teardown=False,
        setup=True,
        legacy=True,
        force=False
    )

    # Delete a service.
    foxx.delete_service(service_mount)

See :ref:`Foxx` for API specification.
