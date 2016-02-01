Task Management
---------------

ArangoDB can execute user-defined Javascript snippets as *one-shot* (run only
once without repeats) or *periodic* (re-scheduled after each execution) tasks.
The tasks are executed in the context of the database they are defined in. For
more information on the HTTP REST API for task management visit this
`page <https://docs.arangodb.com/HTTP/Tasks>`__.

.. note::
    When deleting a database, any tasks that were initialized under its context
    remain active. It is therefore advisable to un-register any running tasks
    before deleting the database.

.. note::
    Some operations in the example below require root privileges (i.e. the
    user must have access to the ``_system`` database).

**Examples:**

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.create_database('my_database')

    # Create a new task
    db.create_task(
        name='test_task',
        command='''
            var task = function(params){
                var db =require('@arangodb');
                db.print(params);
            }
            task(params);
        '''
        params={'foo': 'bar'}
        offset=300,
        period=10,
        task_id='001'
    )

    # List all active tasks
    db.tasks()

    # Retrieve information on a task by ID
    db.task('001')

    # Delete an existing task
    db.delete_task('001', ignore_missing=False)

Refer to the :ref:`Database` class for more details.
