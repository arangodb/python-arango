from arango.collection import EdgeCollection
from arango.exceptions import (
    DocumentDeleteError,
    DocumentGetError,
    DocumentInsertError,
    DocumentParseError,
    DocumentReplaceError,
    DocumentRevisionError,
    DocumentUpdateError,
    EdgeDefinitionCreateError,
    EdgeDefinitionDeleteError,
    EdgeDefinitionListError,
    EdgeDefinitionReplaceError,
    EdgeListError,
    GraphCreateError,
    GraphDeleteError,
    GraphListError,
    GraphPropertiesError,
    GraphTraverseError,
    VertexCollectionCreateError,
    VertexCollectionDeleteError,
    VertexCollectionListError,
)
from tests.helpers import (
    assert_raises,
    clean_doc,
    empty_collection,
    extract,
    generate_col_name,
    generate_doc_key,
    generate_graph_name,
)


def test_graph_properties(graph, bad_graph, db):
    assert repr(graph) == f"<Graph {graph.name}>"

    properties = graph.properties()

    assert properties["id"] == f"_graphs/{graph.name}"
    assert properties["name"] == graph.name
    assert len(properties["edge_definitions"]) == 1
    assert "orphan_collections" in properties
    assert isinstance(properties["revision"], str)

    # Test properties with bad database
    with assert_raises(GraphPropertiesError):
        bad_graph.properties()

    new_graph_name = generate_graph_name()
    new_graph = db.create_graph(new_graph_name)
    properties = new_graph.properties()
    assert properties["id"] == f"_graphs/{new_graph_name}"
    assert properties["name"] == new_graph_name
    assert properties["edge_definitions"] == []
    assert properties["orphan_collections"] == []
    assert isinstance(properties["revision"], str)


def test_graph_provision(graph, db):
    vertices = [{"foo": i} for i in range(1, 101)]
    edges = [
        {"_from": f"numbers/{j}", "_to": f"numbers/{i}", "result": j / i}
        for i in range(1, 101)
        for j in range(1, 101)
        if j % i == 0
    ]
    e_d = [
        {
            "edge_collection": "is_divisible_by",
            "from_vertex_collections": ["numbers"],
            "to_vertex_collections": ["numbers"],
        }
    ]
    graph = db.create_graph(
        name="DivisibilityGraph",
        edge_definitions=e_d,
        collections={
            "numbers": {"docs": vertices, "options": {"batch_size": 5}},
            "is_divisible_by": {"docs": edges, "options": {"sync": True}},
        },
    )

    assert graph.vertex_collection("numbers").count() == len(vertices)
    assert graph.edge_collection("is_divisible_by").count() == len(edges)


def test_graph_management(db, bad_db):
    # Test create graph
    graph_name = generate_graph_name()
    assert db.has_graph(graph_name) is False

    graph = db.create_graph(graph_name)
    assert db.has_graph(graph_name) is True
    assert graph.name == graph_name
    assert graph.db_name == db.name

    # Test create duplicate graph
    with assert_raises(GraphCreateError) as err:
        db.create_graph(graph_name)
    assert err.value.error_code == 1925

    # Test get graph
    result = db.graph(graph_name)
    assert result.name == graph.name
    assert result.db_name == graph.db_name

    # Test get graphs
    result = db.graphs()
    for entry in result:
        assert "revision" in entry
        assert "edge_definitions" in entry
        assert "orphan_collections" in entry
    assert graph_name in extract("name", db.graphs())

    # Test list graphs with bad database
    with assert_raises(GraphListError) as err:
        bad_db.graphs()
    assert err.value.error_code in {11, 1228}

    # Test has graph with bad database
    with assert_raises(GraphListError) as err:
        bad_db.has_graph(graph_name)
    assert err.value.error_code in {11, 1228}

    # Test delete graph
    assert db.delete_graph(graph_name) is True
    assert graph_name not in extract("name", db.graphs())

    # Test delete missing graph
    with assert_raises(GraphDeleteError) as err:
        db.delete_graph(graph_name)
    assert err.value.error_code == 1924
    assert db.delete_graph(graph_name, ignore_missing=True) is False

    # Create a graph with vertex and edge collections and delete the graph
    graph = db.create_graph(graph_name)
    ecol_name = generate_col_name()
    fvcol_name = generate_col_name()
    tvcol_name = generate_col_name()

    graph.create_vertex_collection(fvcol_name)
    graph.create_vertex_collection(tvcol_name)
    graph.create_edge_definition(
        edge_collection=ecol_name,
        from_vertex_collections=[fvcol_name],
        to_vertex_collections=[tvcol_name],
    )
    collections = extract("name", db.collections())
    assert fvcol_name in collections
    assert tvcol_name in collections
    assert ecol_name in collections

    db.delete_graph(graph_name)
    collections = extract("name", db.collections())
    assert fvcol_name in collections
    assert tvcol_name in collections
    assert ecol_name in collections

    # Create a graph with vertex and edge collections and delete all
    graph = db.create_graph(graph_name)
    graph.create_edge_definition(
        edge_collection=ecol_name,
        from_vertex_collections=[fvcol_name],
        to_vertex_collections=[tvcol_name],
    )
    db.delete_graph(graph_name, drop_collections=True)
    collections = extract("name", db.collections())
    assert fvcol_name not in collections
    assert tvcol_name not in collections
    assert ecol_name not in collections


