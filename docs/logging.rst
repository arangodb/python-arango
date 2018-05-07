Logging
-------

In order to see full HTTP request response details, you can modify logger
settings for Requests_ library, which python-arango uses under the hood:

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

.. note::
    If python-arango's default HTTP client is overridden with a custom one,
    the code snippet above may not work as expected.

Alternatively, if you want to use your own loggers, see :doc:`http` for an
example.
