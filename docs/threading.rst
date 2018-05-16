Threading
---------

Instances of the following classes are considered *stateful*, and should not be
shared across multiple threads without locks in place:

* :ref:`BatchDatabase` (see :doc:`batch`)
* :ref:`BatchJob` (see :doc:`batch`)
* :ref:`Cursor` (see :doc:`cursor`)
* :ref:`TransactionDatabase` (see :doc:`transaction`)
* :ref:`TransactionJob` (see :doc:`transaction`)

The rest of python-arango is safe to use in multi-threaded environments.
