Compression
------------

The :ref:`ArangoClient` lets you define the preferred compression policy for request and responses. By default
compression is disabled. You can change this by setting the `request_compression` and `response_compression` parameters
when creating the client. Currently, only the "deflate" compression algorithm is supported.

.. testcode::

    from arango import ArangoClient

    from arango.http import DeflateRequestCompression

    client = ArangoClient(
        hosts='http://localhost:8529',
        request_compression=DeflateRequestCompression(),
        response_compression="deflate"
    )

Furthermore, you can customize the request compression policy by defining the minimum size of the request body that
should be compressed and the desired compression level. For example, the following code sets the minimum size to 2 KB
and the compression level to 8:

.. code-block:: python

    client = ArangoClient(
        hosts='http://localhost:8529',
        request_compression=DeflateRequestCompression(
            threshold=2048,
            level=8),
    )

If you want to implement your own compression policy, you can do so by implementing the
:class:`arango.http.RequestCompression` interface.

.. note::
    The `response_compression` parameter is only used to inform the server that the client prefers compressed responses
    (in the form of an *Accept-Encoding* header). Note that the server may or may not honor this preference, depending
    on how it is configured. This can be controlled by setting the `--http.compress-response-threshold` option to
    a value greater than 0 when starting the ArangoDB server.
