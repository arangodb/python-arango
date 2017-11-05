from __future__ import absolute_import, unicode_literals

import pytest
from six import string_types

from arango import ArangoClient
from arango.collections.edge import EdgeCollection
from arango.collections.vertex import VertexCollection
from arango.exceptions import (
    ArangoError,
    DocumentDeleteError,
    DocumentGetError,
    DocumentInsertError,
    DocumentReplaceError,
    DocumentRevisionError,
    DocumentUpdateError,
    EdgeDefinitionCreateError,
    EdgeDefinitionDeleteError,
    EdgeDefinitionListError,
    EdgeDefinitionReplaceError,
    GraphPropertiesError,
    GraphTraverseError,
    OrphanCollectionListError,
    VertexCollectionCreateError,
    VertexCollectionDeleteError,
    VertexCollectionListError,
)
from tests.utils import (
    generate_db_name,
    generate_col_name,
    generate_graph_name,
    clean_keys
)

arango_client = ArangoClient()
db_name = generate_db_name()
db = arango_client.create_database(db_name)
col_name = generate_col_name()
col = db.create_collection(col_name)
graph_name = generate_graph_name()
graph = db.create_graph(graph_name)
bad_graph_name = generate_graph_name()
bad_graph = db.graph(bad_graph_name)
bad_col_name = generate_col_name()
bad_vcol = bad_graph.vertex_collection(bad_col_name)
bad_ecol = bad_graph.edge_collection(bad_col_name)

# vertices in test vertex collection #1
vertex1 = {'_key': '1', 'value': 1}
vertex2 = {'_key': '2', 'value': 2}
vertex3 = {'_key': '3', 'value': 3}

# vertices in test vertex collection #2
vertex4 = {'_key': '4', 'value': 4}
vertex5 = {'_key': '5', 'value': 5}
vertex6 = {'_key': '6', 'value': 6}

# edges in test edge collection
edge1 = {'_key': '1', '_from': 'vcol1/1', '_to': 'vcol3/4'}  # valid
edge2 = {'_key': '2', '_from': 'vcol1/1', '_to': 'vcol3/5'}  # valid
edge3 = {'_key': '3', '_from': 'vcol3/6', '_to': 'vcol1/2'}  # invalid
edge4 = {'_key': '4', '_from': 'vcol1/8', '_to': 'vcol3/7'}  # missing

# new edges that will be updated/replaced to
edge5 = {'_key': '1', '_from': 'vcol1/1', '_to': 'vcol3/5'}  # valid
edge6 = {'_key': '1', '_from': 'vcol3/6', '_to': 'vcol1/2'}  # invalid
edge7 = {'_key': '1', '_from': 'vcol1/8', '_to': 'vcol3/7'}  # missing


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)


def setup_function(*_):
    col.truncate()


@pytest.mark.order1
def test_properties():
    assert graph.name == graph_name
    assert repr(graph) == (
        "<ArangoDB graph '{}'>".format(graph_name)
    )
    properties = graph.properties()
    assert properties['id'] == '_graphs/{}'.format(graph_name)
    assert properties['name'] == graph_name
    assert properties['edge_definitions'] == []
    assert properties['orphan_collections'] == []
    assert isinstance(properties['revision'], string_types)
    assert not properties['smart']
    assert 'smart_field' in properties
    assert 'shard_count' in properties

    # Test if exception is raised properly
    with pytest.raises(GraphPropertiesError):
        bad_graph.properties()

    new_graph_name = generate_graph_name()
    new_graph = db.create_graph(
        new_graph_name,
        # TODO only possible with enterprise edition
        # smart=True,
        # smart_field='foo',
        # shard_count=2
    )
    properties = new_graph.properties()
    assert properties['id'] == '_graphs/{}'.format(new_graph_name)
    assert properties['name'] == new_graph_name
    assert properties['edge_definitions'] == []
    assert properties['orphan_collections'] == []
    assert isinstance(properties['revision'], string_types)
    # TODO only possible with enterprise edition
    # assert properties['smart'] == True
    # assert properties['smart_field'] == 'foo'
    # assert properties['shard_count'] == 2


