.. _HTTPClients:

HTTP Clients
------------

Python-arango lets you define your own HTTP client for sending requests to
ArangoDB server. The default implementation uses the requests_ library.

Your HTTP client must inherit :class:`arango.http.HTTPClient` and implement the
following abstract methods:

* :func:`arango.http.HTTPClient.create_session`
* :func:`arango.http.HTTPClient.send_request`

The **create_session** method must return a `requests.Session`_ instance per
connected host (coordinator). The session objects are stored in the client.

The **send_request** method must use the session to send an HTTP request, and
return a fully populated instance of :class:`arango.response.Response`.

For example, let's say your HTTP client needs:

* Automatic retries
* Additional HTTP header called ``x-my-header``
* SSL certificate verification disabled
* Custom logging

Your ``CustomHTTPClient`` class might look something like this:

.. testcode::

    import logging

    from requests.adapters import HTTPAdapter
    from requests import Session
    from requests.packages.urllib3.util.retry import Retry

    from arango.response import Response
    from arango.http import HTTPClient


    class CustomHTTPClient(HTTPClient):
        """My custom HTTP client with cool features."""

        def __init__(self):
            # Initialize your logger.
            self._logger = logging.getLogger('my_logger')

        def create_session(self, host):
            session = Session()

            # Add request header.
            session.headers.update({'x-my-header': 'true'})

            # Enable retries.
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "OPTIONS"],
            )
            http_adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount('https://', http_adapter)
            session.mount('http://', http_adapter)

            return session

        def send_request(self,
                         session,
                         method,
                         url,
                         params=None,
                         data=None,
                         headers=None,
                         auth=None):
            # Add your own debug statement.
            self._logger.debug(f'Sending request to {url}')

            # Send a request.
            response = session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                headers=headers,
                auth=auth,
                verify=False,  # Disable SSL verification
                timeout=5      # Use timeout of 5 seconds
            )
            self._logger.debug(f'Got {response.status_code}')

            # Return an instance of arango.response.Response.
            return Response(
                method=response.request.method,
                url=response.url,
                headers=response.headers,
                status_code=response.status_code,
                status_text=response.reason,
                raw_body=response.text,
            )

Then you would inject your client as follows:

.. code-block:: python

    from arango import ArangoClient

    from my_module import CustomHTTPClient

    client = ArangoClient(
        hosts='http://localhost:8529',
        http_client=CustomHTTPClient()
    )

See `requests.Session`_ for more details on how to create and manage sessions.

.. _requests: https://github.com/requests/requests
.. _requests.Session: http://docs.python-requests.org/en/master/user/advanced/#session-objects
