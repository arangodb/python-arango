from __future__ import absolute_import, unicode_literals

from datetime import datetime

import pytest
from six import string_types

from arango import ArangoClient
from arango.collections import Collection
from arango.graph import Graph
from arango.exceptions import *

from .utils import (
    generate_db_name,
    generate_col_name,
    generate_graph_name,
    arango_version
)

arango_client = ArangoClient()
db_name = generate_db_name(arango_client)
db = arango_client.create_database(db_name)
bad_db_name = generate_db_name(arango_client)
bad_db = arango_client.db(bad_db_name)
col_name_1 = generate_col_name(db)
col_name_2 = ''
db.create_collection(col_name_1)
graph_name = generate_graph_name(db)
db.create_graph(graph_name)


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)


@pytest.mark.order1
def test_properties():
    assert db.name == db_name
    assert repr(db) == '<ArangoDB database "{}">'.format(db_name)

    properties = db.properties()
    assert 'id' in properties
    assert 'path' in properties
    assert properties['system'] is False
    assert properties['name'] == db_name
    assert 'ArangoDB connection' in repr(db.connection)

    with pytest.raises(DatabasePropertiesError):
        bad_db.properties()


@pytest.mark.order2
def test_list_collections():
    assert all(
        col['name'] == col_name_1 or col['name'].startswith('_')
        for col in db.collections()
    )

    with pytest.raises(CollectionListError):
        bad_db.collections()


@pytest.mark.order3
def test_get_collection():
    for col in [db.collection(col_name_1), db[col_name_1]]:
        assert isinstance(col, Collection)
        assert col.name == col_name_1


@pytest.mark.order4
def test_create_collection():
    global col_name_2

    # Test create duplicate collection
    with pytest.raises(CollectionCreateError):
        db.create_collection(col_name_1)

    # Test create collection with parameters
    col_name_2 = generate_col_name(db)
    col = db.create_collection(
        name=col_name_2,
        sync=True,
        compact=False,
        journal_size=7774208,
        system=False,
        volatile=False,
        key_generator="autoincrement",
        user_keys=False,
        key_increment=9,
        key_offset=100,
        edge=True,
        shard_count=2,
        shard_fields=["test_attr"],
        index_bucket_count=10,
        replication_factor=1
    )
    properties = col.properties()
    assert 'id' in properties
    assert properties['name'] == col_name_2
    assert properties['sync'] is True
    assert properties['compact'] is False
    assert properties['journal_size'] == 7774208
    assert properties['system'] is False
    assert properties['volatile'] is False
    assert properties['edge'] is True
    assert properties['keygen'] == 'autoincrement'
    assert properties['user_keys'] is False
    assert properties['key_increment'] == 9
    assert properties['key_offset'] == 100


@pytest.mark.order5
def test_create_system_collection():
    major, minor = arango_version(arango_client)
    if major == 3 and minor >= 1:

        system_col_name = '_' + col_name_1
        col = db.create_collection(
            name=system_col_name,
            system=True,
        )
        properties = col.properties()
        assert properties['system'] is True
        assert system_col_name in [c['name'] for c in db.collections()]
        assert db.collection(system_col_name).properties()['system'] is True

        with pytest.raises(CollectionDeleteError):
            db.delete_collection(system_col_name)
        assert system_col_name in [c['name'] for c in db.collections()]

        db.delete_collection(system_col_name, system=True)
        assert system_col_name not in [c['name'] for c in db.collections()]


@pytest.mark.order6
def test_drop_collection():
    # Test drop collection
    result = db.delete_collection(col_name_2)
    assert result is True
    assert col_name_2 not in set(c['name'] for c in db.collections())

    # Test drop missing collection
    with pytest.raises(CollectionDeleteError):
        db.delete_collection(col_name_2)

    # Test drop missing collection (ignore_missing)
    result = db.delete_collection(col_name_2, ignore_missing=True)
    assert result is False


@pytest.mark.order7
def test_list_graphs():
    graphs = db.graphs()
    assert len(graphs) == 1

    graph = graphs[0]
    assert graph['name'] == graph_name
    assert graph['edge_definitions'] == []
    assert graph['orphan_collections'] == []
    assert 'revision' in graph

    with pytest.raises(GraphListError):
        bad_db.graphs()


@pytest.mark.order8
def test_get_graph():
    graph = db.graph(graph_name)
    assert isinstance(graph, Graph)
    assert graph.name == graph_name