@pytest.mark.order2
def test_create_vertex_collection():
    # Test preconditions
    assert graph.vertex_collections() == []
    vcol1 = graph.create_vertex_collection('vcol1')
    assert isinstance(vcol1, VertexCollection)
    assert vcol1.name == 'vcol1'
    assert vcol1.name in repr(vcol1)
    assert graph.name in repr(vcol1)
    assert graph.name == vcol1.graph_name
    assert graph.vertex_collections() == ['vcol1']
    assert graph.orphan_collections() == ['vcol1']
    assert 'vcol1' in set(c['name'] for c in db.collections())

    # Test create duplicate vertex collection
    with pytest.raises(VertexCollectionCreateError):
        graph.create_vertex_collection('vcol1')
    assert graph.vertex_collections() == ['vcol1']
    assert graph.orphan_collections() == ['vcol1']
    assert 'vcol1' in set(c['name'] for c in db.collections())

    # Test create valid vertex collection
    vcol2 = graph.create_vertex_collection('vcol2')
    assert isinstance(vcol2, VertexCollection)
    assert vcol2.name == 'vcol2'
    assert sorted(graph.vertex_collections()) == ['vcol1', 'vcol2']
    assert graph.orphan_collections() == ['vcol1', 'vcol2']
    assert 'vcol1' in set(c['name'] for c in db.collections())
    assert 'vcol2' in set(c['name'] for c in db.collections())


@pytest.mark.order3
def test_list_vertex_collections():
    assert graph.vertex_collections() == ['vcol1', 'vcol2']

    # Test if exception is raised properly
    with pytest.raises(VertexCollectionListError):
        bad_graph.vertex_collections()
    with pytest.raises(OrphanCollectionListError):
        bad_graph.orphan_collections()


@pytest.mark.order4
def test_delete_vertex_collection():
    # Test preconditions
    assert sorted(graph.vertex_collections()) == ['vcol1', 'vcol2']
    assert graph.delete_vertex_collection('vcol1') is True
    assert graph.vertex_collections() == ['vcol2']
    assert 'vcol1' in set(c['name'] for c in db.collections())

    # Test delete missing vertex collection
    with pytest.raises(VertexCollectionDeleteError):
        graph.delete_vertex_collection('vcol1')

    # Test delete vertex collection with purge option
    assert graph.delete_vertex_collection('vcol2', purge=True) is True
    assert graph.vertex_collections() == []
    assert 'vcol1' in set(c['name'] for c in db.collections())
    assert 'vcol2' not in set(c['name'] for c in db.collections())


@pytest.mark.order5
def test_create_edge_definition():
    # Test preconditions
    assert graph.edge_definitions() == []

    ecol1 = graph.create_edge_definition('ecol1', [], [])
    assert isinstance(ecol1, EdgeCollection)
    assert ecol1.name == 'ecol1'
    assert ecol1.name in repr(ecol1)
    assert graph.name in repr(ecol1)
    assert graph.name == ecol1.graph_name

    assert graph.edge_definitions() == [{
        'name': 'ecol1',
        'from_collections': [],
        'to_collections': []
    }]
    assert 'ecol1' in set(c['name'] for c in db.collections())

    # Test create duplicate edge definition
    with pytest.raises(EdgeDefinitionCreateError):
        assert graph.create_edge_definition('ecol1', [], [])
    assert graph.edge_definitions() == [{
        'name': 'ecol1',
        'from_collections': [],
        'to_collections': []
    }]

    # Test create edge definition with existing vertex collection
    vcol1 = graph.create_vertex_collection('vcol1')
    assert isinstance(vcol1, VertexCollection)
    assert vcol1.name == 'vcol1'
    vcol2 = graph.create_vertex_collection('vcol2')
    assert isinstance(vcol2, VertexCollection)
    assert vcol2.name == 'vcol2'
    ecol2 = graph.create_edge_definition(
        name='ecol2',
        from_collections=['vcol1'],
        to_collections=['vcol2']
    )
    assert isinstance(ecol1, EdgeCollection)
    assert ecol2.name == 'ecol2'
    assert graph.edge_definitions() == [
        {
            'name': 'ecol1',
            'from_collections': [],
            'to_collections': []
        },
        {
            'name': 'ecol2',
            'from_collections': ['vcol1'],
            'to_collections': ['vcol2']
        }
    ]
    assert 'ecol2' in set(c['name'] for c in db.collections())

    # Test create edge definition with missing vertex collection
    ecol3 = graph.create_edge_definition(
        name='ecol3',
        from_collections=['vcol3'],
        to_collections=['vcol3']
    )
    assert isinstance(ecol3, EdgeCollection)
    assert ecol3.name == 'ecol3'
    assert graph.edge_definitions() == [
        {
            'name': 'ecol1',
            'from_collections': [],
            'to_collections': []
        },
        {
            'name': 'ecol2',
            'from_collections': ['vcol1'],
            'to_collections': ['vcol2']
        },
        {
            'name': 'ecol3',
            'from_collections': ['vcol3'],
            'to_collections': ['vcol3']
        }
    ]
    assert 'vcol3' in graph.vertex_collections()
    assert 'vcol3' not in graph.orphan_collections()
    assert 'vcol3' in set(c['name'] for c in db.collections())
    assert 'ecol3' in set(c['name'] for c in db.collections())


