__all__ = ["Graph"]

from typing import List, Optional, Sequence, Union
from warnings import warn

from arango.api import ApiGroup
from arango.collection import EdgeCollection, VertexCollection
from arango.connection import Connection
from arango.exceptions import (
    EdgeDefinitionCreateError,
    EdgeDefinitionDeleteError,
    EdgeDefinitionListError,
    EdgeDefinitionReplaceError,
    GraphPropertiesError,
    GraphTraverseError,
    VertexCollectionCreateError,
    VertexCollectionDeleteError,
    VertexCollectionListError,
)
from arango.executor import ApiExecutor
from arango.formatter import format_graph_properties
from arango.request import Request
from arango.response import Response
from arango.result import Result
from arango.typings import Json, Jsons
from arango.utils import get_col_name, get_doc_id


class Graph(ApiGroup):
    """Graph API wrapper."""

    def __init__(
        self, connection: Connection, executor: ApiExecutor, name: str
    ) -> None:
        super().__init__(connection, executor)
        self._name = name

    def __repr__(self) -> str:
        return f"<Graph {self._name}>"

    def _get_col_by_vertex(self, vertex: Union[str, Json]) -> VertexCollection:
        """Return the vertex collection for the given vertex document.

        :param vertex: Vertex document ID or body with "_id" field.
        :type vertex: str | dict
        :return: Vertex collection API wrapper.
        :rtype: arango.collection.VertexCollection
        """
        return self.vertex_collection(get_col_name(vertex))

    def _get_col_by_edge(self, edge: Union[str, Json]) -> EdgeCollection:
        """Return the edge collection for the given edge document.

        :param edge: Edge document ID or body with "_id" field.
        :type edge: str | dict
        :return: Edge collection API wrapper.
        :rtype: arango.collection.EdgeCollection
        """
        return self.edge_collection(get_col_name(edge))

    @property
    def name(self) -> str:
        """Return the graph name.

        :return: Graph name.
        :rtype: str
        """
        return self._name

    def properties(self) -> Result[Json]:
        """Return graph properties.

        :return: Graph properties.
        :rtype: dict
        :raise arango.exceptions.GraphPropertiesError: If retrieval fails.
        """
        request = Request(method="get", endpoint=f"/_api/gharial/{self._name}")

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_graph_properties(resp.body["graph"])
            raise GraphPropertiesError(resp, request)

        return self._execute(request, response_handler)

    ################################
    # Vertex Collection Management #
    ################################

    def has_vertex_collection(self, name: str) -> Result[bool]:
        """Check if the graph has the given vertex collection.

        :param name: Vertex collection name.
        :type name: str
        :return: True if vertex collection exists, False otherwise.
        :rtype: bool
        """
        request = Request(
            method="get",
            endpoint=f"/_api/gharial/{self._name}/vertex",
        )

        def response_handler(resp: Response) -> bool:
            if resp.is_success:
                return name in resp.body["collections"]
            raise VertexCollectionListError(resp, request)

        return self._execute(request, response_handler)

    def vertex_collections(self) -> Result[List[str]]:
        """Return vertex collections in the graph.

        :return: Names of vertex collections in Edge Definitions and Orphan Collections.
        :rtype: [str]
        :raise arango.exceptions.VertexCollectionListError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint=f"/_api/gharial/{self._name}/vertex",
        )

        def response_handler(resp: Response) -> List[str]:
            if not resp.is_success:
                raise VertexCollectionListError(resp, request)
            return sorted(set(resp.body["collections"]))

        return self._execute(request, response_handler)

    def vertex_collection(self, name: str) -> VertexCollection:
        """Return the vertex collection API wrapper.

        :param name: Vertex collection name.
        :type name: str
        :return: Vertex collection API wrapper.
        :rtype: arango.collection.VertexCollection
        """
        return VertexCollection(self._conn, self._executor, self._name, name)

    def create_vertex_collection(self, name: str) -> Result[VertexCollection]:
        """Create a vertex collection in the graph.

        :param name: Vertex collection name.
        :type name: str
        :return: Vertex collection API wrapper.
        :rtype: arango.collection.VertexCollection
        :raise arango.exceptions.VertexCollectionCreateError: If create fails.
        """
        request = Request(
            method="post",
            endpoint=f"/_api/gharial/{self._name}/vertex",
            data={"collection": name},
        )

        def response_handler(resp: Response) -> VertexCollection:
            if resp.is_success:
                return self.vertex_collection(name)
            raise VertexCollectionCreateError(resp, request)

        return self._execute(request, response_handler)

    def delete_vertex_collection(self, name: str, purge: bool = False) -> Result[bool]:
        """Remove a vertex collection from the graph.

        :param name: Vertex collection name.
        :type name: str
        :param purge: If set to True, the vertex collection is not just deleted
            from the graph but also from the database completely.
        :type purge: bool
        :return: True if vertex collection was deleted successfully.
        :rtype: bool
        :raise arango.exceptions.VertexCollectionDeleteError: If delete fails.
        """
        request = Request(
            method="delete",
            endpoint=f"/_api/gharial/{self._name}/vertex/{name}",
            params={"dropCollection": purge},
        )

        def response_handler(resp: Response) -> bool:
            if resp.is_success:
                return True
            raise VertexCollectionDeleteError(resp, request)

        return self._execute(request, response_handler)

    ##############################
    # Edge Collection Management #
    ##############################

    def has_edge_definition(self, name: str) -> Result[bool]:
        """Check if the graph has the given edge definition.

        :param name: Edge collection name.
        :type name: str
        :return: True if edge definition exists, False otherwise.
        :rtype: bool
        """
        request = Request(method="get", endpoint=f"/_api/gharial/{self._name}")

        def response_handler(resp: Response) -> bool:
            if not resp.is_success:
                raise EdgeDefinitionListError(resp, request)

            body = resp.body["graph"]
            return any(
                edge_definition["collection"] == name
                for edge_definition in body["edgeDefinitions"]
            )

        return self._execute(request, response_handler)

    def has_edge_collection(self, name: str) -> Result[bool]:
        """Check if the graph has the given edge collection.

        :param name: Edge collection name.
        :type name: str
        :return: True if edge collection exists, False otherwise.
        :rtype: bool
        """
        return self.has_edge_definition(name)

    def edge_collection(self, name: str) -> EdgeCollection:
        """Return the edge collection API wrapper.

        :param name: Edge collection name.
        :type name: str
        :return: Edge collection API wrapper.
        :rtype: arango.collection.EdgeCollection
        """
        return EdgeCollection(self._conn, self._executor, self._name, name)

    def edge_definitions(self) -> Result[Jsons]:
        """Return the edge definitions of the graph.

        :return: Edge definitions of the graph.
        :rtype: [dict]
        :raise arango.exceptions.EdgeDefinitionListError: If retrieval fails.
        """
        request = Request(method="get", endpoint=f"/_api/gharial/{self._name}")

        def response_handler(resp: Response) -> Jsons:
            if not resp.is_success:
                raise EdgeDefinitionListError(resp, request)

            body = resp.body["graph"]
            return [
                {
                    "edge_collection": edge_definition["collection"],
                    "from_vertex_collections": edge_definition["from"],
                    "to_vertex_collections": edge_definition["to"],
                }
                for edge_definition in body["edgeDefinitions"]
            ]

        return self._execute(request, response_handler)

    def create_edge_definition(
        self,
        edge_collection: str,
        from_vertex_collections: Sequence[str],
        to_vertex_collections: Sequence[str],
    ) -> Result[EdgeCollection]:
        """Create a new edge definition.

        An edge definition consists of an edge collection, "from" vertex
        collection(s) and "to" vertex collection(s). Here is an example entry:

        .. code-block:: python

            {
                'edge_collection': 'edge_collection_name',
                'from_vertex_collections': ['from_vertex_collection_name'],
                'to_vertex_collections': ['to_vertex_collection_name']
            }

        :param edge_collection: Edge collection name.
        :type edge_collection: str
        :param from_vertex_collections: Names of "from" vertex collections.
        :type from_vertex_collections: [str]
        :param to_vertex_collections: Names of "to" vertex collections.
        :type to_vertex_collections: [str]
        :return: Edge collection API wrapper.
        :rtype: arango.collection.EdgeCollection
        :raise arango.exceptions.EdgeDefinitionCreateError: If create fails.
        """
        request = Request(
            method="post",
            endpoint=f"/_api/gharial/{self._name}/edge",
            data={
                "collection": edge_collection,
                "from": from_vertex_collections,
                "to": to_vertex_collections,
            },
        )

        def response_handler(resp: Response) -> EdgeCollection:
            if resp.is_success:
                return self.edge_collection(edge_collection)
            raise EdgeDefinitionCreateError(resp, request)

        return self._execute(request, response_handler)

    def replace_edge_definition(
        self,
        edge_collection: str,
        from_vertex_collections: Sequence[str],
        to_vertex_collections: Sequence[str],
    ) -> Result[EdgeCollection]:
        """Replace an edge definition.

        :param edge_collection: Edge collection name.
        :type edge_collection: str
        :param from_vertex_collections: Names of "from" vertex collections.
        :type from_vertex_collections: [str]
        :param to_vertex_collections: Names of "to" vertex collections.
        :type to_vertex_collections: [str]
        :return: Edge collection API wrapper.
        :rtype: arango.collection.EdgeCollection
        :raise arango.exceptions.EdgeDefinitionReplaceError: If replace fails.
        """
        request = Request(
            method="put",
            endpoint=f"/_api/gharial/{self._name}/edge/{edge_collection}",
            data={
                "collection": edge_collection,
                "from": from_vertex_collections,
                "to": to_vertex_collections,
            },
        )

        def response_handler(resp: Response) -> EdgeCollection:
            if resp.is_success:
                return self.edge_collection(edge_collection)
            raise EdgeDefinitionReplaceError(resp, request)

        return self._execute(request, response_handler)

    def delete_edge_definition(self, name: str, purge: bool = False) -> Result[bool]:
        """Delete an edge definition from the graph.

        :param name: Edge collection name.
        :type name: str
        :param purge: If set to True, the edge definition is not just removed
            from the graph but the edge collection is also deleted completely
            from the database.
        :type purge: bool
        :return: True if edge definition was deleted successfully.
        :rtype: bool
        :raise arango.exceptions.EdgeDefinitionDeleteError: If delete fails.
        """
        request = Request(
            method="delete",
            endpoint=f"/_api/gharial/{self._name}/edge/{name}",
            params={"dropCollections": purge},
        )

        def response_handler(resp: Response) -> bool:
            if resp.is_success:
                return True
            raise EdgeDefinitionDeleteError(resp, request)

        return self._execute(request, response_handler)

    ###################
    # Graph Functions #
    ###################

    def traverse(
        self,
        start_vertex: Union[str, Json],
        direction: str = "outbound",
        item_order: str = "forward",
        strategy: Optional[str] = None,
        order: Optional[str] = None,
        edge_uniqueness: Optional[str] = None,
        vertex_uniqueness: Optional[str] = None,
        max_iter: Optional[int] = None,
        min_depth: Optional[int] = None,
        max_depth: Optional[int] = None,
        init_func: Optional[str] = None,
        sort_func: Optional[str] = None,
        filter_func: Optional[str] = None,
        visitor_func: Optional[str] = None,
        expander_func: Optional[str] = None,
    ) -> Result[Json]:
        """Traverse the graph and return the visited vertices and edges.

        .. warning::

            This method is deprecated and no longer works since ArangoDB 3.12.
            The preferred way to traverse graphs is via AQL.

        :param start_vertex: Start vertex document ID or body with "_id" field.
        :type start_vertex: str | dict
        :param direction: Traversal direction. Allowed values are "outbound"
            (default), "inbound" and "any".
        :type direction: str
        :param item_order: Item iteration order. Allowed values are "forward"
            (default) and "backward".
        :type item_order: str
        :param strategy: Traversal strategy. Allowed values are "depthfirst"
            and "breadthfirst".
        :type strategy: str | None
        :param order: Traversal order. Allowed values are "preorder",
            "postorder", and "preorder-expander".
        :type order: str | None
        :param edge_uniqueness: Uniqueness for visited edges. Allowed values
            are "global", "path" or "none".
        :type edge_uniqueness: str | None
        :param vertex_uniqueness: Uniqueness for visited vertices. Allowed
            values are "global", "path" or "none".
        :type vertex_uniqueness: str | None
        :param max_iter: If set, halt the traversal after the given number of
            iterations. This parameter can be used to prevent endless loops in
            cyclic graphs.
        :type max_iter: int | None
        :param min_depth: Minimum depth of the nodes to visit.
        :type min_depth: int | None
        :param max_depth: Maximum depth of the nodes to visit.
        :type max_depth: int | None
        :param init_func: Initialization function in Javascript with signature
            ``(config, result) -> void``. This function is used to initialize
            values in the result.
        :type init_func: str | None
        :param sort_func: Sorting function in Javascript with signature
            ``(left, right) -> integer``, which returns ``-1`` if ``left <
            right``, ``+1`` if ``left > right`` and ``0`` if ``left == right``.
        :type sort_func: str | None
        :param filter_func: Filter function in Javascript with signature
            ``(config, vertex, path) -> mixed``, where ``mixed`` can have one
            of the following values (or an array with multiple): "exclude" (do
            not visit the vertex), "prune" (do not follow the edges of the
            vertex), or "undefined" (visit the vertex and follow its edges).
        :type filter_func: str | None
        :param visitor_func: Visitor function in Javascript with signature
            ``(config, result, vertex, path, connected) -> void``. The return
            value is ignored, ``result`` is modified by reference, and
            ``connected`` is populated only when parameter **order** is set to
            "preorder-expander".
        :type visitor_func: str | None
        :param expander_func: Expander function in Javascript with signature
            ``(config, vertex, path) -> mixed``. The function must return an
            array of connections for ``vertex``. Each connection is an object
            with attributes "edge" and "vertex".
        :type expander_func: str | None
        :return: Visited edges and vertices.
        :rtype: dict
        :raise arango.exceptions.GraphTraverseError: If traversal fails.
        """
        m = "The HTTP traversal API is deprecated since version 3.4.0. The preferred way to traverse graphs is via AQL."  # noqa: E501
        warn(m, DeprecationWarning, stacklevel=2)

        if strategy is not None:
            if strategy.lower() == "dfs":
                strategy = "depthfirst"
            elif strategy.lower() == "bfs":
                strategy = "breadthfirst"

        uniqueness = {}
        if vertex_uniqueness is not None:
            uniqueness["vertices"] = vertex_uniqueness
        if edge_uniqueness is not None:
            uniqueness["edges"] = edge_uniqueness

        data: Json = {
            "startVertex": get_doc_id(start_vertex),
            "graphName": self._name,
            "direction": direction,
            "strategy": strategy,
            "order": order,
            "itemOrder": item_order,
            "uniqueness": uniqueness or None,
            "maxIterations": max_iter,
            "minDepth": min_depth,
            "maxDepth": max_depth,
            "init": init_func,
            "filter": filter_func,
            "visitor": visitor_func,
            "sort": sort_func,
            "expander": expander_func,
        }
        request = Request(
            method="post",
            endpoint="/_api/traversal",
            data={k: v for k, v in data.items() if v is not None},
        )

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise GraphTraverseError(resp, request)

            result: Json = resp.body["result"]["visited"]
            return result

        return self._execute(request, response_handler)

    #####################
    # Vertex Management #
    #####################

    def has_vertex(
        self,
        vertex: Union[str, Json],
        rev: Optional[str] = None,
        check_rev: bool = True,
    ) -> Result[bool]:
        """Check if the given vertex document exists in the graph.

        :param vertex: Vertex document ID or body with "_id" field.
        :type vertex: str | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **vertex** if present.
        :type rev: str | None
        :param check_rev: If set to True, revision of **vertex** (if given) is
            compared against the revision of target vertex document.
        :type check_rev: bool
        :return: True if vertex document exists, False otherwise.
        :rtype: bool
        :raise arango.exceptions.DocumentGetError: If check fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_vertex(vertex).has(vertex, rev, check_rev)

    def vertex(
        self,
        vertex: Union[str, Json],
        rev: Optional[str] = None,
        check_rev: bool = True,
    ) -> Result[Optional[Json]]:
        """Return a vertex document.

        :param vertex: Vertex document ID or body with "_id" field.
        :type vertex: str | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **vertex** if present.
        :type rev: str | None
        :param check_rev: If set to True, revision of **vertex** (if given) is
            compared against the revision of target vertex document.
        :type check_rev: bool
        :return: Vertex document or None if not found.
        :rtype: dict | None
        :raise arango.exceptions.DocumentGetError: If retrieval fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_vertex(vertex).get(vertex, rev, check_rev)

    def insert_vertex(
        self,
        collection: str,
        vertex: Json,
        sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Insert a new vertex document.

        :param collection: Vertex collection name.
        :type collection: str
        :param vertex: New vertex document to insert. If it has "_key" or "_id"
            field, its value is used as key of the new vertex (otherwise it is
            auto-generated). Any "_rev" field is ignored.
        :type vertex: dict
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentInsertError: If insert fails.
        """
        return self.vertex_collection(collection).insert(vertex, sync, silent)

    def update_vertex(
        self,
        vertex: Json,
        check_rev: bool = True,
        keep_none: bool = True,
        sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Update a vertex document.

        :param vertex: Partial or full vertex document with updated values. It
            must contain the "_id" field.
        :type vertex: dict
        :param check_rev: If set to True, revision of **vertex** (if given) is
            compared against the revision of target vertex document.
        :type check_rev: bool
        :param keep_none: If set to True, fields with value None are retained
            in the document. If set to False, they are removed completely.
        :type keep_none: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentUpdateError: If update fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_vertex(vertex).update(
            vertex=vertex,
            check_rev=check_rev,
            keep_none=keep_none,
            sync=sync,
            silent=silent,
        )

    def replace_vertex(
        self,
        vertex: Json,
        check_rev: bool = True,
        sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Replace a vertex document.

        :param vertex: New vertex document to replace the old one with. It must
            contain the "_id" field.
        :type vertex: dict
        :param check_rev: If set to True, revision of **vertex** (if given) is
            compared against the revision of target vertex document.
        :type check_rev: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentReplaceError: If replace fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_vertex(vertex).replace(
            vertex=vertex, check_rev=check_rev, sync=sync, silent=silent
        )

    def delete_vertex(
        self,
        vertex: Json,
        rev: Optional[str] = None,
        check_rev: bool = True,
        ignore_missing: bool = False,
        sync: Optional[bool] = None,
    ) -> Result[Union[bool, Json]]:
        """Delete a vertex document.

        :param vertex: Vertex document ID or body with "_id" field.
        :type vertex: str | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **vertex** if present.
        :type rev: str | None
        :param check_rev: If set to True, revision of **vertex** (if given) is
            compared against the revision of target vertex document.
        :type check_rev: bool
        :param ignore_missing: Do not raise an exception on missing document.
            This parameter has no effect in transactions where an exception is
            always raised on failures.
        :type ignore_missing: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :return: True if vertex was deleted successfully, False if vertex was
            not found and **ignore_missing** was set to True (does not apply in
            transactions).
        :rtype: bool
        :raise arango.exceptions.DocumentDeleteError: If delete fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_vertex(vertex).delete(
            vertex=vertex,
            rev=rev,
            check_rev=check_rev,
            ignore_missing=ignore_missing,
            sync=sync,
        )

    ###################
    # Edge Management #
    ###################

    def has_edge(
        self, edge: Union[str, Json], rev: Optional[str] = None, check_rev: bool = True
    ) -> Result[bool]:
        """Check if the given edge document exists in the graph.

        :param edge: Edge document ID or body with "_id" field.
        :type edge: str | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **edge** if present.
        :type rev: str | None
        :param check_rev: If set to True, revision of **edge** (if given) is
            compared against the revision of target edge document.
        :type check_rev: bool
        :return: True if edge document exists, False otherwise.
        :rtype: bool
        :raise arango.exceptions.DocumentInError: If check fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_edge(edge).has(edge, rev, check_rev)

    def edge(
        self, edge: Union[str, Json], rev: Optional[str] = None, check_rev: bool = True
    ) -> Result[Optional[Json]]:
        """Return an edge document.

        :param edge: Edge document ID or body with "_id" field.
        :type edge: str | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **edge** if present.
        :type rev: str | None
        :param check_rev: If set to True, revision of **edge** (if given) is
            compared against the revision of target edge document.
        :type check_rev: bool
        :return: Edge document or None if not found.
        :rtype: dict | None
        :raise arango.exceptions.DocumentGetError: If retrieval fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_edge(edge).get(edge, rev, check_rev)

    def insert_edge(
        self,
        collection: str,
        edge: Json,
        sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Insert a new edge document.

        :param collection: Edge collection name.
        :type collection: str
        :param edge: New edge document to insert. It must contain "_from" and
            "_to" fields. If it has "_key" or "_id" field, its value is used
            as key of the new edge document (otherwise it is auto-generated).
            Any "_rev" field is ignored.
        :type edge: dict
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentInsertError: If insert fails.
        """
        return self.edge_collection(collection).insert(edge, sync, silent)

    def update_edge(
        self,
        edge: Json,
        check_rev: bool = True,
        keep_none: bool = True,
        sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Update an edge document.

        :param edge: Partial or full edge document with updated values. It must
            contain the "_id" field.
        :type edge: dict
        :param check_rev: If set to True, revision of **edge** (if given) is
            compared against the revision of target edge document.
        :type check_rev: bool
        :param keep_none: If set to True, fields with value None are retained
            in the document. If set to False, they are removed completely.
        :type keep_none: bool | None
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentUpdateError: If update fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_edge(edge).update(
            edge=edge,
            check_rev=check_rev,
            keep_none=keep_none,
            sync=sync,
            silent=silent,
        )

    def replace_edge(
        self,
        edge: Json,
        check_rev: bool = True,
        sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Replace an edge document.

        :param edge: New edge document to replace the old one with. It must
            contain the "_id" field. It must also contain the "_from" and "_to"
            fields.
        :type edge: dict
        :param check_rev: If set to True, revision of **edge** (if given) is
            compared against the revision of target edge document.
        :type check_rev: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentReplaceError: If replace fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_edge(edge).replace(
            edge=edge, check_rev=check_rev, sync=sync, silent=silent
        )

    def delete_edge(
        self,
        edge: Union[str, Json],
        rev: Optional[str] = None,
        check_rev: bool = True,
        ignore_missing: bool = False,
        sync: Optional[bool] = None,
    ) -> Result[Union[bool, Json]]:
        """Delete an edge document.

        :param edge: Edge document ID or body with "_id" field.
        :type edge: str | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **edge** if present.
        :type rev: str | None
        :param check_rev: If set to True, revision of **edge** (if given) is
            compared against the revision of target edge document.
        :type check_rev: bool
        :param ignore_missing: Do not raise an exception on missing document.
            This parameter has no effect in transactions where an exception is
            always raised on failures.
        :type ignore_missing: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :return: True if edge was deleted successfully, False if edge was not
            found and **ignore_missing** was set to True (does not  apply in
            transactions).
        :rtype: bool
        :raise arango.exceptions.DocumentDeleteError: If delete fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_edge(edge).delete(
            edge=edge,
            rev=rev,
            check_rev=check_rev,
            ignore_missing=ignore_missing,
            sync=sync,
        )

    def link(
        self,
        collection: str,
        from_vertex: Union[str, Json],
        to_vertex: Union[str, Json],
        data: Optional[Json] = None,
        sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Insert a new edge document linking the given vertices.

        :param collection: Edge collection name.
        :type collection: str
        :param from_vertex: "From" vertex document ID or body with "_id" field.
        :type from_vertex: str | dict
        :param to_vertex: "To" vertex document ID or body with "_id" field.
        :type to_vertex: str | dict
        :param data: Any extra data for the new edge document. If it has "_key"
            or "_id" field, its value is used as key of the new edge document
            (otherwise it is auto-generated).
        :type data: dict
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentInsertError: If insert fails.
        """
        return self.edge_collection(collection).link(
            from_vertex=from_vertex,
            to_vertex=to_vertex,
            data=data,
            sync=sync,
            silent=silent,
        )

    def edges(
        self, collection: str, vertex: Union[str, Json], direction: Optional[str] = None
    ) -> Result[Json]:
        """Return the edge documents coming in and/or out of given vertex.

        :param collection: Edge collection name.
        :type collection: str
        :param vertex: Vertex document ID or body with "_id" field.
        :type vertex: str | dict
        :param direction: The direction of the edges. Allowed values are "in"
            and "out". If not set, edges in both directions are returned.
        :type direction: str
        :return: List of edges and statistics.
        :rtype: dict
        :raise arango.exceptions.EdgeListError: If retrieval fails.
        """
        return self.edge_collection(collection).edges(vertex, direction)
