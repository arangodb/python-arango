.. _multithreading-page:

Multithreading
--------------


Notes on Eventlet
=================

**Python-arango** should be compatible with eventlet_ *for the most part*.
By default, **python-arango** makes API calls to ArangoDB using the requests_
library which can be monkeypatched:

.. code-block:: python

    import eventlet
    requests = eventlet.import_patched("requests")

.. _requests: https://github.com/requests/requests
.. _eventlet: http://eventlet.net

Assuming the requests library is used and monkeypatched properly, all
python-arango APIs except :ref:`Batch Execution <batch-page>` and
:ref:`Async Execution <async-page>` should be thread-safe.