@pytest.mark.order6
def test_list_edge_definitions():
    assert graph.edge_definitions() == [
        {
            'name': 'ecol1',
            'from_collections': [],
            'to_collections': []
        },
        {
            'name': 'ecol2',
            'from_collections': ['vcol1'],
            'to_collections': ['vcol2']
        },
        {
            'name': 'ecol3',
            'from_collections': ['vcol3'],
            'to_collections': ['vcol3']
        }
    ]

    # Test if exception is raised properly
    with pytest.raises(EdgeDefinitionListError):
        bad_graph.edge_definitions()


@pytest.mark.order7
def test_replace_edge_definition():
    assert graph.replace_edge_definition(
        name='ecol1',
        from_collections=['vcol3'],
        to_collections=['vcol2']
    ) is True
    assert graph.orphan_collections() == ['vcol1']
    assert graph.edge_definitions() == [
        {
            'name': 'ecol1',
            'from_collections': ['vcol3'],
            'to_collections': ['vcol2']
        },
        {
            'name': 'ecol2',
            'from_collections': ['vcol1'],
            'to_collections': ['vcol2']
        },
        {
            'name': 'ecol3',
            'from_collections': ['vcol3'],
            'to_collections': ['vcol3']
        }
    ]
    assert graph.replace_edge_definition(
        name='ecol2',
        from_collections=['vcol1'],
        to_collections=['vcol3']
    ) is True
    assert graph.orphan_collections() == []
    assert 'vcol3' not in graph.orphan_collections()
    assert graph.replace_edge_definition(
        name='ecol3',
        from_collections=['vcol4'],
        to_collections=['vcol4']
    ) is True
    with pytest.raises(EdgeDefinitionReplaceError):
        graph.replace_edge_definition(
            name='ecol4',
            from_collections=[],
            to_collections=['vcol1']
        )
    assert graph.edge_definitions() == [
        {
            'name': 'ecol1',
            'from_collections': ['vcol3'],
            'to_collections': ['vcol2']
        },
        {
            'name': 'ecol2',
            'from_collections': ['vcol1'],
            'to_collections': ['vcol3']
        },
        {
            'name': 'ecol3',
            'from_collections': ['vcol4'],
            'to_collections': ['vcol4']
        }
    ]
    assert graph.orphan_collections() == []


@pytest.mark.order8
def test_delete_edge_definition():
    assert graph.delete_edge_definition('ecol3') is True
    assert graph.edge_definitions() == [
        {
            'name': 'ecol1',
            'from_collections': ['vcol3'],
            'to_collections': ['vcol2']
        },
        {
            'name': 'ecol2',
            'from_collections': ['vcol1'],
            'to_collections': ['vcol3']
        }
    ]
    assert graph.orphan_collections() == ['vcol4']
    assert 'vcol4' in graph.vertex_collections()
    assert 'vcol4' in set(c['name'] for c in db.collections())
    assert 'ecol3' in set(c['name'] for c in db.collections())

    with pytest.raises(EdgeDefinitionDeleteError):
        graph.delete_edge_definition('ecol3')

    assert graph.delete_edge_definition('ecol1', purge=True) is True
    assert graph.edge_definitions() == [
        {
            'name': 'ecol2',
            'from_collections': ['vcol1'],
            'to_collections': ['vcol3']
        }
    ]
    assert sorted(graph.orphan_collections()) == ['vcol2', 'vcol4']
    assert 'ecol1' not in set(c['name'] for c in db.collections())
    assert 'ecol2' in set(c['name'] for c in db.collections())
    assert 'ecol3' in set(c['name'] for c in db.collections())


@pytest.mark.order9
def test_create_graph_with_vertices_ane_edges():
    new_graph_name = generate_graph_name()
    edge_definitions = [
        {
            'name': 'ecol1',
            'from_collections': ['vcol3'],
            'to_collections': ['vcol2']
        }
    ]
    new_graph = db.create_graph(
        new_graph_name,
        edge_definitions=edge_definitions,
        orphan_collections=['vcol1']
    )
    assert new_graph.edge_definitions() == edge_definitions
    assert new_graph.orphan_collections() == ['vcol1']


