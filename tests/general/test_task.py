from __future__ import absolute_import, unicode_literals

import pytest
from six import string_types

from arango import ArangoClient
from arango.exceptions import *

from tests.utils import (
    generate_db_name,
    generate_task_name, 
    generate_task_id
)

arango_client = ArangoClient()
db_name = generate_db_name()
db = arango_client.create_database(db_name)
bad_db_name = generate_db_name()
bad_db = arango_client.db(bad_db_name)
test_cmd = "require('@arangodb').print(params);"


def teardown_module(*_):
    # Clean up any test tasks that were created
    for task in db.tasks():
        if task['name'].startswith('test_task_'):
            db.delete_task(task['id'])
    arango_client.delete_database(db_name, ignore_missing=True)


def test_list_tasks():
    for task in db.tasks():
        assert task['database'] == '_system'
        assert task['type'] in {'periodic', 'timed'}
        assert isinstance(task['id'], string_types)
        assert isinstance(task['name'], string_types)
        assert isinstance(task['created'], float)
        assert isinstance(task['command'], string_types)

    with pytest.raises(TaskListError):
        bad_db.tasks()


def test_get_task():
    # Test get existing tasks
    for task in db.tasks():
        assert db.task(task['id']) == task

    # Test get missing task
    with pytest.raises(TaskGetError):
        db.task(generate_task_id())


def test_create_task():
    # Test create task with random ID
    task_name = generate_task_name()
    new_task = db.create_task(
        name=task_name,
        command=test_cmd,
        params={'foo': 1, 'bar': 2},
        offset=1,
    )
    assert new_task['name'] == task_name
    assert 'print(params)' in new_task['command']
    assert new_task['type'] == 'timed'
    assert new_task['database'] == db_name
    assert isinstance(new_task['created'], float)
    assert isinstance(new_task['id'], string_types)
    assert db.task(new_task['id']) == new_task

    # Test create task with specific ID
    task_name = generate_task_name()
    task_id = generate_task_id()
    new_task = db.create_task(
        name=task_name,
        command=test_cmd,
        params={'foo': 1, 'bar': 2},
        offset=1,
        period=10,
        task_id=task_id
    )
    assert new_task['name'] == task_name
    assert new_task['id'] == task_id
    assert 'print(params)' in new_task['command']
    assert new_task['type'] == 'periodic'
    assert new_task['database'] == db_name
    assert isinstance(new_task['created'], float)
    assert db.task(new_task['id']) == new_task

    # Test create duplicate task
    with pytest.raises(TaskCreateError):
        db.create_task(
            name=task_name,
            command=test_cmd,
            params={'foo': 1, 'bar': 2},
            task_id=task_id
        )


def test_delete_task():
    # Set up a test task to delete
    task_name = generate_task_name()
    task_id = generate_task_id()
    db.create_task(
        name=task_name,
        command=test_cmd,
        params={'foo': 1, 'bar': 2},
        task_id=task_id,
        period=10
    )

    # Test delete existing task
    assert db.delete_task(task_id) is True
    with pytest.raises(TaskGetError):
        db.task(task_id)

    # Test delete missing task without ignore_missing
    with pytest.raises(TaskDeleteError):
        db.delete_task(task_id, ignore_missing=False)

    # Test delete missing task with ignore_missing
    assert db.delete_task(task_id, ignore_missing=True) is False