def test_vertex_collection_management(db, graph, bad_graph):
    # Test create valid "from" vertex collection
    fvcol_name = generate_col_name()
    assert not graph.has_vertex_collection(fvcol_name)
    assert not db.has_collection(fvcol_name)

    fvcol = graph.create_vertex_collection(fvcol_name)
    assert graph.has_vertex_collection(fvcol_name)
    assert db.has_collection(fvcol_name)
    assert fvcol.name == fvcol_name
    assert fvcol.graph == graph.name
    assert fvcol_name in repr(fvcol)
    assert fvcol_name in graph.vertex_collections()
    assert fvcol_name in extract("name", db.collections())

    # Test has vertex collection with bad graph
    with assert_raises(VertexCollectionListError) as err:
        bad_graph.has_vertex_collection(fvcol_name)
    assert err.value.error_code in {11, 1228}

    # Test create duplicate vertex collection
    with assert_raises(VertexCollectionCreateError) as err:
        graph.create_vertex_collection(fvcol_name)
    assert err.value.error_code == 1938
    assert fvcol_name in graph.vertex_collections()
    assert fvcol_name in extract("name", db.collections())

    # Test create valid "to" vertex collection
    tvcol_name = generate_col_name()
    assert not graph.has_vertex_collection(tvcol_name)
    assert not db.has_collection(tvcol_name)

    tvcol = graph.create_vertex_collection(tvcol_name)
    assert graph.has_vertex_collection(tvcol_name)
    assert db.has_collection(tvcol_name)
    assert tvcol_name == tvcol_name
    assert tvcol.graph == graph.name
    assert tvcol_name in repr(tvcol)
    assert tvcol_name in graph.vertex_collections()
    assert tvcol_name in extract("name", db.collections())

    # Test list vertex collection via bad database
    with assert_raises(VertexCollectionListError) as err:
        bad_graph.vertex_collections()
    assert err.value.error_code in {11, 1228}

    # Test delete missing vertex collection
    with assert_raises(VertexCollectionDeleteError) as err:
        graph.delete_vertex_collection(generate_col_name())
    assert err.value.error_code in {1926, 1928}

    # Test delete "to" vertex collection with purge option
    assert graph.delete_vertex_collection(tvcol_name, purge=True) is True
    assert tvcol_name not in graph.vertex_collections()
    assert fvcol_name in extract("name", db.collections())
    assert tvcol_name not in extract("name", db.collections())
    assert not graph.has_vertex_collection(tvcol_name)

    # Test delete "from" vertex collection without purge option
    assert graph.delete_vertex_collection(fvcol_name, purge=False) is True
    assert fvcol_name not in graph.vertex_collections()
    assert fvcol_name in extract("name", db.collections())
    assert not graph.has_vertex_collection(fvcol_name)


def test_edge_definition_management(db, graph, bad_graph):
    ecol_name = generate_col_name()
    assert not graph.has_edge_definition(ecol_name)
    assert not graph.has_edge_collection(ecol_name)
    assert not db.has_collection(ecol_name)

    # Test create edge definition with existing vertex collections
    fvcol_name = generate_col_name()
    tvcol_name = generate_col_name()
    ecol_name = generate_col_name()
    ecol = graph.create_edge_definition(
        edge_collection=ecol_name,
        from_vertex_collections=[fvcol_name],
        to_vertex_collections=[tvcol_name],
    )
    assert ecol.name == ecol_name
    assert ecol.graph == graph.name
    assert repr(ecol) == f"<EdgeCollection {ecol.name}>"
    assert {
        "edge_collection": ecol_name,
        "from_vertex_collections": [fvcol_name],
        "to_vertex_collections": [tvcol_name],
    } in graph.edge_definitions()
    assert ecol_name in extract("name", db.collections())

    vertex_collections = graph.vertex_collections()
    assert fvcol_name in vertex_collections
    assert tvcol_name in vertex_collections

    # Test has edge definition with bad graph
    with assert_raises(EdgeDefinitionListError) as err:
        bad_graph.has_edge_definition(ecol_name)
    assert err.value.error_code in {11, 1228}

    # Test create duplicate edge definition
    with assert_raises(EdgeDefinitionCreateError) as err:
        graph.create_edge_definition(
            edge_collection=ecol_name,
            from_vertex_collections=[fvcol_name],
            to_vertex_collections=[tvcol_name],
        )
    assert err.value.error_code == 1920

    # Test create edge definition with missing vertex collection
    bad_vcol_name = generate_col_name()
    ecol_name = generate_col_name()
    ecol = graph.create_edge_definition(
        edge_collection=ecol_name,
        from_vertex_collections=[bad_vcol_name],
        to_vertex_collections=[bad_vcol_name],
    )
    assert graph.has_edge_definition(ecol_name)
    assert graph.has_edge_collection(ecol_name)
    assert ecol.name == ecol_name
    assert {
        "edge_collection": ecol_name,
        "from_vertex_collections": [bad_vcol_name],
        "to_vertex_collections": [bad_vcol_name],
    } in graph.edge_definitions()
    assert bad_vcol_name in graph.vertex_collections()
    assert bad_vcol_name in extract("name", db.collections())
    assert bad_vcol_name in extract("name", db.collections())

    # Test list edge definition with bad database
    with assert_raises(EdgeDefinitionListError) as err:
        bad_graph.edge_definitions()
    assert err.value.error_code in {11, 1228}

    # Test replace edge definition (happy path)
    ecol = graph.replace_edge_definition(
        edge_collection=ecol_name,
        from_vertex_collections=[tvcol_name],
        to_vertex_collections=[fvcol_name],
    )
    assert isinstance(ecol, EdgeCollection)
    assert ecol.name == ecol_name
    assert {
        "edge_collection": ecol_name,
        "from_vertex_collections": [tvcol_name],
        "to_vertex_collections": [fvcol_name],
    } in graph.edge_definitions()

    # Test replace missing edge definition
    bad_ecol_name = generate_col_name()
    with assert_raises(EdgeDefinitionReplaceError):
        graph.replace_edge_definition(
            edge_collection=bad_ecol_name,
            from_vertex_collections=[],
            to_vertex_collections=[fvcol_name],
        )

    # Test delete missing edge definition
    with assert_raises(EdgeDefinitionDeleteError) as err:
        graph.delete_edge_definition(bad_ecol_name)
    assert err.value.error_code == 1930

    # Test delete existing edge definition with purge
    assert graph.delete_edge_definition(ecol_name, purge=True) is True
    assert ecol_name not in extract("edge_collection", graph.edge_definitions())
    assert not graph.has_edge_definition(ecol_name)
    assert not graph.has_edge_collection(ecol_name)
    assert ecol_name not in extract("name", db.collections())


