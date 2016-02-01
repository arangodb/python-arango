from __future__ import absolute_import, unicode_literals

from datetime import datetime

import pytest
from six import string_types

from arango import ArangoClient
from arango.database import Database
from arango.exceptions import *

from .utils import generate_db_name

arango_client = ArangoClient()
db_name = generate_db_name(arango_client)


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)


def test_properties():
    assert arango_client.protocol == 'http'
    assert arango_client.host == 'localhost'
    assert arango_client.port == 8529
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


# def test_sleep():
#     assert arango_client.sleep(2) == 2


def test_execute():
    assert arango_client.execute('return 1') == '1'
    assert arango_client.execute('return "test"') == '"test"'
    with pytest.raises(ServerExecuteError) as err:
        arango_client.execute('return invalid')
    assert 'Internal Server Error' in err.value.message


# TODO test parameters
def test_log():
    log = arango_client.read_log()
    assert 'lid' in log
    assert 'level' in log
    assert 'text' in log
    assert 'total_amount' in log


def test_reload_routing():
    result = arango_client.reload_routing()
    assert isinstance(result, bool)


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
