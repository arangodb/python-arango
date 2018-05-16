from __future__ import absolute_import, unicode_literals

from six import string_types

from arango.exceptions import (
    TaskCreateError,
    TaskDeleteError,
    TaskGetError,
    TaskListError
)
from tests.helpers import (
    assert_raises,
    extract,
    generate_task_id,
    generate_task_name,
)


def test_task_management(db, bad_db):
    test_command = 'require("@arangodb").print(params);'

    # Test create task with random ID
    task_name = generate_task_name()
    new_task = db.create_task(
        name=task_name,
        command=test_command,
        params={'foo': 1, 'bar': 2},
        offset=1,
    )
    assert new_task['name'] == task_name
    assert 'print(params)' in new_task['command']
    assert new_task['type'] == 'timed'
    assert new_task['database'] == db.name
    assert isinstance(new_task['created'], float)
    assert isinstance(new_task['id'], string_types)

    # Test get existing task
    assert db.task(new_task['id']) == new_task

    # Test create task with specific ID
    task_name = generate_task_name()
    task_id = generate_task_id()
    new_task = db.create_task(
        name=task_name,
        command=test_command,
        params={'foo': 1, 'bar': 2},
        offset=1,
        period=10,
        task_id=task_id
    )
    assert new_task['name'] == task_name
    assert new_task['id'] == task_id
    assert 'print(params)' in new_task['command']
    assert new_task['type'] == 'periodic'
    assert new_task['database'] == db.name
    assert isinstance(new_task['created'], float)
    assert db.task(new_task['id']) == new_task

    # Test create duplicate task
    with assert_raises(TaskCreateError) as err:
        db.create_task(
            name=task_name,
            command=test_command,
            params={'foo': 1, 'bar': 2},
            task_id=task_id
        )
    assert err.value.error_code == 1851

    # Test list tasks
    for task in db.tasks():
        assert task['database'] in db.databases()
        assert task['type'] in {'periodic', 'timed'}
        assert isinstance(task['id'], string_types)
        assert isinstance(task['name'], string_types)
        assert isinstance(task['created'], float)
        assert isinstance(task['command'], string_types)

    # Test list tasks with bad database
    with assert_raises(TaskListError) as err:
        bad_db.tasks()
    assert err.value.error_code == 1228

    # Test get missing task
    with assert_raises(TaskGetError) as err:
        db.task(generate_task_id())
    assert err.value.error_code == 1852

    # Test delete existing task
    assert task_id in extract('id', db.tasks())
    assert db.delete_task(task_id) is True
    assert task_id not in extract('id', db.tasks())
    with assert_raises(TaskGetError) as err:
        db.task(task_id)
    assert err.value.error_code == 1852

    # Test delete missing task
    with assert_raises(TaskDeleteError) as err:
        db.delete_task(generate_task_id(), ignore_missing=False)
    assert err.value.error_code == 1852
    assert db.delete_task(task_id, ignore_missing=True) is False