def test_create_graph_with_edge_definition(db):
    new_graph_name = generate_graph_name()
    new_ecol_name = generate_col_name()
    fvcol_name = generate_col_name()
    tvcol_name = generate_col_name()
    ovcol_name = generate_col_name()

    edge_definition = {
        "edge_collection": new_ecol_name,
        "from_vertex_collections": [fvcol_name],
        "to_vertex_collections": [tvcol_name],
    }
    new_graph = db.create_graph(
        new_graph_name,
        edge_definitions=[edge_definition],
        orphan_collections=[ovcol_name],
    )
    assert edge_definition in new_graph.edge_definitions()


def test_vertex_management(fvcol, bad_fvcol, fvdocs):
    # Test insert vertex with no key
    result = fvcol.insert({})
    assert result["_key"] in fvcol
    assert len(fvcol) == 1
    empty_collection(fvcol)

    # Test insert vertex with ID
    vertex_id = fvcol.name + "/" + "foo"
    fvcol.insert({"_id": vertex_id})
    assert "foo" in fvcol
    assert vertex_id in fvcol
    assert len(fvcol) == 1
    empty_collection(fvcol)

    # Test insert vertex with return_new set to True
    result = fvcol.insert({"_id": vertex_id}, return_new=True)
    assert "new" in result
    assert "vertex" in result
    assert len(fvcol) == 1
    empty_collection(fvcol)

    with assert_raises(DocumentParseError) as err:
        fvcol.insert({"_id": generate_col_name() + "/" + "foo"})
    assert "bad collection name" in err.value.message

    vertex = fvdocs[0]
    key = vertex["_key"]

    # Test insert first valid vertex
    result = fvcol.insert(vertex, sync=True)
    assert result["_key"] == key
    assert "_rev" in result
    assert vertex in fvcol and key in fvcol
    assert len(fvcol) == 1
    assert fvcol[key]["val"] == vertex["val"]

    # Test insert duplicate vertex
    with assert_raises(DocumentInsertError) as err:
        fvcol.insert(vertex)
    assert err.value.error_code in {1202, 1210}
    assert len(fvcol) == 1

    vertex = fvdocs[1]
    key = vertex["_key"]

    # Test insert second valid vertex
    result = fvcol.insert(vertex)
    assert result["_key"] == key
    assert "_rev" in result
    assert vertex in fvcol and key in fvcol
    assert len(fvcol) == 2
    assert fvcol[key]["val"] == vertex["val"]

    vertex = fvdocs[2]
    key = vertex["_key"]

    # Test insert third valid vertex with silent set to True
    assert fvcol.insert(vertex, silent=True) is True
    assert len(fvcol) == 3
    assert fvcol[key]["val"] == vertex["val"]

    # Test get missing vertex
    if fvcol.context != "transaction":
        assert fvcol.get(generate_doc_key()) is None

    # Test get existing edge by body with "_key" field
    result = fvcol.get({"_key": key})
    assert clean_doc(result) == vertex

    # Test get existing edge by body with "_id" field
    result = fvcol.get({"_id": fvcol.name + "/" + key})
    assert clean_doc(result) == vertex

    # Test get existing vertex by key
    result = fvcol.get(key)
    assert clean_doc(result) == vertex

    # Test get existing vertex by ID
    result = fvcol.get(fvcol.name + "/" + key)
    assert clean_doc(result) == vertex

    # Test get existing vertex with bad revision
    old_rev = result["_rev"]
    with assert_raises(DocumentRevisionError) as err:
        fvcol.get(key, rev=old_rev + "1", check_rev=True)
    assert err.value.error_code in {1903, 1200}

    # Test get existing vertex with bad database
    with assert_raises(DocumentGetError) as err:
        bad_fvcol.get(key)
    assert err.value.error_code in {11, 1228}

    # Test update vertex with a single field change
    assert "foo" not in fvcol.get(key)
    result = fvcol.update({"_key": key, "foo": 100})
    assert result["_key"] == key
    assert fvcol[key]["foo"] == 100
    old_rev = fvcol[key]["_rev"]

    # Test update vertex with return_new and return_old set to True
    result = fvcol.update({"_key": key, "foo": 100}, return_old=True, return_new=True)
    assert "old" in result
    assert "new" in result
    assert "vertex" in result

    # Test update vertex with silent set to True
    assert "bar" not in fvcol[vertex]
    assert fvcol.update({"_key": key, "bar": 200}, silent=True) is True
    assert fvcol[vertex]["bar"] == 200
    assert fvcol[vertex]["_rev"] != old_rev
    old_rev = fvcol[key]["_rev"]

    # Test update vertex with multiple field changes
    result = fvcol.update({"_key": key, "foo": 200, "bar": 300})
    assert result["_key"] == key
    assert result["_old_rev"] == old_rev
    assert fvcol[key]["foo"] == 200
    assert fvcol[key]["bar"] == 300
    old_rev = result["_rev"]

    # Test update vertex with correct revision
    result = fvcol.update({"_key": key, "_rev": old_rev, "bar": 400})
    assert result["_key"] == key
    assert result["_old_rev"] == old_rev
    assert fvcol[key]["foo"] == 200
    assert fvcol[key]["bar"] == 400
    old_rev = result["_rev"]

    # Test update vertex with bad revision
    if fvcol.context != "transaction":
        new_rev = old_rev + "1"
        with assert_raises(DocumentRevisionError) as err:
            fvcol.update({"_key": key, "_rev": new_rev, "bar": 500})
        assert err.value.error_code in {1200, 1903}
        assert fvcol[key]["foo"] == 200
        assert fvcol[key]["bar"] == 400

    # Test update vertex in missing vertex collection
    with assert_raises(DocumentUpdateError) as err:
        bad_fvcol.update({"_key": key, "bar": 500})
    assert err.value.error_code in {11, 1228}
    assert fvcol[key]["foo"] == 200
    assert fvcol[key]["bar"] == 400

    # Test update vertex with sync set to True
    result = fvcol.update({"_key": key, "bar": 500}, sync=True)
    assert result["_key"] == key
    assert result["_old_rev"] == old_rev
    assert fvcol[key]["foo"] == 200
    assert fvcol[key]["bar"] == 500
    old_rev = result["_rev"]

    # Test update vertex with keep_none set to True
    result = fvcol.update({"_key": key, "bar": None}, keep_none=True)
    assert result["_key"] == key
    assert result["_old_rev"] == old_rev
    assert fvcol[key]["foo"] == 200
    assert fvcol[key]["bar"] is None
    old_rev = result["_rev"]

    # Test update vertex with keep_none set to False
    result = fvcol.update({"_key": key, "foo": None}, keep_none=False)
    assert result["_key"] == key
    assert result["_old_rev"] == old_rev
    assert "foo" not in fvcol[key]
    assert fvcol[key]["bar"] is None

    # Test replace vertex with a single field change
    result = fvcol.replace({"_key": key, "baz": 100})
    assert result["_key"] == key
    assert "foo" not in fvcol[key]
    assert "bar" not in fvcol[key]
    assert fvcol[key]["baz"] == 100
    old_rev = result["_rev"]

    # Test replace vertex with return_new and return_old set to True
    result = fvcol.replace({"_key": key, "baz": 100}, return_old=True, return_new=True)
    assert "old" in result
    assert "new" in result
    assert "vertex" in result

    # Test replace vertex with silent set to True
    assert fvcol.replace({"_key": key, "bar": 200}, silent=True) is True
    assert "foo" not in fvcol[key]
    assert "baz" not in fvcol[vertex]
    assert fvcol[vertex]["bar"] == 200
    assert len(fvcol) == 3
    assert fvcol[vertex]["_rev"] != old_rev
    old_rev = fvcol[vertex]["_rev"]

    # Test replace vertex with multiple field changes
    vertex = {"_key": key, "foo": 200, "bar": 300}
    result = fvcol.replace(vertex)
    assert result["_key"] == key
    assert result["_old_rev"] == old_rev
    assert clean_doc(fvcol[key]) == vertex
    old_rev = result["_rev"]

    # Test replace vertex with correct revision
    vertex = {"_key": key, "_rev": old_rev, "bar": 500}
    result = fvcol.replace(vertex)
    assert result["_key"] == key
    assert result["_old_rev"] == old_rev
    assert clean_doc(fvcol[key]) == clean_doc(vertex)
    old_rev = result["_rev"]

    # Test replace vertex with bad revision
    if fvcol.context != "transaction":
        new_rev = old_rev + "10"
        vertex = {"_key": key, "_rev": new_rev, "bar": 600}
        with assert_raises(DocumentRevisionError, DocumentReplaceError) as err:
            fvcol.replace(vertex)
        assert err.value.error_code in {1200, 1903}
        assert fvcol[key]["bar"] == 500
        assert "foo" not in fvcol[key]

    # Test replace vertex with bad database
    with assert_raises(DocumentReplaceError) as err:
        bad_fvcol.replace({"_key": key, "bar": 600})
    assert err.value.error_code in {11, 1228}
    assert fvcol[key]["bar"] == 500
    assert "foo" not in fvcol[key]

    # Test replace vertex with sync set to True
    vertex = {"_key": key, "bar": 400, "foo": 200}
    result = fvcol.replace(vertex, sync=True)
    assert result["_key"] == key
    assert result["_old_rev"] == old_rev
    assert fvcol[key]["foo"] == 200
    assert fvcol[key]["bar"] == 400

    # Test delete vertex with bad revision
    if fvcol.context != "transaction":
        old_rev = fvcol[key]["_rev"]
        vertex["_rev"] = old_rev + "1"
        with assert_raises(DocumentRevisionError, DocumentDeleteError) as err:
            fvcol.delete(vertex, check_rev=True)
        assert err.value.error_code in {1200, 1903}
        vertex["_rev"] = old_rev
        assert vertex in fvcol

    # Test delete missing vertex
    bad_key = generate_doc_key()
    with assert_raises(DocumentDeleteError) as err:
        fvcol.delete(bad_key, ignore_missing=False)
    assert err.value.error_code == 1202
    if fvcol.context != "transaction":
        assert fvcol.delete(bad_key, ignore_missing=True) is False

    # Test delete existing vertex with sync set to True
    assert fvcol.delete(vertex, sync=True, check_rev=False) is True
    if fvcol.context != "transaction":
        assert fvcol[vertex] is None
    assert vertex not in fvcol
    assert len(fvcol) == 2

    # Test delete existing vertex with return_old set to True
    vertex = fvdocs[1]
    result = fvcol.delete(vertex, return_old=True)
    assert "old" in result
    assert len(fvcol) == 1
    empty_collection(fvcol)

    fvcol.import_bulk(fvdocs)
    assert len(fvcol) == len(fvdocs)
    empty_collection(fvcol)

    fvcol.insert_many(fvdocs)
    assert len(fvcol) == len(fvdocs)

    fvcol.delete_many(fvdocs)
    assert len(fvcol) == 0


