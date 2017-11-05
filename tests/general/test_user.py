from __future__ import absolute_import, unicode_literals

from six import string_types
import pytest

from arango import ArangoClient
from arango.utils import HTTP_AUTH_ERR
from arango.exceptions import *

from .utils import (
    generate_user_name,
    generate_db_name,
    generate_col_name
)

arango_client = ArangoClient()
bad_client = ArangoClient(password='incorrect')
db_name = generate_db_name()
db = arango_client.create_database(db_name)
bad_db = bad_client.db(db_name)
another_db_name = generate_db_name()


def teardown_module(*_):
    # Clean up any users that were created during the test
    for user in arango_client.users():
        if user['username'].startswith('test_user'):
            arango_client.delete_user(user['username'])
    arango_client.delete_database(db_name, ignore_missing=True)


def test_list_users():
    for user in arango_client.users():
        assert isinstance(user['username'], string_types)
        assert isinstance(user['active'], bool)
        assert isinstance(user['extra'], dict)

    with pytest.raises(UserListError) as err:
        bad_client.users()
    assert err.value.http_code in HTTP_AUTH_ERR


def test_get_user():
    # Get existing user
    for user in arango_client.users():
        assert arango_client.user(user['username']) == user

    # Get a missing user
    bad_username = generate_user_name()
    with pytest.raises(UserGetError) as err:
        arango_client.user(bad_username)
    assert err.value.http_code == 404


def test_create_user():
    # Create a new user
    username = generate_user_name()
    new_user = arango_client.create_user(
        username=username,
        password='password',
        active=True,
        extra={'foo': 'bar'},
    )
    assert new_user['username'] == username
    assert new_user['active'] is True
    assert new_user['extra'] == {'foo': 'bar'}
    assert arango_client.user(username) == new_user

    # Create a duplicate user
    with pytest.raises(UserCreateError) as err:
        arango_client.create_user(username=username, password='foo')
    assert 'duplicate' in err.value.message


def test_update_user():
    username = generate_user_name()
    arango_client.create_user(
        username=username,
        password='password',
        active=True,
        extra={'foo': 'bar'},
    )

    # Update an existing user
    new_user = arango_client.update_user(
        username=username,
        password='new_password',
        active=False,
        extra={'bar': 'baz'},
    )
    assert new_user['username'] == username
    assert new_user['active'] is False
    assert new_user['extra'] == {'foo': 'bar', 'bar': 'baz'}
    assert arango_client.user(username) == new_user

    # Update a missing user
    bad_username = generate_user_name()
    with pytest.raises(UserUpdateError) as err:
        arango_client.update_user(
            username=bad_username,
            password='new_password'
        )
    assert err.value.http_code == 404


def test_replace_user():
    username = generate_user_name()
    arango_client.create_user(
        username=username,
        password='password',
        active=True,
        extra={'foo': 'bar'},
    )

    # Replace an existing user
    new_user = arango_client.replace_user(
        username=username,
        password='password',
        active=False,
        extra={'bar': 'baz'},
    )
    assert new_user['username'] == username
    assert new_user['active'] is False
    assert new_user['extra'] == {'bar': 'baz'}
    assert arango_client.user(username) == new_user

    # Replace a missing user
    bad_username = generate_user_name()
    with pytest.raises(UserReplaceError) as err:
        arango_client.replace_user(
            username=bad_username,
            password='new_password'
        )
    assert err.value.http_code == 404


def test_delete_user():
    username = generate_user_name()
    arango_client.create_user(
        username=username,
        password='password'
    )

    # Delete an existing user
    assert arango_client.delete_user(username) is True

    # Delete a missing user without ignore_missing
    with pytest.raises(UserDeleteError) as err:
        arango_client.delete_user(username, ignore_missing=False)
    assert err.value.http_code == 404

    # Delete a missing user with ignore_missing
    assert arango_client.delete_user(username, ignore_missing=True) is False


def test_grant_user_access():
    # Create a test user and login as that user
    username = generate_user_name()
    arango_client.create_user(username=username, password='password')
    user_db = arango_client.database(
        name=db_name,
        username=username,
        password='password'
    )

    # Create a collection with the user (should have no access)
    col_name = generate_col_name()
    with pytest.raises(CollectionCreateError) as err:
        user_db.create_collection(col_name)
    assert err.value.http_code in HTTP_AUTH_ERR
    assert col_name not in set(col['name'] for col in db.collections())

    # Grant the user access and try again
    arango_client.grant_user_access(username, db_name)
    db.create_collection(col_name)
    assert col_name in set(col['name'] for col in db.collections())

    # Grant access to a missing user
    bad_username = generate_user_name()
    with pytest.raises(UserGrantAccessError) as err:
        arango_client.grant_user_access(bad_username, db_name)
    assert err.value.http_code == 404


