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
You can use this option to disable verification.

.. code-block:: python

    client = ArangoClient(hosts="https://localhost:8529", verify_override=False)

This will allow connecting, but the underlying `urllib3` library may still issue
warnings due to the insecurity of using self-signed certificates.

To turn off these warnings as well, you can add the following code to your client
application:

.. code-block:: python

    import requests
    requests.packages.urllib3.disable_warnings()

You can also provide a custom CA bundle without defining a custom HTTP Client:

.. code-block:: python

    client = ArangoClient(hosts="https://localhost:8529", verify_override="path/to/certfile")

If `verify_override` is set to a path to a directory, the directory must have been processed using the `c_rehash` utility
supplied with OpenSSL. For more information, see the `requests documentation <https://requests.readthedocs.io/en/master/user/advanced/#ssl-cert-verification>`_.

Setting `verify_override` to `True` will use the system's default CA bundle.

.. code-block:: python

    client = ArangoClient(hosts="https://localhost:8529", verify_override=True)
