from __future__ import absolute_import, unicode_literals

from datetime import datetime

import pytest
from six import string_types

from arango import ArangoClient
from arango.http_clients import DefaultHTTPClient
from arango.database import Database
from arango.exceptions import *

from .utils import generate_db_name, arango_version

http_client = DefaultHTTPClient(use_session=False)
arango_client = ArangoClient(http_client=http_client)
bad_arango_client = ArangoClient(username='root', password='incorrect')
db_name = generate_db_name()


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)


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
    assert arango_client.http_client == http_client
    assert arango_client.logging_enabled is True
    assert 'ArangoDB client for' in repr(arango_client)


def test_version():
    version = arango_client.version()
    assert isinstance(version, string_types)

    with pytest.raises(ServerVersionError):
        bad_arango_client.version()


def test_details():
    details = arango_client.details()
    assert 'architecture' in details
    assert 'server-version' in details

    with pytest.raises(ServerDetailsError):
        bad_arango_client.details()


def test_required_db_version():
    version = arango_client.required_db_version()
    assert isinstance(version, string_types)

    with pytest.raises(ServerRequiredDBVersionError):
        bad_arango_client.required_db_version()


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

    with pytest.raises(ServerStatisticsError):
        bad_arango_client.statistics()


def test_role():
    assert arango_client.role() in {
        'SINGLE',
        'COORDINATOR',
        'PRIMARY',
        'SECONDARY',
        'UNDEFINED'
    }
    with pytest.raises(ServerRoleError):
        bad_arango_client.role()


def test_time():
    system_time = arango_client.time()
    assert isinstance(system_time, datetime)

    with pytest.raises(ServerTimeError):
        bad_arango_client.time()


def test_echo():
    last_request = arango_client.echo()
    assert 'protocol' in last_request
    assert 'user' in last_request
    assert 'requestType' in last_request
    assert 'rawRequestBody' in last_request

    with pytest.raises(ServerEchoError):
        bad_arango_client.echo()


def test_sleep():
    assert arango_client.sleep(0) == 0

    with pytest.raises(ServerSleepError):
        bad_arango_client.sleep(0)


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

    # Test read_log with incorrect auth
    with pytest.raises(ServerReadLogError):
        bad_arango_client.read_log()


def test_reload_routing():
    result = arango_client.reload_routing()
    assert isinstance(result, bool)

    with pytest.raises(ServerReloadRoutingError):
        bad_arango_client.reload_routing()


def test_log_levels():
    major, minor = arango_version(arango_client)
    if major == 3 and minor >= 1:

        result = arango_client.log_levels()
        assert isinstance(result, dict)

        with pytest.raises(ServerLogLevelError):
            bad_arango_client.log_levels()


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

        with pytest.raises(ServerLogLevelSetError):
            bad_arango_client.set_log_levels(**new_levels)


def test_endpoints():
    endpoints = arango_client.endpoints()
    assert isinstance(endpoints, list)
    for endpoint in endpoints:
        assert 'endpoint' in endpoint

    with pytest.raises(ServerEndpointsError):
        bad_arango_client.endpoints()


def test_database_management():
    # Test list databases
    # TODO something wrong here
    result = arango_client.databases()
    assert '_system' in result
    result = arango_client.databases(user_only=True)
    assert '_system' in result
    assert db_name not in arango_client.databases()

    with pytest.raises(DatabaseListError):
        bad_arango_client.databases()

    # Test create database
    result = arango_client.create_database(db_name)
    assert isinstance(result, Database)
    assert db_name in arango_client.databases()

    # Test get after create database
    assert isinstance(arango_client.db(db_name), Database)
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