def test_revoke_user_access():
    # Create a test user with access and login as that user
    username = generate_user_name()
    arango_client.create_user(username=username, password='password')
    arango_client.grant_user_access(username, db_name)
    user_db = arango_client.database(
        name=db_name,
        username=username,
        password='password'
    )

    # Test user access by creating a collection
    col_name = generate_col_name()
    user_db.create_collection(col_name)
    assert col_name in set(col['name'] for col in db.collections())

    # Revoke access from the user
    arango_client.revoke_user_access(username, db_name)
    with pytest.raises(CollectionDeleteError) as err:
        user_db.delete_collection(col_name)
    assert err.value.http_code in HTTP_AUTH_ERR

    # Test revoke access to missing user
    bad_username = generate_user_name()
    with pytest.raises(UserRevokeAccessError) as err:
        arango_client.revoke_user_access(bad_username, db_name)
    assert err.value.http_code == 404


def test_get_user_access():
    # Create a test user
    username = generate_user_name()
    arango_client.create_user(username=username, password='password')

    # Get user access (should be empty initially)
    assert arango_client.user_access(username) == []

    # Grant user access to the database and check again
    arango_client.grant_user_access(username, db_name)
    assert arango_client.user_access(username) == [db_name]

    # Get access of a missing user
    bad_username = generate_user_name()
    assert arango_client.user_access(bad_username) == []

    # Get access of a user from a bad client (incorrect password)
    with pytest.raises(UserAccessError) as err:
        bad_client.user_access(username)
    assert err.value.http_code in HTTP_AUTH_ERR


def test_change_password():
    username = generate_user_name()
    arango_client.create_user(username=username, password='password1')
    arango_client.grant_user_access(username, db_name)

    db1 = arango_client.db(db_name, username, 'password1')
    db2 = arango_client.db(db_name, username, 'password2')

    # Ensure that the user can make requests with correct credentials
    db1.properties()

    # Ensure that the user cannot make requests with bad credentials
    with pytest.raises(DatabasePropertiesError) as err:
        db2.properties()
    assert err.value.http_code in HTTP_AUTH_ERR

    # Update the user password and test again
    arango_client.update_user(username=username, password='password2')
    db2.properties()

    # TODO ArangoDB 3.2 seems to have broken authentication:
    # TODO When the password of a user is changed, the old password still works
    # db1.create_collection('test1')
    # with pytest.raises(DatabasePropertiesError) as err:
    #     db1.create_collection('test')
    # assert err.value.http_code in HTTP_AUTH_ERR
    #
    # # Replace the user password and test again
    # arango_client.update_user(username=username, password='password1')
    # db1.properties()
    # with pytest.raises(DatabasePropertiesError) as err:
    #     db2.properties()
    # assert err.value.http_code in HTTP_AUTH_ERR


def test_create_user_with_database():
    username1 = generate_user_name()
    username2 = generate_user_name()
    username3 = generate_user_name()
    user_db = arango_client.create_database(
        name=another_db_name,
        users=[
            {'username': username1, 'password': 'password1'},
            {'username': username2, 'password': 'password2'},
            {'username': username3, 'password': 'password3', 'active': False},
        ],
        username=username1,
        password='password1'
    )
    # Test if the users were created properly
    all_usernames = set(user['username'] for user in arango_client.users())
    assert username1 in all_usernames
    assert username2 in all_usernames

    # Test if the first user has access to the database
    assert user_db.connection.username == username1
    assert user_db.connection.password == 'password1'
    user_db.properties()

    # Test if the second user also has access to the database
    user_db = arango_client.database(another_db_name, username2, 'password2')
    assert user_db.connection.username == username2
    assert user_db.connection.password == 'password2'
    user_db.properties()

    # Test if the third user has access to the database (should not)
    user_db = arango_client.database(another_db_name, username3, 'password3')
    assert user_db.connection.username == username3
    assert user_db.connection.password == 'password3'
    with pytest.raises(DatabasePropertiesError) as err:
        user_db.properties()
    assert err.value.http_code in HTTP_AUTH_ERR

