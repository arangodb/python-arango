from __future__ import absolute_import, unicode_literals

from datetime import datetime

from six import string_types

from arango.exceptions import (
    DatabaseCreateError,
    DatabaseDeleteError,
    DatabaseListError,
    DatabasePropertiesError,
    ServerDetailsError,
    ServerEchoError,
    ServerLogLevelError,
    ServerLogLevelSetError,
    ServerMetricsError,
    ServerReadLogError,
    ServerReloadRoutingError,
    ServerRequiredDBVersionError,
    ServerRoleError,
    ServerStatusError,
    ServerStatisticsError,
    ServerTimeError,
    ServerVersionError,
    ServerEngineError,
)
from tests.helpers import assert_raises, generate_db_name


def test_database_attributes(db, username):
    assert db.context in ['default', 'async', 'batch', 'transaction']
    assert db.username == username
    assert db.db_name == db.name
    assert db.name.startswith('test_database')
    assert db.conn is not None
    assert repr(db) == '<StandardDatabase {}>'.format(db.name)


def test_database_misc_methods(sys_db, db, bad_db):
    # Test get properties
    properties = db.properties()
    assert 'id' in properties
    assert 'path' in properties
    assert properties['name'] == db.name
    assert properties['system'] is False

    # Test get properties with bad database
    with assert_raises(DatabasePropertiesError) as err:
        bad_db.properties()
    assert err.value.error_code in {11, 1228}

    # Test get server version
    assert isinstance(db.version(), string_types)

    # Test get server version with bad database
    with assert_raises(ServerVersionError) as err:
        bad_db.version()
    assert err.value.error_code in {11, 1228}

    # Test get server details
    details = db.details()
    assert 'architecture' in details
    assert 'server-version' in details

    # Test get server details with bad database
    with assert_raises(ServerDetailsError) as err:
        bad_db.details()
    assert err.value.error_code in {11, 1228}

    # Test get server required database version
    version = db.required_db_version()
    assert isinstance(version, string_types)

    # Test get server target version with bad database
    with assert_raises(ServerRequiredDBVersionError):
        bad_db.required_db_version()

    # Test get server metrics
    metrics = db.metrics()
    assert isinstance(metrics, string_types)

    # Test get server statistics with bad database
    with assert_raises(ServerMetricsError) as err:
        bad_db.metrics()
    assert err.value.error_code in {11, 1228}

    # Test get server statistics
    statistics = db.statistics(description=False)
    assert isinstance(statistics, dict)
    assert 'time' in statistics
    assert 'system' in statistics
    assert 'server' in statistics

    # Test get server statistics with description
    description = db.statistics(description=True)
    assert isinstance(description, dict)
    assert 'figures' in description
    assert 'groups' in description

    # Test get server statistics with bad database
    with assert_raises(ServerStatisticsError) as err:
        bad_db.statistics()
    assert err.value.error_code in {11, 1228}

    # Test get server role
    assert db.role() in {
        'SINGLE',
        'COORDINATOR',
        'PRIMARY',
        'SECONDARY',
        'UNDEFINED'
    }

    # Test get server role with bad database
    with assert_raises(ServerRoleError) as err:
        bad_db.role()
    assert err.value.error_code in {11, 1228}

    # Test get server status
    status = db.status()
    assert 'host' in status
    assert 'operation_mode' in status
    assert 'server_info' in status
    assert 'read_only' in status['server_info']
    assert 'write_ops_enabled' in status['server_info']
    assert 'version' in status

    # Test get status with bad database
    with assert_raises(ServerStatusError) as err:
        bad_db.status()
    assert err.value.error_code in {11, 1228}

    # Test get server time
    assert isinstance(db.time(), datetime)

    # Test get server time with bad database
    with assert_raises(ServerTimeError) as err:
        bad_db.time()
    assert err.value.error_code in {11, 1228}

    # Test echo (get last request)
    last_request = db.echo()
    assert 'protocol' in last_request
    assert 'user' in last_request
    assert 'requestType' in last_request
    assert 'rawRequestBody' in last_request

    # Test echo with bad database
    with assert_raises(ServerEchoError) as err:
        bad_db.echo()
    assert err.value.error_code in {11, 1228}

    # Test read_log with default parameters
    log = sys_db.read_log(upto='fatal')
    assert 'lid' in log
    assert 'level' in log
    assert 'text' in log
    assert 'total_amount' in log

    # Test read_log with specific parameters
    log = sys_db.read_log(
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

    # Test read_log with bad database
    with assert_raises(ServerReadLogError) as err:
        bad_db.read_log()
    assert err.value.error_code in {11, 1228}

    # Test reload routing
    assert isinstance(db.reload_routing(), bool)

    # Test reload routing with bad database
    with assert_raises(ServerReloadRoutingError) as err:
        bad_db.reload_routing()
    assert err.value.error_code in {11, 1228}

    # Test get log levels
    assert isinstance(sys_db.log_levels(), dict)

    # Test get log levels with bad database
    with assert_raises(ServerLogLevelError) as err:
        bad_db.log_levels()
    assert err.value.error_code in {11, 1228}

    # Test set log levels
    new_levels = {
        'agency': 'DEBUG',
        'collector': 'INFO',
        'threads': 'WARNING'
    }
    result = sys_db.set_log_levels(**new_levels)
    for key, value in new_levels.items():
        assert result[key] == value
    for key, value in sys_db.log_levels().items():
        assert result[key] == value

    # Test set log levels with bad database
    with assert_raises(ServerLogLevelSetError):
        bad_db.set_log_levels(**new_levels)

    # Test get storage engine
    engine = db.engine()
    assert engine['name'] in ['rocksdb']
    assert 'supports' in engine

    # Test get storage engine with bad database
    with assert_raises(ServerEngineError) as err:
        bad_db.engine()
    assert err.value.error_code in {11, 1228}


def test_database_management(db, sys_db, bad_db):
    # Test list databases
    result = sys_db.databases()
    assert '_system' in result

    # Test list databases with bad database
    with assert_raises(DatabaseListError):
        bad_db.databases()

    # Test create database
    db_name = generate_db_name()
    assert sys_db.has_database(db_name) is False
    assert sys_db.create_database(
        name=db_name,
        replication_factor=1,
        write_concern=1,
        sharding="single"
    ) is True
    assert sys_db.has_database(db_name) is True

    # Test create duplicate database
    with assert_raises(DatabaseCreateError) as err:
        sys_db.create_database(db_name)
    assert err.value.error_code == 1207

    # Test create database without permissions
    with assert_raises(DatabaseCreateError) as err:
        db.create_database(db_name)
    assert err.value.error_code == 1230

    # Test delete database without permissions
    with assert_raises(DatabaseDeleteError) as err:
        db.delete_database(db_name)
    assert err.value.error_code == 1230

    # Test delete database
    assert sys_db.delete_database(db_name) is True
    assert db_name not in sys_db.databases()

    # Test delete missing database
    with assert_raises(DatabaseDeleteError) as err:
        sys_db.delete_database(db_name)
    assert err.value.error_code in {11, 1228}
    assert sys_db.delete_database(db_name, ignore_missing=True) is False
