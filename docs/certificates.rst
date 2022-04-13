TLS certificate verification
----------------------------

When connecting against a server using an https/TLS connection, TLS certificates
are verified by default.
By default, self-signed certificates will cause trouble when connecting.

.. code-block:: python

    client = ArangoClient(hosts="https://localhost:8529")

In order to make connections work even when using self-signed certificates, the
`verify_certificates` option can be disabled when creating the `ArangoClient`
instance:

.. code-block:: python

    client = ArangoClient(hosts="https://localhost:8529", verify_certificate=False)

This will allow connecting, but the underlying `urllib3` library may still issue
warnings due to the insecurity of using self-signed certificates.

To turn off these warnings as well, you can add the following code to your client
application:

.. code-block:: python

    import requests
    requests.packages.urllib3.disable_warnings() 