def test_list_users_db_level():
    for user in db.users():
        assert isinstance(user['username'], string_types)
        assert isinstance(user['active'], bool)
        assert isinstance(user['extra'], dict)

    with pytest.raises(UserListError) as err:
        bad_db.users()
    assert err.value.http_code in HTTP_AUTH_ERR


def test_get_user_db_level():
    # Get existing user
    for user in db.users():
        assert db.user(user['username']) == user

    # Get a missing user
    bad_username = generate_user_name()
    with pytest.raises(UserGetError) as err:
        db.user(bad_username)
    assert err.value.http_code == 404


def test_create_user_db_level():
    # Create a new user
    username = generate_user_name()
    new_user = db.create_user(
        username=username,
        password='password',
        active=True,
        extra={'foo': 'bar'},
    )
    assert new_user['username'] == username
    assert new_user['active'] is True
    assert new_user['extra'] == {'foo': 'bar'}
    assert db.user(username) == new_user

    # Create a duplicate user
    with pytest.raises(UserCreateError) as err:
        db.create_user(username=username, password='foo')
    assert 'duplicate' in err.value.message


def test_update_user_db_level():
    username = generate_user_name()
    db.create_user(
        username=username,
        password='password',
        active=True,
        extra={'foo': 'bar'},
    )

    # Update an existing user
    new_user = db.update_user(
        username=username,
        password='new_password',
        active=False,
        extra={'bar': 'baz'},
    )
    assert new_user['username'] == username
    assert new_user['active'] is False
    assert new_user['extra'] == {'foo': 'bar', 'bar': 'baz'}
    assert db.user(username) == new_user

    # Update a missing user
    bad_username = generate_user_name()
    with pytest.raises(UserUpdateError) as err:
        db.update_user(
            username=bad_username,
            password='new_password'
        )
    assert err.value.http_code == 404


def test_replace_user_db_level():
    username = generate_user_name()
    db.create_user(
        username=username,
        password='password',
        active=True,
        extra={'foo': 'bar'},
    )

    # Replace an existing user
    new_user = db.replace_user(
        username=username,
        password='password',
        active=False,
        extra={'bar': 'baz'},
    )
    assert new_user['username'] == username
    assert new_user['active'] is False
    assert new_user['extra'] == {'bar': 'baz'}
    assert db.user(username) == new_user

    # Replace a missing user
    bad_username = generate_user_name()
    with pytest.raises(UserReplaceError) as err:
        db.replace_user(
            username=bad_username,
            password='new_password'
        )
    assert err.value.http_code == 404


def test_delete_user_db_level():
    username = generate_user_name()
    db.create_user(
        username=username,
        password='password'
    )

    # Delete an existing user
    assert db.delete_user(username) is True

    # Delete a missing user without ignore_missing
    with pytest.raises(UserDeleteError) as err:
        db.delete_user(username, ignore_missing=False)
    assert err.value.http_code == 404

    # Delete a missing user with ignore_missing
    assert db.delete_user(username, ignore_missing=True) is False


def test_grant_user_access_db_level():
    # Create a test user and login as that user
    username = generate_user_name()
    db.create_user(username=username, password='password')
    user_db = arango_client.database(
        name=db_name,
        username=username,
        password='password'
    )

    # Create a collection with the user (should have no access)
    col_name = generate_col_name()
    with pytest.raises(CollectionCreateError) as err:
        user_db.create_collection(col_name)
    assert err.value.http_code in HTTP_AUTH_ERR
    assert col_name not in set(col['name'] for col in db.collections())

    # Grant the user access and try again
    db.grant_user_access(username)
    db.create_collection(col_name)
    assert col_name in set(col['name'] for col in db.collections())

    # Grant access to a missing user
    bad_username = generate_user_name()
    with pytest.raises(UserGrantAccessError) as err:
        db.grant_user_access(bad_username)
    assert err.value.http_code == 404


def test_revoke_user_access_db_level():
    # Create a test user with access and login as that user
    username = generate_user_name()
    db.create_user(username=username, password='password')
    db.grant_user_access(username, db_name)
    user_db = arango_client.database(
        name=db_name,
        username=username,
        password='password'
    )

    # Test user access by creating a collection
    col_name = generate_col_name()
    user_db.create_collection(col_name)
    assert col_name in set(col['name'] for col in db.collections())

    # Revoke access from the user
    db.revoke_user_access(username)
    with pytest.raises(CollectionDeleteError) as err:
        user_db.delete_collection(col_name)
    assert err.value.http_code in HTTP_AUTH_ERR

    # Test revoke access to missing user
    bad_username = generate_user_name()
    with pytest.raises(UserRevokeAccessError) as err:
        db.revoke_user_access(bad_username)
    assert err.value.http_code == 404


