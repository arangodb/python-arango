from __future__ import absolute_import, unicode_literals

import pytest

from arango import ArangoClient
from arango.aql import AQL
from arango.collections import Collection
from arango.exceptions import ClusterTestError
from arango.graph import Graph

from tests.utils import (
    generate_db_name,
    generate_col_name,
    generate_graph_name
)

arango_client = ArangoClient()
db_name = generate_db_name()
db = arango_client.create_database(db_name)
col_name = generate_col_name()
col = db.create_collection(col_name)
graph_name = generate_graph_name()
graph = db.create_graph(graph_name)
vcol_name = generate_col_name()
graph.create_vertex_collection(vcol_name)


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)


@pytest.mark.order1
def test_async_object():
    cluster = db.cluster(
        shard_id=1,
        transaction_id=1,
        timeout=2000,
        sync=False
    )
    assert cluster.type == 'cluster'
    assert 'ArangoDB cluster round-trip test' in repr(cluster)
    assert isinstance(cluster.aql, AQL)
    assert isinstance(cluster.graph(graph_name), Graph)
    assert isinstance(cluster.collection(col_name), Collection)


@pytest.mark.order2
def test_cluster_execute():
    cluster = db.cluster(
        shard_id='foo',
        transaction_id='bar',
        timeout=2000,
        sync=True
    )
    with pytest.raises(ClusterTestError):
        cluster.collection(col_name).checksum()