@pytest.mark.order10
def test_insert_vertex():
    vcol = graph.vertex_collection('vcol1')

    # Test preconditions
    assert '1' not in vcol
    assert len(vcol) == 0

    # Test insert first vertex
    result = vcol.insert(vertex1)
    assert result['_id'] == 'vcol1/1'
    assert result['_key'] == '1'
    assert isinstance(result['_rev'], string_types)
    assert '1' in vcol
    assert len(vcol) == 1
    assert vcol['1']['value'] == 1

    # Test insert vertex into missing collection
    with pytest.raises(DocumentInsertError):
        assert bad_vcol.insert(vertex2)
    assert '2' not in vcol
    assert len(vcol) == 1

    # Test insert duplicate vertex
    with pytest.raises(DocumentInsertError):
        assert vcol.insert(vertex1)
    assert len(vcol) == 1

    # Test insert second vertex
    result = vcol.insert(vertex2, sync=True)
    assert result['_id'] == 'vcol1/2'
    assert result['_key'] == '2'
    assert isinstance(result['_rev'], string_types)
    assert '2' in vcol
    assert len(vcol) == 2
    assert vcol['2']['value'] == 2

    # Test insert duplicate vertex second time
    with pytest.raises(DocumentInsertError):
        assert vcol.insert(vertex2)


@pytest.mark.order11
def test_get_vertex():
    vcol = graph.vertex_collection('vcol1')

    # Test get missing vertex
    assert vcol.get('0') is None

    # Test get existing vertex
    result = vcol.get('1')
    old_rev = result['_rev']
    assert clean_keys(result) == {'_key': '1', 'value': 1}

    # Test get existing vertex with wrong revision
    with pytest.raises(ArangoError):
        vcol.get('1', rev=old_rev + '1')

    # Test get existing vertex from missing vertex collection
    with pytest.raises(DocumentGetError):
        bad_vcol.get('1')

    # Test get existing vertex again
    assert clean_keys(vcol.get('2')) == {'_key': '2', 'value': 2}


@pytest.mark.order12
def test_update_vertex():
    vcol = graph.vertex_collection('vcol1')

    # Test update vertex with a single field change
    assert 'foo' not in vcol.get('1')
    result = vcol.update({'_key': '1', 'foo': 100})
    assert result['_id'] == 'vcol1/1'
    assert result['_key'] == '1'
    assert vcol['1']['foo'] == 100
    old_rev = vcol['1']['_rev']

    # Test update vertex with multiple field changes
    result = vcol.update({'_key': '1', 'foo': 200, 'bar': 300})
    assert result['_id'] == 'vcol1/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert vcol['1']['foo'] == 200
    assert vcol['1']['bar'] == 300
    old_rev = result['_rev']

    # Test update vertex with correct revision
    result = vcol.update({'_key': '1', '_rev': old_rev, 'bar': 400})
    assert result['_id'] == 'vcol1/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert vcol['1']['foo'] == 200
    assert vcol['1']['bar'] == 400
    old_rev = result['_rev']

    # Test update vertex with incorrect revision
    new_rev = old_rev + '1'
    with pytest.raises(DocumentRevisionError):
        vcol.update({'_key': '1', '_rev': new_rev, 'bar': 500})
    assert vcol['1']['foo'] == 200
    assert vcol['1']['bar'] == 400

    # Test update vertex in missing vertex collection
    with pytest.raises(DocumentUpdateError):
        bad_vcol.update({'_key': '1', 'bar': 500})
    assert vcol['1']['foo'] == 200
    assert vcol['1']['bar'] == 400

    # Test update vertex with sync option
    result = vcol.update({'_key': '1', 'bar': 500}, sync=True)
    assert result['_id'] == 'vcol1/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert vcol['1']['foo'] == 200
    assert vcol['1']['bar'] == 500
    old_rev = result['_rev']

    # Test update vertex with keep_none option
    result = vcol.update({'_key': '1', 'bar': None}, keep_none=True)
    assert result['_id'] == 'vcol1/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert vcol['1']['foo'] == 200
    assert vcol['1']['bar'] is None
    old_rev = result['_rev']

    # Test update vertex without keep_none option
    result = vcol.update({'_key': '1', 'foo': None}, keep_none=False)
    assert result['_id'] == 'vcol1/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert 'foo' not in vcol['1']
    assert vcol['1']['bar'] is None


