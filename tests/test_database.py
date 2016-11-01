from __future__ import absolute_import, unicode_literals

import pytest

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