@pytest.mark.order9
def test_create_graph():
    # Test create duplicate graph
    with pytest.raises(GraphCreateError):
        db.create_graph(graph_name)

    new_graph_name = generate_graph_name(db)
    db.create_graph(new_graph_name)
    assert new_graph_name in [g['name'] for g in db.graphs()]


@pytest.mark.order10
def test_drop_graph():
    # Test drop graph
    result = db.delete_graph(graph_name)
    assert result is True
    assert graph_name not in db.graphs()

    # Test drop missing graph
    with pytest.raises(GraphDeleteError):
        db.delete_graph(graph_name)

    # Test drop missing graph (ignore_missing)
    result = db.delete_graph(graph_name, ignore_missing=True)
    assert result is False


@pytest.mark.order11
def test_verify():
    assert db.verify() is True
    with pytest.raises(ServerConnectionError):
        bad_db.verify()


@pytest.mark.order12
def test_version():
    version = db.version()
    assert isinstance(version, string_types)

    with pytest.raises(ServerVersionError):
        bad_db.version()


@pytest.mark.order13
def test_details():
    details = db.details()
    assert 'architecture' in details
    assert 'server-version' in details

    with pytest.raises(ServerDetailsError):
        bad_db.details()


@pytest.mark.order14
def test_required_db_version():
    version = db.required_db_version()
    assert isinstance(version, string_types)

    with pytest.raises(ServerRequiredDBVersionError):
        bad_db.required_db_version()


@pytest.mark.order15
def test_statistics():
    statistics = db.statistics(description=False)
    assert isinstance(statistics, dict)
    assert 'time' in statistics
    assert 'system' in statistics
    assert 'server' in statistics

    description = db.statistics(description=True)
    assert isinstance(description, dict)
    assert 'figures' in description
    assert 'groups' in description

    with pytest.raises(ServerStatisticsError):
        bad_db.statistics()


@pytest.mark.order16
def test_role():
    assert db.role() in {
        'SINGLE',
        'COORDINATOR',
        'PRIMARY',
        'SECONDARY',
        'UNDEFINED'
    }
    with pytest.raises(ServerRoleError):
        bad_db.role()


@pytest.mark.order17
def test_time():
    system_time = db.time()
    assert isinstance(system_time, datetime)

    with pytest.raises(ServerTimeError):
        bad_db.time()


@pytest.mark.order18
def test_echo():
    last_request = db.echo()
    assert 'protocol' in last_request
    assert 'user' in last_request
    assert 'requestType' in last_request
    assert 'rawRequestBody' in last_request

    with pytest.raises(ServerEchoError):
        bad_db.echo()


@pytest.mark.order19
def test_sleep():
    assert db.sleep(0) == 0

    with pytest.raises(ServerSleepError):
        bad_db.sleep(0)


@pytest.mark.order20
def test_execute():
    assert db.execute('return 1') == '1'
    assert db.execute('return "test"') == '"test"'
    with pytest.raises(ServerExecuteError) as err:
        db.execute('return invalid')
    assert 'Internal Server Error' in err.value.message


@pytest.mark.order21
def test_log():
    # Test read_log with default arguments
    log = db.read_log(upto='fatal')
    assert 'lid' in log
    assert 'level' in log
    assert 'text' in log
    assert 'total_amount' in log

    # Test read_log with specific arguments
    log = db.read_log(
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
        bad_db.read_log()


@pytest.mark.order22
def test_reload_routing():
    result = db.reload_routing()
    assert isinstance(result, bool)

    with pytest.raises(ServerReloadRoutingError):
        bad_db.reload_routing()


@pytest.mark.order23
def test_log_levels():
    major, minor = arango_version(arango_client)
    if major == 3 and minor >= 1:

        result = db.log_levels()
        assert isinstance(result, dict)

        with pytest.raises(ServerLogLevelError):
            bad_db.log_levels()


@pytest.mark.order24
def test_set_log_levels():
    major, minor = arango_version(arango_client)
    if major == 3 and minor >= 1:

        new_levels = {
            'agency': 'DEBUG',
            'collector': 'INFO',
            'threads': 'WARNING'
        }
        result = db.set_log_levels(**new_levels)

        for key, value in new_levels.items():
            assert result[key] == value

        for key, value in db.log_levels().items():
            assert result[key] == value

        with pytest.raises(ServerLogLevelSetError):
            bad_db.set_log_levels(**new_levels)
