Logging
-------

To see full HTTP request and response details, you can modify the logger
settings for the Requests_ library, which python-arango uses under the hood:

.. _Requests: https://github.com/requests/requests

.. code-block:: python

    import requests
    import logging

    try:
        # For Python 3
        from http.client import HTTPConnection
    except ImportError:
        # For Python 2
        from httplib import HTTPConnection
    HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

If python-arango's default HTTP client is overridden, the code snippet above
may not work as expected. See :doc:`http` for more information.
