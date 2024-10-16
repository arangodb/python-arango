from datetime import datetime

import pytest
from packaging import version

from arango.aql import AQL
from arango.backup import Backup
from arango.cluster import Cluster
from arango.errno import (
    DATABASE_NOT_FOUND,
    DUPLICATE_NAME,
    FORBIDDEN,
    USE_SYSTEM_DATABASE,
)
from arango.exceptions import (
    DatabaseCompactError,
    DatabaseCreateError,
    DatabaseDeleteError,
    DatabaseListError,
    DatabasePropertiesError,
    DatabaseSupportInfoError,
    ServerDetailsError,
    ServerEchoError,
    ServerEngineError,
    ServerLicenseSetError,
    ServerLogLevelError,
    ServerLogLevelResetError,
    ServerLogLevelSetError,
    ServerMetricsError,
    ServerModeSetError,
    ServerReadLogError,
    ServerReloadRoutingError,
    ServerRequiredDBVersionError,
    ServerRoleError,
    ServerStatisticsError,
    ServerStatusError,
    ServerTimeError,
    ServerVersionError,
)
from arango.foxx import Foxx
from arango.pregel import Pregel
from arango.replication import Replication
from arango.wal import WAL
from tests.helpers import (
    assert_raises,
    generate_col_name,
    generate_db_name,
    generate_jwt,
)


def test_database_attributes(db, username):
    assert db.context in ["default", "async", "batch", "transaction"]
    assert db.username == username
    assert db.db_name == db.name
    assert db.name.startswith("test_database")
    assert db.conn is not None
    assert repr(db) == f"<StandardDatabase {db.name}>"

    assert isinstance(db.aql, AQL)
    assert isinstance(db.backup, Backup)
    assert isinstance(db.cluster, Cluster)
    assert isinstance(db.foxx, Foxx)
    assert isinstance(db.pregel, Pregel)
    assert isinstance(db.replication, Replication)
    assert isinstance(db.wal, WAL)


