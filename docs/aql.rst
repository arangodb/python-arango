.. _aql-page:

AQL
----

**ArangoDB AQL Language (AQL)** is used to retrieve and modify data stored in
ArangoDB. AQL is similar to SQL for relational databases but without the
support for data-definition operations such as creating or deleting
:ref:`databases <database-page>`, :ref:`collections <collection-page>` and
:ref:`indexes <index-page>` etc. For more general information on AQL visit this
`page <https://docs.arangodb.com/AQL>`__.

AQL Queries
===========

**AQL queries** can be invoked using the :ref:`AQL` class, which returns
instances of :ref:`Cursor`. For more information on AQL syntax visit this
`page <https://docs.arangodb.com/AQL/Fundamentals/Syntax.html>`__.

Here is an example showing how AQL queries can be executed:

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.db('my_database')

    # Set up some test data to query against
    db.collection('students').insert_many([
        {'_key': 'Abby', 'age': 22},
        {'_key': 'John', 'age': 18},
        {'_key': 'Mary', 'age': 21}
    ])

    # Retrieve the execution plan without running the query
    db.aql.explain('FOR s IN students RETURN s')

    # Validate the query without executing it
    db.aql.validate('FOR s IN students RETURN s')

    # Execute the query
    cursor = db.aql.execute(
      'FOR s IN students FILTER s.age < @value RETURN s',
      bind_vars={'value': 19}
    )
    # Iterate through the result cursor
    print([student['_key'] for student in cursor])


AQL User Functions
==================

**AQL user functions** are custom functions defined by the users to extend the
functionality of AQL. Although python-arango provides ways to add, delete and
retrieve user functions in Python, the functions themselves must be defined in
Javascript. For more general information on AQL user functions visit this
`page <https://docs.arangodb.com/AQL/Extending>`__.

Here is an example showing how AQL functions can be created or deleted:

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.db('my_database')

    # Create a new AQL user function
    db.aql.create_function(
        name='functions::temperature::converter',
        code='function (celsius) { return celsius * 1.8 + 32; }'
    )
    # List all available AQL user functions
    db.aql.functions()

    # Delete an existing AQL user function
    db.aql.delete_function('functions::temperature::converter')

Refer to :ref:`AQL` class for more details.


AQL Query Cache
===============

**AQL query cache** minimizes redundant calculation of the same query results.
If it useful when read queries are called frequently and write queries are not.
For more general information on AQL query caches visit this
`page <https://docs.arangodb.com/AQL/ExecutionAndPerformance/QueryCache.html>`__.

Here is an example showing how the AQL query cache can be used:

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.db('my_database')

    # Configure the AQL query cache properties
    db.aql.cache.configure(mode='demand', limit=10000)

    # Retrieve the AQL query cache properties
    db.aql.cache.properties()

    # Clear the AQL query cache
    db.aql.cache.clear()

Refer to :ref:`AQLQueryCache` class for more details.