@pytest.mark.order13
def test_replace_vertex():
    vcol = graph.vertex_collection('vcol1')

    # Test preconditions
    assert 'bar' in vcol.get('1')
    assert 'value' in vcol.get('1')

    # Test replace vertex with a single field change
    result = vcol.replace({'_key': '1', 'baz': 100})
    assert result['_id'] == 'vcol1/1'
    assert result['_key'] == '1'
    assert 'foo' not in vcol['1']
    assert 'bar' not in vcol['1']
    assert vcol['1']['baz'] == 100
    old_rev = result['_rev']

    # Test replace vertex with multiple field changes
    vertex = {'_key': '1', 'foo': 200, 'bar': 300}
    result = vcol.replace(vertex)
    assert result['_id'] == 'vcol1/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert clean_keys(vcol['1']) == vertex
    old_rev = result['_rev']

    # Test replace vertex with correct revision
    vertex = {'_key': '1', '_rev': old_rev, 'bar': 500}
    result = vcol.replace(vertex)
    assert result['_id'] == 'vcol1/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert clean_keys(vcol['1']) == clean_keys(vertex)
    old_rev = result['_rev']

    # Test replace vertex with incorrect revision
    new_rev = old_rev + '10'
    vertex = {'_key': '1', '_rev': new_rev, 'bar': 600}
    with pytest.raises(DocumentRevisionError):
        vcol.replace(vertex)
    assert vcol['1']['bar'] == 500
    assert 'foo' not in vcol['1']

    # Test replace vertex in missing vertex collection
    with pytest.raises(DocumentReplaceError):
        bad_vcol.replace({'_key': '1', 'bar': 600})
    assert vcol['1']['bar'] == 500
    assert 'foo' not in vcol['1']

    # Test replace vertex with sync option
    vertex = {'_key': '1', 'bar': 400, 'foo': 200}
    result = vcol.replace(vertex, sync=True)
    assert result['_id'] == 'vcol1/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert vcol['1']['foo'] == 200
    assert vcol['1']['bar'] == 400


@pytest.mark.order14
def test_delete_vertex():
    vcol = graph.vertex_collection('vcol1')
    vcol.truncate()

    vcol.insert(vertex1)
    vcol.insert(vertex2)
    vcol.insert(vertex3)

    # Test delete existing vertex
    assert vcol.delete(vertex1) is True
    assert vcol['1'] is None
    assert '1' not in vcol

    # Test delete existing vertex with sync
    assert vcol.delete(vertex3, sync=True) is True
    assert vcol['3'] is None
    assert '3' not in vcol

    # Test delete vertex with incorrect revision
    old_rev = vcol['2']['_rev']
    vertex2['_rev'] = old_rev + '10'
    with pytest.raises(DocumentRevisionError):
        vcol.delete(vertex2)
    assert '2' in vcol

    with pytest.raises(DocumentDeleteError):
        bad_vcol.delete({'_key': '10', '_rev': 'boo'}, ignore_missing=True)
    assert '2' in vcol

    # Test delete vertex from missing collection
    with pytest.raises(DocumentDeleteError):
        bad_vcol.delete(vertex1, ignore_missing=False)

    # Test delete missing vertex
    with pytest.raises(DocumentDeleteError):
        vcol.delete({'_key': '10'}, ignore_missing=False)

    # Test delete missing vertex while ignoring missing
    assert vcol.delete({'_key': '10'}, ignore_missing=True) is False


@pytest.mark.order15
def test_insert_edge():
    ecol = graph.edge_collection('ecol2')
    ecol.truncate()

    vcol1 = db.collection('vcol1')
    vcol1.truncate()
    vcol1.import_bulk([vertex1, vertex2, vertex3])

    vcol3 = db.collection('vcol3')
    vcol3.truncate()
    vcol3.import_bulk([vertex4, vertex5, vertex6])

    # Test preconditions
    assert '1' not in ecol
    assert len(ecol) == 0
    assert len(vcol1) == 3
    assert len(vcol3) == 3

    # Test insert first valid edge
    result = ecol.insert(edge1)
    assert result['_id'] == 'ecol2/1'
    assert result['_key'] == '1'
    assert isinstance(result['_rev'], string_types)
    assert '1' in ecol
    assert len(ecol) == 1
    assert ecol['1']['_from'] == 'vcol1/1'
    assert ecol['1']['_to'] == 'vcol3/4'

    # Test insert valid edge into missing collection
    with pytest.raises(DocumentInsertError):
        assert bad_ecol.insert(edge2)
    assert '2' not in ecol
    assert len(ecol) == 1

    # Test insert duplicate edge
    with pytest.raises(DocumentInsertError):
        assert ecol.insert(edge1)
    assert len(ecol) == 1

    # Test insert second valid edge
    result = ecol.insert(edge2, sync=True)
    assert result['_id'] == 'ecol2/2'
    assert result['_key'] == '2'
    assert '2' in ecol
    assert len(ecol) == 2
    assert ecol['2']['_from'] == 'vcol1/1'
    assert ecol['2']['_to'] == 'vcol3/5'
    old_rev = result['_rev']

    # Test insert duplicate edge second time
    with pytest.raises(DocumentInsertError):
        assert ecol.insert(edge2)
    assert ecol['2']['_from'] == 'vcol1/1'
    assert ecol['2']['_to'] == 'vcol3/5'
    assert ecol['2']['_rev'] == old_rev

    # Test insert invalid edge (from and to mixed up)
    with pytest.raises(DocumentInsertError):
        ecol.insert(edge3)
    assert ecol['2']['_from'] == 'vcol1/1'
    assert ecol['2']['_to'] == 'vcol3/5'
    assert ecol['2']['_rev'] == old_rev

    # Test insert invalid edge (missing vertices)
    result = ecol.insert(edge4)
    assert result['_id'] == 'ecol2/4'
    assert result['_key'] == '4'
    assert isinstance(result['_rev'], string_types)
    assert '4' in ecol
    assert len(ecol) == 3
    assert ecol['4']['_from'] == 'vcol1/8'
    assert ecol['4']['_to'] == 'vcol3/7'
    assert len(vcol1) == 3
    assert len(vcol3) == 3
    assert '4' not in vcol1
    assert 'd' not in vcol3


