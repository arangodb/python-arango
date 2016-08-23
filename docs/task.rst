.. _task-page:

Task Management
---------------

ArangoDB can execute user-defined Javascript snippets as one-shot (runs only
once without repeats) or periodic (re-scheduled after each execution) tasks.
The tasks are executed in the context of the database they are defined in.

.. note::
    When deleting a database, any tasks that were initialized under its context
    remain active. It is therefore advisable to delete any running tasks before
    deleting the database.

Example:

.. code-block:: python

    from arango import ArangoClient

    client = ArangoClient()
    db = client.db('my_database')

    # Create a new task
    db.create_task(
        name='test_task',
        command='''
            var task = function(params){
                var db = require('@arangodb');
                db.print(params);
            }
            task(params);
        ''',
        params={'foo': 'bar'},
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

Refer to :ref:`Database` class for more details.