def test_vertex_management_via_graph(graph, fvcol):
    # Test insert vertex via graph object
    result = graph.insert_vertex(fvcol.name, {})
    assert result["_key"] in fvcol
    assert len(fvcol) == 1
    vertex_id = result["_id"]

    # Test get vertex via graph object
    assert graph.vertex(vertex_id)["_id"] == vertex_id

    # Test update vertex via graph object
    result = graph.update_vertex({"_id": vertex_id, "foo": 100})
    assert result["_id"] == vertex_id
    assert fvcol[vertex_id]["foo"] == 100

    # Test replace vertex via graph object
    result = graph.replace_vertex({"_id": vertex_id, "bar": 200})
    assert result["_id"] == vertex_id
    assert "foo" not in fvcol[vertex_id]
    assert fvcol[vertex_id]["bar"] == 200

    # Test delete vertex via graph object
    assert graph.delete_vertex(vertex_id) is True
    assert vertex_id not in fvcol
    assert len(fvcol) == 0


def test_edge_management(ecol, bad_ecol, edocs, fvcol, fvdocs, tvcol, tvdocs):
    for vertex in fvdocs:
        fvcol.insert(vertex)
    for vertex in tvdocs:
        tvcol.insert(vertex)

    edge = edocs[0]
    key = edge["_key"]

    # Test insert edge with no key
    no_key_edge = {"_from": edge["_from"], "_to": edge["_to"]}
    result = ecol.insert(no_key_edge)
    assert result["_key"] in ecol
    assert len(ecol) == 1
    empty_collection(ecol)

    # Test insert edge with return_new set to True
    result = ecol.insert(no_key_edge, return_new=True)
    assert "new" in result
    assert result["edge"]["_key"] in ecol
    assert len(ecol) == 1
    empty_collection(ecol)

    # Test insert vertex with ID
    edge_id = ecol.name + "/" + "foo"
    ecol.insert({"_id": edge_id, "_from": edge["_from"], "_to": edge["_to"]})
    assert "foo" in ecol
    assert edge_id in ecol
    assert len(ecol) == 1
    empty_collection(ecol)

    with assert_raises(DocumentParseError) as err:
        ecol.insert(
            {
                "_id": generate_col_name() + "/" + "foo",
                "_from": edge["_from"],
                "_to": edge["_to"],
            }
        )
    assert "bad collection name" in err.value.message

    # Test insert first valid edge
    result = ecol.insert(edge)
    assert result["_key"] == key
    assert "_rev" in result
    assert edge in ecol and key in ecol
    assert len(ecol) == 1
    assert ecol[key]["_from"] == edge["_from"]
    assert ecol[key]["_to"] == edge["_to"]

    # Test insert duplicate edge
    with assert_raises(DocumentInsertError) as err:
        assert ecol.insert(edge)
    assert err.value.error_code in {1202, 1210, 1906}
    assert len(ecol) == 1

    edge = edocs[1]
    key = edge["_key"]

    # Test insert second valid edge with silent set to True
    assert ecol.insert(edge, sync=True, silent=True) is True
    assert edge in ecol and key in ecol
    assert len(ecol) == 2
    assert ecol[key]["_from"] == edge["_from"]
    assert ecol[key]["_to"] == edge["_to"]

    # Test insert third valid edge using link method
    from_vertex = fvcol.get(fvdocs[2])
    to_vertex = tvcol.get(tvdocs[2])
    result = ecol.link(from_vertex, to_vertex, sync=False)
    assert result["_key"] in ecol
    assert len(ecol) == 3

    # Test insert fourth valid edge using link method
    from_vertex = fvcol.get(fvdocs[2])
    to_vertex = tvcol.get(tvdocs[0])
    assert (
        ecol.link(
            from_vertex["_id"],
            to_vertex["_id"],
            {"_id": ecol.name + "/foo"},
            sync=True,
            silent=True,
        )
        is True
    )
    assert "foo" in ecol
    assert len(ecol) == 4

    with assert_raises(DocumentParseError) as err:
        assert ecol.link({}, {})
    assert err.value.message == 'field "_id" required'

    # Test get missing vertex
    bad_document_key = generate_doc_key()
    if ecol.context != "transaction":
        assert ecol.get(bad_document_key) is None

    # Test get existing edge by body with "_key" field
    result = ecol.get({"_key": key})
    assert clean_doc(result) == edge

    # Test get existing edge by body with "_id" field
    result = ecol.get({"_id": ecol.name + "/" + key})
    assert clean_doc(result) == edge

    # Test get existing edge by key
    result = ecol.get(key)
    assert clean_doc(result) == edge

    # Test get existing edge by ID
    result = ecol.get(ecol.name + "/" + key)
    assert clean_doc(result) == edge

    # Test get existing edge with bad revision
    old_rev = result["_rev"]
    with assert_raises(DocumentRevisionError) as err:
        ecol.get(key, rev=old_rev + "1")
    assert err.value.error_code in {1903, 1200}

    # Test get existing edge with bad database
    with assert_raises(DocumentGetError) as err:
        bad_ecol.get(key)
    assert err.value.error_code in {11, 1228}

    # Test update edge with a single field change
    assert "foo" not in ecol.get(key)
    result = ecol.update({"_key": key, "foo": 100})
    assert result["_key"] == key
    assert ecol[key]["foo"] == 100

    # Test update edge with return_old and return_new set to True
    result = ecol.update({"_key": key, "foo": 100}, return_old=True, return_new=True)
    assert "old" in result
    assert "new" in result
    assert "edge" in result
    old_rev = ecol[key]["_rev"]

    # Test update edge with multiple field changes
    result = ecol.update({"_key": key, "foo": 200, "bar": 300})
    assert result["_key"] == key
    assert result["_old_rev"] == old_rev
    assert ecol[key]["foo"] == 200
    assert ecol[key]["bar"] == 300
    old_rev = result["_rev"]

    # Test update edge with correct revision
    result = ecol.update({"_key": key, "_rev": old_rev, "bar": 400})
    assert result["_key"] == key
    assert result["_old_rev"] == old_rev
    assert ecol[key]["foo"] == 200
    assert ecol[key]["bar"] == 400
    old_rev = result["_rev"]

    if ecol.context != "transaction":
        # Test update edge with bad revision
        new_rev = old_rev + "1"
        with assert_raises(DocumentRevisionError, DocumentUpdateError):
            ecol.update({"_key": key, "_rev": new_rev, "bar": 500})
        assert ecol[key]["foo"] == 200
        assert ecol[key]["bar"] == 400

    # Test update edge in missing edge collection
    with assert_raises(DocumentUpdateError) as err:
        bad_ecol.update({"_key": key, "bar": 500})
    assert err.value.error_code in {11, 1228}
    assert ecol[key]["foo"] == 200
    assert ecol[key]["bar"] == 400

    # Test update edge with sync option
    result = ecol.update({"_key": key, "bar": 500}, sync=True)
    assert result["_key"] == key
    assert result["_old_rev"] == old_rev
    assert ecol[key]["foo"] == 200
    assert ecol[key]["bar"] == 500
    old_rev = result["_rev"]

    # Test update edge with silent option
    assert ecol.update({"_key": key, "bar": 600}, silent=True) is True
    assert ecol[key]["foo"] == 200
    assert ecol[key]["bar"] == 600
    assert ecol[key]["_rev"] != old_rev
    old_rev = ecol[key]["_rev"]

    # Test update edge without keep_none option
    result = ecol.update({"_key": key, "bar": None}, keep_none=True)
    assert result["_key"] == key
    assert result["_old_rev"] == old_rev
    assert ecol[key]["foo"] == 200
    assert ecol[key]["bar"] is None
    old_rev = result["_rev"]

    # Test update edge with keep_none option
    result = ecol.update({"_key": key, "foo": None}, keep_none=False)
    assert result["_key"] == key
    assert result["_old_rev"] == old_rev
    assert "foo" not in ecol[key]
    assert ecol[key]["bar"] is None

    # Test replace edge with a single field change
    edge["foo"] = 100
    result = ecol.replace(edge)
    assert result["_key"] == key
    assert ecol[key]["foo"] == 100

    # Test replace edge with return_old and return_new set to True
    result = ecol.replace(edge, return_old=True, return_new=True)
    assert "old" in result
    assert "new" in result
    assert "edge" in result
    old_rev = ecol[key]["_rev"]

    # Test replace edge with silent set to True
    edge["bar"] = 200
    assert ecol.replace(edge, silent=True) is True
    assert ecol[key]["foo"] == 100
    assert ecol[key]["bar"] == 200
    assert ecol[key]["_rev"] != old_rev
    old_rev = ecol[key]["_rev"]

    # Test replace edge with multiple field changes
    edge["foo"] = 200
    edge["bar"] = 300
    result = ecol.replace(edge)
    assert result["_key"] == key
    assert result["_old_rev"] == old_rev
    assert ecol[key]["foo"] == 200
    assert ecol[key]["bar"] == 300
    old_rev = result["_rev"]

    # Test replace edge with correct revision
    edge["foo"] = 300
    edge["bar"] = 400
    edge["_rev"] = old_rev
    result = ecol.replace(edge)
    assert result["_key"] == key
    assert result["_old_rev"] == old_rev
    assert ecol[key]["foo"] == 300
    assert ecol[key]["bar"] == 400
    old_rev = result["_rev"]

    edge["bar"] = 500
    if ecol.context != "transaction":
        # Test replace edge with bad revision
        edge["_rev"] = old_rev + key
        with assert_raises(DocumentRevisionError, DocumentReplaceError) as err:
            ecol.replace(edge)
        assert err.value.error_code in {1200, 1903}
        assert ecol[key]["foo"] == 300
        assert ecol[key]["bar"] == 400

    # Test replace edge with bad database
    with assert_raises(DocumentReplaceError) as err:
        bad_ecol.replace(edge)
    assert err.value.error_code in {11, 1228}
    assert ecol[key]["foo"] == 300
    assert ecol[key]["bar"] == 400

    # Test replace edge with sync option
    result = ecol.replace(edge, sync=True, check_rev=False)
    assert result["_key"] == key
    assert result["_old_rev"] == old_rev
    assert ecol[key]["foo"] == 300
    assert ecol[key]["bar"] == 500

    # Test delete edge with bad revision
    if ecol.context != "transaction":
        old_rev = ecol[key]["_rev"]
        edge["_rev"] = old_rev + "1"
        with assert_raises(DocumentRevisionError, DocumentDeleteError) as err:
            ecol.delete(edge, check_rev=True)
        assert err.value.error_code in {1200, 1903}
        edge["_rev"] = old_rev
        assert edge in ecol

    # Test delete missing edge
    with assert_raises(DocumentDeleteError) as err:
        ecol.delete(bad_document_key, ignore_missing=False)
    assert err.value.error_code == 1202
    if ecol.context != "transaction":
        assert not ecol.delete(bad_document_key, ignore_missing=True)

    # Test delete existing edge with sync set to True
    assert ecol.delete(edge, sync=True, check_rev=False) is True
    if ecol.context != "transaction":
        assert ecol[edge] is None
    assert edge not in ecol

    # Test delete existing edge with return_old set to True
    ecol.insert(edge)
    result = ecol.delete(edge, return_old=True, check_rev=False)
    assert "old" in result
    assert edge not in ecol
    empty_collection(ecol)

    ecol.import_bulk(edocs)
    assert len(ecol) == len(edocs)
    empty_collection(ecol)

    ecol.insert_many(edocs)
    assert len(ecol) == len(edocs)

    ecol.delete_many(edocs)
    assert len(ecol) == 1