def test_database_misc_methods(client, sys_db, db, bad_db, cluster, secret, db_version):
    # Test get properties
    properties = db.properties()
    assert "id" in properties
    assert "path" in properties
    assert properties["name"] == db.name
    assert properties["system"] is False

    # Test get properties with bad database
    with assert_raises(DatabasePropertiesError) as err:
        bad_db.properties()
    assert err.value.error_code in {11, 1228}

    # Test get server version
    assert isinstance(db.version(), str)
    assert isinstance(db.version(details=True), dict)

    # Test get server version with bad database
    with assert_raises(ServerVersionError) as err:
        bad_db.version()
    assert err.value.error_code in {11, 1228}

    # Test get server details
    details = db.details()
    assert "architecture" in details
    assert "server-version" in details

    # Test get server details with bad database
    with assert_raises(ServerDetailsError) as err:
        bad_db.details()
    assert err.value.error_code in {11, 1228}

    # Test get server required database version
    required_version = db.required_db_version()
    assert isinstance(required_version, str)

    # Test get server target version with bad database
    with assert_raises(ServerRequiredDBVersionError):
        bad_db.required_db_version()

    # Test get server metrics
    metrics = db.metrics()
    assert isinstance(metrics, str)

    # Test get server statistics with bad database
    with assert_raises(ServerMetricsError) as err:
        bad_db.metrics()
    assert err.value.error_code in {11, 1228}

    # Test get server statistics
    statistics = db.statistics(description=False)
    assert isinstance(statistics, dict)
    assert "time" in statistics
    assert "system" in statistics
    assert "server" in statistics

    # Test get server statistics with description
    description = db.statistics(description=True)
    assert isinstance(description, dict)
    assert "figures" in description
    assert "groups" in description

    # Test get server statistics with bad database
    with assert_raises(ServerStatisticsError) as err:
        bad_db.statistics()
    assert err.value.error_code in {11, 1228}

    # Test get server role
    assert db.role() in {"SINGLE", "COORDINATOR", "PRIMARY", "SECONDARY", "UNDEFINED"}

    # Test get server role with bad database
    with assert_raises(ServerRoleError) as err:
        bad_db.role()
    assert err.value.error_code in {11, 1228}

    # Test get/set server mode
    assert sys_db.mode() == "default"
    with assert_raises(ServerModeSetError):
        sys_db.set_mode("badmode")
    assert err.value.error_code in {11, 1228}

    with assert_raises(ServerModeSetError):
        db.set_mode("readonly")
    assert err.value.error_code in {11, 1228}

    result = sys_db.set_mode("default")
    assert result == {"mode": "default"}

    # Test get server status
    status = db.status()
    assert "host" in status
    assert "operation_mode" in status
    assert "server_info" in status
    assert "read_only" in status["server_info"]
    assert "write_ops_enabled" in status["server_info"]
    assert "version" in status

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
    assert "protocol" in last_request
    assert "user" in last_request
    assert "requestType" in last_request
    assert "rawRequestBody" in last_request

    # Test echo with bad database
    with assert_raises(ServerEchoError) as err:
        bad_db.echo()
    assert err.value.error_code in {11, 1228}

    # Test echo (forward request)
    body = "request goes here"
    echo = db.echo(body)
    assert isinstance(echo, dict)
    assert echo["requestBody"] == body

    # Test read_log with default parameters
    # Deprecated in 3.8.0
    # TODO: Remove in future release
    log = sys_db.read_log(upto="fatal")
    assert "lid" in log
    assert "level" in log
    assert "text" in log
    assert "total_amount" in log

    log_entry = sys_db.read_log_entries(upto="fatal")
    assert "total" in log_entry
    assert "messages" in log_entry

    kwargs = {
        "level": "error",
        "start": 0,
        "size": 100000,
        "offset": 0,
        "search": "test",
        "sort": "desc",
    }

    # Test read_log with specific parameters
    # Deprecated in 3.8.0
    # TODO: Remove in future release
    log = sys_db.read_log(**kwargs)
    assert "lid" in log
    assert "level" in log
    assert "text" in log
    assert "total_amount" in log

    log_entry = sys_db.read_log_entries(**kwargs)
    assert "total" in log_entry
    assert "messages" in log_entry

    # Test read_log with bad database
    # Deprecated in 3.8.0
    # TODO: Remove in future release
    with assert_raises(ServerReadLogError) as err:
        bad_db.read_log()
    assert err.value.error_code in {11, 1228}

    # Test read_log_entries with bad database
    with assert_raises(ServerReadLogError) as err:
        bad_db.read_log_entries()
    assert err.value.error_code in {11, 1228}

    # Test reload routing
    assert isinstance(db.reload_routing(), bool)

    # Test reload routing with bad database
    with assert_raises(ServerReloadRoutingError) as err:
        bad_db.reload_routing()
    assert err.value.error_code in {11, 1228}

    # Test get log levels
    default_log_levels = sys_db.log_levels()
    assert isinstance(default_log_levels, dict)
    if db_version >= version.parse("3.12.2"):
        log_levels_with_appenders = sys_db.log_levels(with_appenders=True)
        assert isinstance(log_levels_with_appenders, dict)

    # Test get log levels with bad database
    with assert_raises(ServerLogLevelError) as err:
        bad_db.log_levels()
    assert err.value.error_code in {11, 1228}

    # Test set log levels
    new_levels = {"agency": "DEBUG", "engines": "INFO", "threads": "WARNING"}
    result = sys_db.set_log_levels(**new_levels)
    for key, value in new_levels.items():
        assert result[key] == value
    for key, value in sys_db.log_levels().items():
        assert result[key] == value

    if cluster:
        # Test get log levels (with server_id)
        server_id = sys_db.cluster.server_id()
        assert isinstance(sys_db.log_levels(server_id), dict)

        # Test set log levels (with server_id)
        result = sys_db.set_log_levels(server_id, **new_levels)
        for key, value in new_levels.items():
            assert result[key] == value
        for key, value in sys_db.log_levels(server_id).items():
            assert result[key] == value

    # Test set log levels with bad database
    with assert_raises(ServerLogLevelSetError):
        bad_db.set_log_levels(**new_levels)

    # Test Log Settings
    result_1 = sys_db.set_log_settings(database=True, url=True, username=True)
    result_2 = sys_db.log_settings()
    assert isinstance(result_1, dict)
    assert "database" in result_1
    assert "url" in result_1
    assert "username" in result_1
    assert result_1 == result_2

    result_1 = sys_db.set_log_settings(database=True, username=False)
    result_2 = sys_db.log_settings()
    assert "database" in result_1
    assert "url" in result_1
    assert "username" not in result_1
    assert result_1 == result_2

    # Reset Log Settings
    if db.version() >= "3.12.1":
        if cluster:
            server_id = sys_db.cluster.server_id()
            assert isinstance(sys_db.reset_log_levels(server_id), dict)

        result = sys_db.reset_log_levels()
        assert result == default_log_levels
        with assert_raises(ServerLogLevelResetError):
            bad_db.reset_log_levels()

    # Test get storage engine
    engine = db.engine()
    assert engine["name"] in ["rocksdb"]
    assert "supports" in engine

    # Test get storage engine with bad database
    with assert_raises(ServerEngineError) as err:
        bad_db.engine()
    assert err.value.error_code in {11, 1228}

    with assert_raises(DatabaseSupportInfoError) as err:
        db.support_info()

    info = sys_db.support_info()
    assert isinstance(info, dict)
    assert "deployment" in info
    assert "date" in info

    # Test execute JavaScript code
    assert db.execute(1) is None
    assert db.execute(None) == {"error": False, "code": 200}
    assert db.execute("") == {"error": False, "code": 200}
    assert db.execute("return 1") == 1

    # Test database compact
    with assert_raises(DatabaseCompactError) as err:
        db.compact()

    collection = db.create_collection(generate_col_name())
    collection.insert({"foo": "bar"})

    token = generate_jwt(secret)
    db_superuser = client.db(db.name, superuser_token=token)
    result = db_superuser.compact()
    assert result == {}


