from __future__ import absolute_import, unicode_literals

from datetime import datetime

import pytest
from six import string_types

from arango import ArangoClient
from arango.api.databases.base import BaseDatabase
from arango.exceptions import (
    DatabaseCreateError,
    DatabaseDeleteError,
    ServerConnectionError,
    ServerExecuteError,
)

from tests.utils import (
    arango_version,
    generate_db_name,
    generate_user_name
)

asyncio_client_module = pytest.importorskip("arango.http_clients.asyncio")
asyncio_client = asyncio_client_module.AsyncioHTTPClient()
arango_client = ArangoClient(http_client=asyncio_client)
db_name = generate_db_name()


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)
    asyncio_client.stop_client_loop()


def test_verify():
    assert arango_client.verify() is True
    with pytest.raises(ServerConnectionError):
        ArangoClient(
            username='root',
            password='incorrect',
            verify=True
        )


def test_properties():
    assert arango_client.protocol == 'http'
    assert arango_client.host == '127.0.0.1'
    assert arango_client.port == 8529
    assert arango_client.username == 'root'
    assert arango_client.password == ''
    assert arango_client.http_client == asyncio_client
    assert arango_client.logging_enabled is True
    assert 'ArangoDB client for' in repr(arango_client)


def test_version():
    version = arango_client.version()
    assert isinstance(version, string_types)


def test_details():
    details = arango_client.details()
    assert 'architecture' in details
    assert 'server-version' in details


def test_required_db_version():
    version = arango_client.required_db_version()
    assert isinstance(version, string_types)


def test_statistics():
    statistics = arango_client.statistics(description=False)
    assert isinstance(statistics, dict)
    assert 'time' in statistics
    assert 'system' in statistics
    assert 'server' in statistics

    description = arango_client.statistics(description=True)
    assert isinstance(description, dict)
    assert 'figures' in description
    assert 'groups' in description


def test_role():
    assert arango_client.role() in {
        'SINGLE',
        'COORDINATOR',
        'PRIMARY',
        'SECONDARY',
        'UNDEFINED'
    }


def test_time():
    system_time = arango_client.time()
    assert isinstance(system_time, datetime)


def test_echo():
    last_request = arango_client.echo()
    assert 'protocol' in last_request
    assert 'user' in last_request
    assert 'requestType' in last_request
    assert 'rawRequestBody' in last_request


def test_sleep():
    assert arango_client.sleep(0) == 0


def test_execute():
    major, minor = arango_version(arango_client)

    # TODO ArangoDB 3.2 seems to be missing this API endpoint
    if not (major == 3 and minor == 2):
        assert arango_client.execute('return 1') == '1'
        assert arango_client.execute('return "test"') == '"test"'
        with pytest.raises(ServerExecuteError) as err:
            arango_client.execute('return invalid')
        assert 'Internal Server Error' in err.value.message


# TODO test parameters
def test_log():
    # Test read_log with default arguments
    log = arango_client.read_log(upto='fatal')
    assert 'lid' in log
    assert 'level' in log
    assert 'text' in log
    assert 'total_amount' in log

    # Test read_log with specific arguments
    log = arango_client.read_log(
        level='error',
        start=0,
        size=100000,
        offset=0,
        search='test',
        sort='desc',
    )
    assert 'lid' in log
    assert 'level' in log
    assert 'text' in log
    assert 'total_amount' in log


def test_reload_routing():
    result = arango_client.reload_routing()
    assert isinstance(result, bool)


def test_log_levels():
    major, minor = arango_version(arango_client)
    if major == 3 and minor >= 1:

        result = arango_client.log_levels()
        assert isinstance(result, dict)


def test_set_log_levels():
    major, minor = arango_version(arango_client)
    if major == 3 and minor >= 1:

        new_levels = {
            'agency': 'DEBUG',
            'collector': 'INFO',
            'threads': 'WARNING'
        }
        result = arango_client.set_log_levels(**new_levels)

        for key, value in new_levels.items():
            assert result[key] == value

        for key, value in arango_client.log_levels().items():
            assert result[key] == value


def test_endpoints():
    endpoints = arango_client.endpoints()
    assert isinstance(endpoints, list)
    for endpoint in endpoints:
        assert 'endpoint' in endpoint


def test_database_management():
    # Test list databases
    # TODO something wrong here
    result = arango_client.databases()
    assert '_system' in result
    result = arango_client.databases(user_only=True)
    assert '_system' in result
    assert db_name not in arango_client.databases()

    # Test create database
    result = arango_client.create_database(db_name)
    assert isinstance(result, BaseDatabase)
    assert db_name in arango_client.databases()

    # Test get after create database
    assert isinstance(arango_client.db(db_name), BaseDatabase)
    assert arango_client.db(db_name).name == db_name

    # Test create duplicate database
    with pytest.raises(DatabaseCreateError):
        arango_client.create_database(db_name)

    # Test list after create database
    assert db_name in arango_client.databases()

    # Test delete database
    result = arango_client.delete_database(db_name)
    assert result is True
    assert db_name not in arango_client.databases()

    # Test delete missing database
    with pytest.raises(DatabaseDeleteError):
        arango_client.delete_database(db_name)

    # Test delete missing database (ignore missing)
    result = arango_client.delete_database(db_name, ignore_missing=True)
    assert result is False


def test_update_user():
    # added for full coverage of patch command
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