def test_vertex_edges(db, bad_db):
    graph_name = generate_graph_name()
    vcol_name = generate_col_name()
    ecol_name = generate_col_name()

    # Prepare test documents
    anna = {"_id": f"{vcol_name}/anna"}
    dave = {"_id": f"{vcol_name}/dave"}
    josh = {"_id": f"{vcol_name}/josh"}
    mary = {"_id": f"{vcol_name}/mary"}
    tony = {"_id": f"{vcol_name}/tony"}

    # Create test graph, vertex and edge collections
    school = db.create_graph(graph_name)

    vcol = school.create_vertex_collection(vcol_name)
    ecol = school.create_edge_definition(
        edge_collection=ecol_name,
        from_vertex_collections=[vcol_name],
        to_vertex_collections=[vcol_name],
    )
    # Insert test vertices into the graph
    vcol.insert(anna)
    vcol.insert(dave)
    vcol.insert(josh)
    vcol.insert(mary)
    vcol.insert(tony)

    # Insert test edges into the graph
    ecol.link(anna, dave)
    ecol.link(josh, dave)
    ecol.link(mary, dave)
    ecol.link(tony, dave)
    ecol.link(dave, anna)

    # Test edges with default direction (both)
    result = ecol.edges(dave)
    assert "stats" in result
    assert "filtered" in result["stats"]
    assert "scanned_index" in result["stats"]
    assert len(result["edges"]) == 5

    result = ecol.edges(anna)
    assert len(result["edges"]) == 2

    # Test edges with direction set to "in"
    result = ecol.edges(dave, direction="in")
    assert len(result["edges"]) == 4

    result = ecol.edges(anna, direction="in")
    assert len(result["edges"]) == 1

    # Test edges with direction set to "out"
    result = ecol.edges(dave, direction="out")
    assert len(result["edges"]) == 1

    result = ecol.edges(anna, direction="out")
    assert len(result["edges"]) == 1

    bad_graph = bad_db.graph(graph_name)
    with assert_raises(EdgeListError) as err:
        bad_graph.edge_collection(ecol_name).edges(dave)
    assert err.value.error_code in {11, 1228}


