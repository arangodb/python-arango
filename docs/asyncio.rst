.. _asyncio-page:

Using Asyncio HTTP Client
-------------------------

If you are using **python-arango** with Python 3.5+, you can use aiohttp_
based HTTP client :class:`arango.http_clients.AsyncioHTTPClient`:

.. code-block:: python

    from arango import ArangoClient
    from arango.http_clients import AsyncioHTTPClient

    arango_client = ArangoClient(
        http_client=AsyncioHTTPClient()
    )

.. _aiohttp: https://aiohttp.readthedocs.io