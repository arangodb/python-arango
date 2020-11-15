Schema Validation
-----------------

ArangoDB supports document validation using JSON schemas. You can use this
feature by providing a schema during collection creation using the ``schema``
parameter.

**Example:**

.. testcode::

    from arango import ArangoClient

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    if db.has_collection('employees'):
        db.delete_collection('employees')

    # Create a new collection named "employees" with custom schema.
    my_schema = {
        'rule': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'email': {'type': 'string'}
            },
            'required': ['name', 'email']
        },
        'level': 'moderate',
        'message': 'Schema Validation Failed.'
    }
    employees = db.create_collection(name='employees', schema=my_schema)

    # Modify the schema.
    employees.configure(schema=my_schema)

    # Remove the schema.
    employees.configure(schema={})