def test_get_user_access_db_level():
    # Create a test user
    username = generate_user_name()
    db.create_user(username=username, password='password')

    # Get user access (should be none initially)
    assert db.user_access(username) is None

    # Grant user access to the database and check again
    db.grant_user_access(username)
    assert db.user_access(username) == 'rw'

    # Get access of a missing user
    bad_username = generate_user_name()
    assert db.user_access(bad_username) is None

    # Get user access from a bad database (incorrect password)
    with pytest.raises(UserAccessError) as err:
        bad_db.user_access(bad_username)
    assert err.value.http_code in HTTP_AUTH_ERR


def test_grant_user_access_collection_level():
    # Create a new test user
    username = generate_user_name()
    db.create_user(username=username, password='password')

    # Sign in as the user
    user_db = arango_client.database(
        name=db_name,
        username=username,
        password='password'
    )

    # Create a new collection
    col_name = generate_col_name()
    col = db.create_collection(col_name)

    # The new user should have no access to the collection
    with pytest.raises(ArangoError) as err:
        user_db.collection(col_name).count()
    assert err.value.http_code in HTTP_AUTH_ERR
    assert isinstance(err.value, DocumentCountError) \
           or isinstance(err.value, AsyncExecuteError) \
           or isinstance(err.value, BatchExecuteError)

    # After granting access to the collection it should work
    col.grant_user_access(username)
    assert user_db.collection(col_name).count() == 0

    # Grant access from a bad database (missing user)
    with pytest.raises(ArangoError) as err:
        bad_db.collection(col_name).grant_user_access(generate_user_name())
    assert err.value.http_code in HTTP_AUTH_ERR
    assert isinstance(err.value, UserGrantAccessError) \
           or isinstance(err.value, AsyncExecuteError) \
           or isinstance(err.value, BatchExecuteError)


def test_revoke_user_access_collection_level():
    # Create a new test user
    username = generate_user_name()
    db.create_user(username=username, password='password')
    user_db = arango_client.database(
        name=db_name,
        username=username,
        password='password'
    )
    col_name = generate_col_name()
    col = db.create_collection(col_name)

    # The new user should have no access to the collection
    with pytest.raises(ArangoError) as err:
        user_db.collection(col_name).count()
    assert err.value.http_code in HTTP_AUTH_ERR

    # After granting access to the collection it should work
    col.grant_user_access(username)
    assert user_db.collection(col_name).count() == 0

    # Revoke the access again to see that 401 is back
    col.revoke_user_access(username)
    with pytest.raises(ArangoError) as err:
        user_db.collection(col_name).count()
    assert err.value.http_code in HTTP_AUTH_ERR

    # Grant access from a bad database (missing user)
    with pytest.raises(ArangoError) as err:
        bad_db.collection(col_name).revoke_user_access(generate_user_name())
    assert err.value.http_code in HTTP_AUTH_ERR
    assert isinstance(err.value, UserRevokeAccessError) \
           or isinstance(err.value, AsyncExecuteError) \
           or isinstance(err.value, BatchExecuteError)


def test_get_user_access_collection_level():
    # Create a new test user
    username = generate_user_name()
    db.create_user(username=username, password='password')
    user_db = arango_client.database(
        name=db_name,
        username=username,
        password='password'
    )
    col_name = generate_col_name()
    col = db.create_collection(col_name)

    # The new user should have no access to the collection
    assert col.user_access(username) is None

    # After granting access to the collection it should work
    col.grant_user_access(username)
    assert col.user_access(username) == 'rw'

    # Revoke the access again to see that 401 is back
    col.revoke_user_access(username)
    assert col.user_access(username) is None

    # Grant access from a bad database (missing user)
    with pytest.raises(ArangoError) as err:
        bad_db.collection(col_name).user_access(generate_user_name())
    assert err.value.http_code in HTTP_AUTH_ERR
    assert isinstance(err.value, UserAccessError) \
           or isinstance(err.value, AsyncExecuteError) \
           or isinstance(err.value, BatchExecuteError)