@pytest.mark.order16
def test_get_edge():
    ecol = graph.edge_collection('ecol2')
    ecol.truncate()
    for edge in [edge1, edge2, edge4]:
        ecol.insert(edge)

    # Test get missing edge
    assert ecol.get('0') is None

    # Test get existing edge
    result = ecol.get('1')
    old_rev = result['_rev']
    assert clean_keys(result) == edge1

    # Test get existing edge with wrong revision
    with pytest.raises(DocumentRevisionError):
        ecol.get('1', rev=old_rev + '1')

    # Test get existing edge from missing edge collection
    with pytest.raises(DocumentGetError):
        bad_ecol.get('1')

    # Test get existing edge again
    assert clean_keys(ecol.get('2')) == edge2


@pytest.mark.order17
def test_update_edge():
    ecol = graph.edge_collection('ecol2')
    ecol.truncate()
    ecol.insert(edge1)

    # Test update edge with a single field change
    assert 'foo' not in ecol.get('1')
    result = ecol.update({'_key': '1', 'foo': 100})
    assert result['_id'] == 'ecol2/1'
    assert result['_key'] == '1'
    assert ecol['1']['foo'] == 100
    old_rev = ecol['1']['_rev']

    # Test update edge with multiple field changes
    result = ecol.update({'_key': '1', 'foo': 200, 'bar': 300})
    assert result['_id'] == 'ecol2/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert ecol['1']['foo'] == 200
    assert ecol['1']['bar'] == 300
    old_rev = result['_rev']

    # Test update edge with correct revision
    result = ecol.update({'_key': '1', '_rev': old_rev, 'bar': 400})
    assert result['_id'] == 'ecol2/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert ecol['1']['foo'] == 200
    assert ecol['1']['bar'] == 400
    old_rev = result['_rev']

    # Test update edge with incorrect revision
    new_rev = old_rev + '1'
    with pytest.raises(DocumentRevisionError):
        ecol.update({'_key': '1', '_rev': new_rev, 'bar': 500})
    assert ecol['1']['foo'] == 200
    assert ecol['1']['bar'] == 400

    # Test update edge in missing edge collection
    with pytest.raises(DocumentUpdateError):
        bad_ecol.update({'_key': '1', 'bar': 500})
    assert ecol['1']['foo'] == 200
    assert ecol['1']['bar'] == 400

    # Test update edge with sync option
    result = ecol.update({'_key': '1', 'bar': 500}, sync=True)
    assert result['_id'] == 'ecol2/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert ecol['1']['foo'] == 200
    assert ecol['1']['bar'] == 500
    old_rev = result['_rev']

    # Test update edge without keep_none option
    result = ecol.update({'_key': '1', 'bar': None}, keep_none=True)
    assert result['_id'] == 'ecol2/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert ecol['1']['foo'] == 200
    assert ecol['1']['bar'] is None
    old_rev = result['_rev']

    # Test update edge with keep_none option
    result = ecol.update({'_key': '1', 'foo': None}, keep_none=False)
    assert result['_id'] == 'ecol2/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert 'foo' not in ecol['1']
    assert ecol['1']['bar'] is None
    old_rev = result['_rev']

    # Test update edge to a valid edge
    result = ecol.update(edge5)
    assert result['_id'] == 'ecol2/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert ecol['1']['_from'] == 'vcol1/1'
    assert ecol['1']['_to'] == 'vcol3/5'
    old_rev = result['_rev']

    # Test update edge to a missing edge
    result = ecol.update(edge7)
    assert result['_id'] == 'ecol2/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert ecol['1']['_from'] == 'vcol1/8'
    assert ecol['1']['_to'] == 'vcol3/7'
    old_rev = result['_rev']

    # TODO why is this succeeding?
    # Test update edge to a invalid edge (from and to mixed up)
    result = ecol.update(edge6)
    assert result['_id'] == 'ecol2/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert ecol['1']['_from'] == 'vcol3/6'
    assert ecol['1']['_to'] == 'vcol1/2'
    assert ecol['1']['_rev'] != old_rev