def test_database_management(db, sys_db, bad_db):
    # Test list databases
    result = sys_db.databases()
    assert "_system" in result
    assert db.name in result

    # Test list databases accesible to root user
    result = sys_db.databases_accessible_to_user()
    assert "_system" in result
    assert db.name in result

    # Test list databases accessible to user
    result = db.databases_accessible_to_user()
    assert result == [db.name]

    # Test list databases with bad database
    with assert_raises(DatabaseListError):
        bad_db.databases()

    # Test list accessible databases with bad database
    with assert_raises(DatabaseListError):
        bad_db.databases_accessible_to_user()

    # Test create database
    db_name = generate_db_name()
    assert sys_db.has_database(db_name) is False
    assert (
        sys_db.create_database(
            name=db_name, replication_factor=1, write_concern=1, sharding="single"
        )
        is True
    )
    assert sys_db.has_database(db_name) is True

    # Test list database with bad database
    with assert_raises(DatabaseListError) as err:
        bad_db.has_database(db_name)
    assert err.value.error_code == FORBIDDEN

    # Test has database with bad database
    with assert_raises(DatabaseListError) as err:
        bad_db.has_database(db_name)
    assert err.value.error_code == FORBIDDEN

    # Test create duplicate database
    with assert_raises(DatabaseCreateError) as err:
        sys_db.create_database(db_name)
    assert err.value.error_code == DUPLICATE_NAME

    # Test create database without permissions
    with assert_raises(DatabaseCreateError) as err:
        db.create_database(db_name)
    assert err.value.error_code == USE_SYSTEM_DATABASE

    # Test delete database without permissions
    with assert_raises(DatabaseDeleteError) as err:
        db.delete_database(db_name)
    assert err.value.error_code == USE_SYSTEM_DATABASE

    # Test delete database
    assert sys_db.delete_database(db_name) is True
    assert db_name not in sys_db.databases()

    # Test delete missing database
    with assert_raises(DatabaseDeleteError) as err:
        sys_db.delete_database(db_name)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}
    assert sys_db.delete_database(db_name, ignore_missing=True) is False


@pytest.fixture
def special_db_names(sys_db):
    names = ["abc123", "maçã", "mötör", "😀", "ﻚﻠﺑ ﻞﻄﻴﻓ", "かわいい犬"]

    yield names

    for name in names:
        try:
            sys_db.delete_database(name)
        except DatabaseDeleteError:
            pass


def test_database_utf8(sys_db, special_db_names):
    for name in special_db_names:
        assert sys_db.create_database(name)
        assert sys_db.has_database(name)
        assert sys_db.delete_database(name)


def test_license(sys_db, enterprise):
    license = sys_db.license()
    assert isinstance(license, dict)

    if enterprise:
        assert set(license.keys()) == {
            "upgrading",
            "features",
            "license",
            "version",
            "status",
        }
    else:
        assert license == {"license": "none"}
        with pytest.raises(ServerLicenseSetError):
            sys_db.set_license('"abc"')


def test_options(sys_db, db_version):
    # Skip if below 3.12
    if db_version < version.parse("3.12.0"):
        pytest.skip("Database options require ArangoDB 3.12+")

    assert sys_db.options()
    assert sys_db.options_available()