def test_edge_management_via_graph(graph, ecol, fvcol, fvdocs, tvcol, tvdocs):
    for vertex in fvdocs:
        fvcol.insert(vertex)
    for vertex in tvdocs:
        tvcol.insert(vertex)
    empty_collection(ecol)

    # Get a random "from" vertex
    from_vertex = fvcol.random()
    assert graph.has_vertex(from_vertex)

    # Get a random "to" vertex
    to_vertex = tvcol.random()
    assert graph.has_vertex(to_vertex)

    # Test insert edge via graph object
    result = graph.insert_edge(
        ecol.name, {"_from": from_vertex["_id"], "_to": to_vertex["_id"]}
    )
    assert result["_key"] in ecol
    assert graph.has_edge(result["_id"])
    assert len(ecol) == 1

    # Test link vertices via graph object
    result = graph.link(ecol.name, from_vertex, to_vertex)
    assert result["_key"] in ecol
    assert len(ecol) == 2
    edge_id = result["_id"]

    # Test get edge via graph object
    assert graph.edge(edge_id)["_id"] == edge_id

    # Test list edges via graph object
    result = graph.edges(ecol.name, from_vertex, direction="out")
    assert "stats" in result
    assert len(result["edges"]) == 2

    result = graph.edges(ecol.name, from_vertex, direction="in")
    assert "stats" in result
    assert len(result["edges"]) == 0

    # Test update edge via graph object
    result = graph.update_edge({"_id": edge_id, "foo": 100})
    assert result["_id"] == edge_id
    assert ecol[edge_id]["foo"] == 100

    # Test replace edge via graph object
    result = graph.replace_edge(
        {
            "_id": edge_id,
            "_from": from_vertex["_id"],
            "_to": to_vertex["_id"],
            "bar": 200,
        }
    )
    assert result["_id"] == edge_id
    assert "foo" not in ecol[edge_id]
    assert ecol[edge_id]["bar"] == 200

    # Test delete edge via graph object
    assert graph.delete_edge(edge_id) is True
    assert edge_id not in ecol
    assert len(ecol) == 1