@pytest.mark.order18
def test_replace_edge():
    ecol = graph.edge_collection('ecol2')
    ecol.truncate()
    ecol.insert(edge1)

    edge = edge1.copy()

    # Test replace edge with a single field change
    assert 'foo' not in ecol.get('1')
    edge['foo'] = 100
    result = ecol.replace(edge)
    assert result['_id'] == 'ecol2/1'
    assert result['_key'] == '1'
    assert ecol['1']['foo'] == 100
    old_rev = ecol['1']['_rev']

    # Test replace edge with multiple field changes
    edge['foo'] = 200
    edge['bar'] = 300
    result = ecol.replace(edge)
    assert result['_id'] == 'ecol2/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert ecol['1']['foo'] == 200
    assert ecol['1']['bar'] == 300
    old_rev = result['_rev']

    # Test replace edge with correct revision
    edge['foo'] = 300
    edge['bar'] = 400
    edge['_rev'] = old_rev
    result = ecol.replace(edge)
    assert result['_id'] == 'ecol2/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert ecol['1']['foo'] == 300
    assert ecol['1']['bar'] == 400
    old_rev = result['_rev']

    # Test replace edge with incorrect revision
    edge['bar'] = 500
    edge['_rev'] = old_rev + '1'
    with pytest.raises(DocumentRevisionError):
        ecol.replace(edge)
    assert ecol['1']['foo'] == 300
    assert ecol['1']['bar'] == 400

    # Test replace edge in missing edge collection
    with pytest.raises(DocumentReplaceError):
        bad_ecol.replace(edge)
    assert ecol['1']['foo'] == 300
    assert ecol['1']['bar'] == 400

    # Test replace edge with sync option
    edge['_rev'] = None
    result = ecol.replace(edge, sync=True)
    assert result['_id'] == 'ecol2/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert ecol['1']['foo'] == 300
    assert ecol['1']['bar'] == 500
    old_rev = result['_rev']

    # Test replace edge to a valid edge
    result = ecol.replace(edge5)
    assert result['_id'] == 'ecol2/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert ecol['1']['_from'] == 'vcol1/1'
    assert ecol['1']['_to'] == 'vcol3/5'
    old_rev = result['_rev']

    # Test replace edge to a missing edge
    result = ecol.replace(edge7)
    assert result['_id'] == 'ecol2/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert ecol['1']['_from'] == 'vcol1/8'
    assert ecol['1']['_to'] == 'vcol3/7'
    old_rev = result['_rev']

    # TODO why is this succeeding?
    # Test replace edge to a invalid edge (from and to mixed up)
    result = ecol.replace(edge6)
    assert result['_id'] == 'ecol2/1'
    assert result['_key'] == '1'
    assert result['_old_rev'] == old_rev
    assert ecol['1']['_from'] == 'vcol3/6'
    assert ecol['1']['_to'] == 'vcol1/2'
    assert ecol['1']['_rev'] != old_rev


@pytest.mark.order19
def test_delete_edge():
    ecol = graph.edge_collection('ecol2')
    ecol.truncate()
    for edge in [edge1, edge2, edge4]:
        ecol.insert(edge)

    # Test delete existing edge
    assert ecol.delete(edge1) is True
    assert ecol['1'] is None
    assert '1' not in ecol

    # Test delete existing edge with sync
    assert ecol.delete(edge4, sync=True) is True
    assert ecol['3'] is None
    assert '3' not in ecol

    # Test delete edge with incorrect revision
    old_rev = ecol['2']['_rev']
    edge2['_rev'] = old_rev + '1'
    with pytest.raises(DocumentRevisionError):
        ecol.delete(edge2)
    assert '2' in ecol

    # Test delete edge from missing collection
    with pytest.raises(DocumentDeleteError):
        bad_ecol.delete(edge1, ignore_missing=False)

    # Test delete missing edge
    with pytest.raises(DocumentDeleteError):
        ecol.delete(edge3, ignore_missing=False)

    # Test delete missing edge while ignoring missing
    assert not ecol.delete(edge3, ignore_missing=True)


