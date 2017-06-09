.. _logging-page:

Logging
-------

By default, :class:`arango.client.ArangoClient` records API call history using
the ``arango`` logger at ``logging.DEBUG`` level.

Here is an example showing how the logger can be enabled and customized:

.. code-block:: python

    import logging

    from arango import ArangoClient

    logger = logging.getLogger('arango')

    # Set the logging level
    logger.setLevel(logging.DEBUG)

    # Attach a handler
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Initialize and use the client to see the changes
    client = ArangoClient(
        username='root',
        password='',
        enable_logging=True
    )
    client.databases()
    client.endpoints()
    client.log_levels()


The logging output for above would look something like this:

.. code-block:: bash

    [DEBUG] GET http://127.0.0.1:8529/_db/_system/_api/database 200
    [DEBUG] GET http://127.0.0.1:8529/_db/_system/_api/endpoint 200
    [DEBUG] GET http://127.0.0.1:8529/_db/_system/_admin/log/level 200


In order to see the full request information, turn on logging for the requests_
library which **python-arango** uses under the hood:

.. _requests: https://github.com/kennethreitz/requests

.. code-block:: python

    import requests
    import logging

    try: # for Python 3
        from http.client import HTTPConnection
    except ImportError:
        from httplib import HTTPConnection
    HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