def test_traverse(db):
    # Create test graph, vertex and edge collections
    school = db.create_graph(generate_graph_name())
    profs = school.create_vertex_collection(generate_col_name())
    classes = school.create_vertex_collection(generate_col_name())
    teaches = school.create_edge_definition(
        edge_collection=generate_col_name(),
        from_vertex_collections=[profs.name],
        to_vertex_collections=[classes.name],
    )
    # Insert test vertices into the graph
    profs.insert({"_key": "anna", "name": "Professor Anna"})
    profs.insert({"_key": "andy", "name": "Professor Andy"})
    classes.insert({"_key": "CSC101", "name": "Introduction to CS"})
    classes.insert({"_key": "MAT223", "name": "Linear Algebra"})
    classes.insert({"_key": "STA201", "name": "Statistics"})
    classes.insert({"_key": "MAT101", "name": "Calculus I"})
    classes.insert({"_key": "MAT102", "name": "Calculus II"})

    # Insert test edges into the graph
    teaches.insert({"_from": f"{profs.name}/anna", "_to": f"{classes.name}/CSC101"})
    teaches.insert({"_from": f"{profs.name}/anna", "_to": f"{classes.name}/STA201"})
    teaches.insert({"_from": f"{profs.name}/anna", "_to": f"{classes.name}/MAT223"})
    teaches.insert({"_from": f"{profs.name}/andy", "_to": f"{classes.name}/MAT101"})
    teaches.insert({"_from": f"{profs.name}/andy", "_to": f"{classes.name}/MAT102"})
    teaches.insert({"_from": f"{profs.name}/andy", "_to": f"{classes.name}/MAT223"})

    # Traverse the graph with default settings
    result = school.traverse(f"{profs.name}/anna")
    visited = extract("_key", result["vertices"])
    assert visited == ["CSC101", "MAT223", "STA201", "anna"]

    for path in result["paths"]:
        for vertex in path["vertices"]:
            assert set(vertex) == {"_id", "_key", "_rev", "name"}
        for edge in path["edges"]:
            assert set(edge) == {"_id", "_key", "_rev", "_to", "_from"}

    result = school.traverse(f"{profs.name}/andy")
    visited = extract("_key", result["vertices"])
    assert visited == ["MAT101", "MAT102", "MAT223", "andy"]

    # Traverse the graph with an invalid start vertex
    with assert_raises(GraphTraverseError):
        school.traverse("invalid")

    with assert_raises(GraphTraverseError):
        bad_col_name = generate_col_name()
        school.traverse(f"{bad_col_name}/hanna")

    with assert_raises(GraphTraverseError):
        school.traverse(f"{profs.name}/anderson")

    # Travers the graph with max iteration of 0
    with assert_raises(GraphTraverseError):
        school.traverse(f"{profs.name}/andy", max_iter=0)

    # Traverse the graph with max depth of 0
    result = school.traverse(f"{profs.name}/andy", max_depth=0)
    assert extract("_key", result["vertices"]) == ["andy"]

    result = school.traverse(f"{profs.name}/anna", max_depth=0)
    assert extract("_key", result["vertices"]) == ["anna"]

    # Traverse the graph with min depth of 2
    result = school.traverse(f"{profs.name}/andy", min_depth=2)
    assert extract("_key", result["vertices"]) == []

    result = school.traverse(f"{profs.name}/anna", min_depth=2)
    assert extract("_key", result["vertices"]) == []

    # Traverse the graph with DFS and BFS
    result = school.traverse(
        {"_id": f"{profs.name}/anna"},
        strategy="dfs",
        direction="any",
    )
    dfs_vertices = extract("_key", result["vertices"])

    result = school.traverse(
        {"_id": f"{profs.name}/anna"}, strategy="bfs", direction="any"
    )
    bfs_vertices = extract("_key", result["vertices"])

    assert sorted(dfs_vertices) == sorted(bfs_vertices)

    # Traverse the graph with filter function
    result = school.traverse(
        {"_id": f"{profs.name}/andy"},
        filter_func='if (vertex._key == "MAT101") {return "exclude";} return;',
    )
    assert extract("_key", result["vertices"]) == ["MAT102", "MAT223", "andy"]

    # Traverse the graph with global uniqueness (should be same as before)
    result = school.traverse(
        {"_id": f"{profs.name}/andy"},
        vertex_uniqueness="global",
        edge_uniqueness="global",
        filter_func='if (vertex._key == "MAT101") {return "exclude";} return;',
    )
    assert extract("_key", result["vertices"]) == ["MAT102", "MAT223", "andy"]

    with assert_raises(DocumentParseError) as err:
        school.traverse({})
    assert err.value.message == 'field "_id" required'