@pytest.mark.order20
def test_traverse():
    # Create test graph, vertex and edge collections
    curriculum = db.create_graph('curriculum')
    professors = curriculum.create_vertex_collection('profs')
    classes = curriculum.create_vertex_collection('classes')
    teaches = curriculum.create_edge_definition(
        name='teaches',
        from_collections=['profs'],
        to_collections=['classes']
    )
    # Insert test vertices into the graph
    professors.insert({'_key': 'anna', 'name': 'Professor Anna'})
    professors.insert({'_key': 'andy', 'name': 'Professor Andy'})
    classes.insert({'_key': 'CSC101', 'name': 'Introduction to CS'})
    classes.insert({'_key': 'MAT223', 'name': 'Linear Algebra'})
    classes.insert({'_key': 'STA201', 'name': 'Statistics'})
    classes.insert({'_key': 'MAT101', 'name': 'Calculus I'})
    classes.insert({'_key': 'MAT102', 'name': 'Calculus II'})

    # Insert test edges into the graph
    teaches.insert({'_from': 'profs/anna', '_to': 'classes/CSC101'})
    teaches.insert({'_from': 'profs/anna', '_to': 'classes/STA201'})
    teaches.insert({'_from': 'profs/anna', '_to': 'classes/MAT223'})
    teaches.insert({'_from': 'profs/andy', '_to': 'classes/MAT101'})
    teaches.insert({'_from': 'profs/andy', '_to': 'classes/MAT102'})
    teaches.insert({'_from': 'profs/andy', '_to': 'classes/MAT223'})

    # Traverse the graph with default settings
    result = curriculum.traverse(start_vertex='profs/anna')
    assert set(result) == {'paths', 'vertices'}
    for path in result['paths']:
        for vertex in path['vertices']:
            assert set(vertex) == {'_id', '_key', '_rev', 'name'}
        for edge in path['edges']:
            assert set(edge) == {'_id', '_key', '_rev', '_to', '_from'}
    visited_vertices = sorted([v['_key'] for v in result['vertices']])
    assert visited_vertices == ['CSC101', 'MAT223', 'STA201', 'anna']
    result = curriculum.traverse(start_vertex='profs/andy')
    visited_vertices = sorted([v['_key'] for v in result['vertices']])
    assert visited_vertices == ['MAT101', 'MAT102', 'MAT223', 'andy']

    # Traverse the graph with an invalid start vertex
    with pytest.raises(GraphTraverseError):
        curriculum.traverse(start_vertex='invalid')
    with pytest.raises(GraphTraverseError):
        curriculum.traverse(start_vertex='students/hanna')
    with pytest.raises(GraphTraverseError):
        curriculum.traverse(start_vertex='profs/anderson')

    # Travers the graph with max iteration of 0
    with pytest.raises(GraphTraverseError):
        curriculum.traverse(start_vertex='profs/andy', max_iter=0)

    # Traverse the graph with max depth of 0
    result = curriculum.traverse(start_vertex='profs/andy', max_depth=0)
    visited_vertices = sorted([v['_key'] for v in result['vertices']])
    assert visited_vertices == ['andy']
    result = curriculum.traverse(start_vertex='profs/anna', max_depth=0)
    visited_vertices = sorted([v['_key'] for v in result['vertices']])
    assert visited_vertices == ['anna']

    # Traverse the graph with min depth of 2
    result = curriculum.traverse(start_vertex='profs/andy', min_depth=2)
    visited_vertices = sorted([v['_key'] for v in result['vertices']])
    assert visited_vertices == []
    result = curriculum.traverse(start_vertex='profs/anna', min_depth=2)
    visited_vertices = sorted([v['_key'] for v in result['vertices']])
    assert visited_vertices == []

    # Traverse the graph with DFS and BFS
    result = curriculum.traverse(
        start_vertex='profs/anna',
        strategy='dfs',
        direction='any',
    )
    dfs_vertices = [v['_key'] for v in result['vertices']]
    result = curriculum.traverse(
        start_vertex='profs/anna',
        strategy='bfs',
        direction='any'
    )
    bfs_vertices = [v['_key'] for v in result['vertices']]
    assert dfs_vertices != bfs_vertices  # the order should be different
    assert sorted(dfs_vertices) == sorted(bfs_vertices)

    # Traverse the graph with filter function
    result = curriculum.traverse(
        start_vertex='profs/andy',
        filter_func='if (vertex._key == "MAT101") {return "exclude";} return;'
    )
    visited_vertices = sorted([v['_key'] for v in result['vertices']])
    assert visited_vertices == ['MAT102', 'MAT223', 'andy']

    # Traverse the graph with uniqueness (should be same as before)
    result = curriculum.traverse(
        start_vertex='profs/andy',
        vertex_uniqueness='global',
        edge_uniqueness='global',
        filter_func='if (vertex._key == "MAT101") {return "exclude";} return;'
    )
    visited_vertices = sorted([v['_key'] for v in result['vertices']])
    assert visited_vertices == ['MAT102', 'MAT223', 'andy']
