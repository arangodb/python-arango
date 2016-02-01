from __future__ import absolute_import, unicode_literals

import pytest
from six import string_types

from arango import ArangoClient
from arango.exceptions import *

from .utils import (
    generate_user_name,
    generate_db_name,
    generate_col_name
)

arango_client = ArangoClient()
db_name = generate_db_name(arango_client)
arango_client.create_database(db_name)


def teardown_module(*_):
    # Clean up any test users that were created
    for user in arango_client.users():
        if user['username'].startswith('test_user'):
            arango_client.delete_user(user['username'])
    arango_client.delete_database(db_name, ignore_missing=True)


def test_list_users():
    for user in arango_client.users():
        assert isinstance(user['username'], string_types)
        assert isinstance(user['active'], bool)
        assert isinstance(user['extra'], dict)
        assert isinstance(user['change_password'], bool)


def test_get_user():
    # Test get existing users
    for user in arango_client.users():
        assert arango_client.user(user['username']) == user

    # Test get missing user
    missing_username = generate_user_name(arango_client)
    with pytest.raises(UserGetError):
        arango_client.user(missing_username)


def test_create_user():
    # Test active create user with change_password
    username = generate_user_name(arango_client)
    new_user = arango_client.create_user(
        username=username,
        password='password',
        active=True,
        extra={'foo': 'bar'},
        change_password=True
    )
    assert new_user['username'] == username
    assert new_user['active'] is True
    assert new_user['extra'] == {'foo': 'bar'}
    assert new_user['change_password'] is True
    assert arango_client.user(new_user['username']) == new_user

    # Test create user without change_password
    username = generate_user_name(arango_client)
    new_user = arango_client.create_user(
        username=username,
        password='password',
        active=False,
        extra={'bar': 'baz'},
        change_password=False
    )
    assert new_user['username'] == username
    assert new_user['active'] is False
    assert new_user['extra'] == {'bar': 'baz'}
    assert new_user['change_password'] is False
    assert arango_client.user(new_user['username']) == new_user

    # Test create duplicate user
    with pytest.raises(UserCreateError):
        arango_client.create_user(username=username, password='password')


def test_update_user():
    # Set up a test user to update
    username = generate_user_name(arango_client)
    arango_client.create_user(
        username=username,
        password='password',
        active=True,
        extra={'foo': 'bar'},
        change_password=True
    )

    # Test update existing user
    new_user = arango_client.update_user(
        username=username,
        password='password',
        active=False,
        extra={'bar': 'baz'},
        change_password=False
    )
    assert new_user['username'] == username
    assert new_user['active'] is False
    assert new_user['extra'] == {'foo': 'bar', 'bar': 'baz'}
    assert new_user['change_password'] is True
    assert arango_client.user(new_user['username']) == new_user

    # Test update missing user
    missing_username = generate_user_name(arango_client)
    with pytest.raises(UserUpdateError):
        arango_client.update_user(missing_username, password='password')


def test_replace_user():
    # Set up a test user to replace
    username = generate_user_name(arango_client)
    arango_client.create_user(
        username=username,
        password='password',
        active=True,
        extra={'foo': 'bar'},
        change_password=True
    )

    # Test replace existing user
    new_user = arango_client.replace_user(
        username=username,
        password='password',
        active=False,
        extra={'bar': 'baz'},
        change_password=False
    )
    assert new_user['username'] == username
    assert new_user['active'] is False
    assert new_user['extra'] == {'bar': 'baz'}
    assert new_user['change_password'] is False
    assert arango_client.user(new_user['username']) == new_user

    # Test replace missing user
    missing_username = generate_user_name(arango_client)
    with pytest.raises(UserReplaceError):
        arango_client.replace_user(missing_username, password='password')


def test_delete_user():
    # Set up a test user to delete
    username = generate_user_name(arango_client)
    arango_client.create_user(username=username, password='password')

    # Test delete existing user
    assert arango_client.delete_user(username) is True

    # Test delete missing user without ignore_missing
    with pytest.raises(UserDeleteError):
        arango_client.delete_user(username, ignore_missing=False)

    # Test delete missing user with ignore_missing
    assert arango_client.delete_user(username, ignore_missing=True) is False


def test_grant_user_access():
    # Set up a test user to grant access
    username = generate_user_name(arango_client)
    arango_client.create_user(username=username, password='password')
    db = arango_client.db(db_name, username=username, password='password')

    # Test new user without access
    with pytest.raises(CollectionCreateError) as err:
        db.create_collection(generate_col_name(arango_client.db('_system')))
    assert err.value.http_code == 401

    # Test new user with access granted
    arango_client.grant_user_access(username, db_name)
    col_name = generate_col_name(db)
    db.create_collection(col_name)
    assert col_name in set(col['name'] for col in db.collections())

    # Test grant access to missing user
    missing_username = generate_user_name(arango_client)
    with pytest.raises(UserGrantAccessError):
        arango_client.grant_user_access(missing_username, db_name)


def test_revoke_user_access():
    # Set up test user with access
    username = generate_user_name(arango_client)
    arango_client.create_user(username=username, password='password')
    db = arango_client.db(db_name, username=username, password='password')
    arango_client.grant_user_access(username, db_name)

    # Test precondition
    col_name = generate_col_name(db)
    db.create_collection(col_name)
    assert col_name in set(col['name'] for col in db.collections())

    # Test user with access revoked
    arango_client.revoke_user_access(username, db_name)
    with pytest.raises(CollectionCreateError) as err:
        db.create_collection(generate_col_name(arango_client.db('_system')))
    assert err.value.http_code == 401

    # Test revoke access to missing user
    missing_username = generate_user_name(arango_client)
    with pytest.raises(UserRevokeAccessError):
        arango_client.revoke_user_access(missing_username, db_name)
