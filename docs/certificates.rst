TLS certificate verification
----------------------------

When connecting against a server using an https/TLS connection, TLS certificates
are verified by default.
By default, self-signed certificates will cause trouble when connecting.

.. code-block:: python

    client = ArangoClient(hosts="https://localhost:8529")

To make connections work even when using self-signed certificates, you can
provide the certificate CA bundle or turn the verification off.

If you want to have fine-grained control over the HTTP connection, you should define
your HTTP client as described in the :ref:`HTTPClients` section.

The ``ArangoClient`` class provides an option to override the verification behavior,
no matter what has been defined in the underlying HTTP session.
You can use this option to disable verification or provide a custom CA bundle without
defining a custom HTTP Client.

.. code-block:: python

    client = ArangoClient(hosts="https://localhost:8529", verify_override=False)

This will allow connecting, but the underlying `urllib3` library may still issue
warnings due to the insecurity of using self-signed certificates.

To turn off these warnings as well, you can add the following code to your client
application:

.. code-block:: python

    import requests
    requests.packages.urllib3.disable_warnings()
