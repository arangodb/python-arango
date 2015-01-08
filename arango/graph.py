"""ArangoDB Graph."""

from arango.utils import uncamelify
from arango.exceptions import *


class Graph(object):
    """A wrapper for ArangoDB graph specific API.

    :param name: the name of the graph
    :type name: str
    :param api: ArangoDB API object
    :type api: arango.api.ArangoAPI
    """

    def __init__(self, name, api):
        self.name = name
        self._api = api

    @property
    def properties(self):
        """Return the properties of this graph.

        :returns: the properties of this graph
        :rtype: dict
        :raises: GraphPropertiesError
        """
        res = self._api.get(
            "/_api/gharial/{}".format(self.name)
        )
        if res.status_code != 200:
            raise GraphPropertiesError(res)
        return uncamelify(res.obj["graph"])

    @property
    def id(self):
        """Return the ID of this graph.

        :returns: the ID of this graph
        :rtype: str
        :raises: GraphPropertiesError
        """
        return self.properties["_id"]

    @property
    def revision(self):
        """Return the revision of this graph.

        :returns: the revision of this graph
        :rtype: str
        :raises: GraphPropertiesError
        """
        return self.properties["_rev"]

    ###############################
    # Handling Vertex Collections #
    ###############################

    @property
    def orphan_collections(self):
        """Return the orphan collections of this graph.

        :returns: the string names of the orphan collections
        :rtype: list
        :raises: GraphPropertiesError
        """
        return self.properties["orphan_collections"]

    @property
    def vertex_collections(self):
        """Return the vertex collections of this graph.

        :returns: the string names of the vertex collections
        :rtype: list
        :raises: VertexCollectionListError
        """
        res = self._api.get(
            "/_api/gharial/{}/vertex".format(self.name)
        )
        if res.status_code != 200:
            raise VertexCollectionListError(res)
        return res.obj["collections"]

    def add_vertex_collection(self, collection):
        """Add a vertex collection to this graph.

        :param collection: the name of the vertex collection to add
        :type collection: str
        :returns: the updated list of the vertex collection names
        :rtype: list
        :raises: VertexCollectionAddError
        """
        res = self._api.post(
            "/_api/gharial/{}/vertex".format(self.name),
            data={"collection": collection}
        )
        if res.status_code != 201:
            raise VertexCollectionAddError(res)
        return self.vertex_collections

    def remove_vertex_collection(self, collection,
                                 drop_collection=False):
        """Remove a vertex collection from this graph.

        :param collection: the name of the vertex collection to remove
        :type collection: str
        :param drop_collection: whether or not to drop the collection also
        :type drop_collection: bool
        :returns: the updated list of the vertex collection names
        :rtype: list
        :raises: VertexCollectionRemoveError
        """
        res = self._api.delete(
            "/_api/gharial/{}/vertex/{}".format(self.name, collection),
            params={"dropCollection": drop_collection}
        )
        if res.status_code != 200:
            raise VertexCollectionRemoveError(res)
        return self.vertex_collections

    #############################
    # Handling Edge Definitions #
    #############################

    @property
    def edge_definitions(self):
        """Return the edge definitions of this graph.

        :returns: the edge definitions of this graph
        :rtype: list
        :raises: GraphPropertiesError
        """
        return self.properties["edge_definitions"]

    def add_edge_definition(self, edge_collection,
                            from_vertex_collections,
                            to_vertex_collections):
        """Add a edge definition to this graph.

        :param edge_collection: the name of the edge collection
        :type edge_collection: str
        :param from_vertex_collections: names of ``from`` vertex collections
        :type from_vertex_collections: list
        :param to_vertex_collections: the names of ``to`` vertex collections
        :type to_vertex_collections: list
        :returns: the updated list of edge definitions
        :rtype: list
        :raises: EdgeDefinitionAddError
        """
        res = self._api.post(
            "/_api/gharial/{}/edge".format(self.name),
            data={
                "collection": edge_collection,
                "from": from_vertex_collections,
                "to": to_vertex_collections
            }
        )
        if res.status_code != 201:
            raise EdgeDefinitionAddError(res)
        return res.obj["graph"]["edgeDefinitions"]

    def replace_edge_definition(self, edge_collection,
                                from_vertex_collections,
                                to_vertex_collections):
        """Replace an edge definition in this graph.

        :param edge_collection: the name of the edge collection
        :type edge_collection: str
        :param from_vertex_collections: names of ``from`` vertex collections
        :type from_vertex_collections: list
        :param to_vertex_collections: the names of ``to`` vertex collections
        :type to_vertex_collections: list
        :returns: the updated list of edge definitions
        :rtype: list
        :raises: EdgeDefinitionReplaceError
        """
        res = self._api.put(
            "/_api/gharial/{}/edge/{}".format(
                self.name, edge_collection
            ),
            data={
                "collection": edge_collection,
                "from": from_vertex_collections,
                "to": to_vertex_collections
            }
        )
        if res.status_code != 200:
            raise EdgeDefinitionReplaceError(res)
        return res.obj["graph"]["edgeDefinitions"]

    def remove_edge_definition(self, collection,
                               drop_collection=False):
        """Remove the specified edge definition from this graph.

        :param collection: the name of the edge collection to remove
        :type collection: str
        :param drop_collection: whether or not to drop the collection also
        :type drop_collection: bool
        :returns: the updated list of edge definitions
        :rtype: list
        :raises: EdgeDefinitionRemoveError
        """
        res = self._api.delete(
            "/_api/gharial/{}/edge/{}".format(self.name, collection),
            params={"dropCollection": drop_collection}
        )
        if res.status_code != 200:
            raise EdgeDefinitionRemoveError(res)
        return res.obj["graph"]["edgeDefinitions"]

    #####################
    # Handling Vertices #
    #####################

    def get_vertex(self, vertex_id, rev=None):
        """Return the vertex of the specified ID in this graph.

        If the vertex revision ``rev`` is specified, it must match against
        the revision of the retrieved vertex.

        :param vertex_id: the ID of the vertex to retrieve
        :type vertex_id: str
        :param rev: the vertex revision must match this value
        :type rev: str or None
        :returns: the requested vertex or None if not found
        :rtype: dict or None
        :raises: RevisionMismatchError, VertexGetError
        """
        res = self._api.get(
            "/_api/gharial/{}/vertex/{}".format(self.name, vertex_id),
            params={"rev": rev} if rev is not None else {}
        )
        if res.status_code == 412:
            raise RevisionMismatchError(res)
        elif res.status_code == 404:
            return None
        elif res.status_code != 200:
            raise VertexGetError(res)
        return res.obj["vertex"]

    def add_vertex(self, collection, data, wait_for_sync=False):
        """Add a vertex to the specified vertex collection if this graph.

        If ``data`` contains the ``_key`` key, its value must be unused
        in the collection.

        :param collection: the name of the vertex collection
        :type collection: str
        :param data: the body of the new vertex
        :type data: dict
        :param wait_for_sync: wait for the add to sync to disk
        :type wait_for_sync: bool
        :return: the id, rev and key of the new vertex
        :rtype: dict
        :raises: VertexAddError
        """
        res = self._api.post(
            "/_api/gharial/{}/vertex/{}".format(
                self.name, collection
            ),
            params={"waitForSync": wait_for_sync},
            data=data
        )
        if res.status_code not in {201, 202}:
            raise VertexAddError(res)
        return res.obj["vertex"]

    def update_vertex(self, vertex_id, data, rev=None, keep_none=True,
                      wait_for_sync=False):
        """Update a vertex of the specified ID in this graph.

        If ``keep_none`` is set to True, then attributes with values None
        are retained. Otherwise, they are removed from the vertex.

        If ``data`` contains the ``_key`` key, it is ignored.

        If the ``_rev`` key is in ``data``, the revision of the target
        vertex must match against its value. Otherwise a RevisionMismatch
        error is thrown. If ``rev`` is also provided, its value is preferred.

        :param vertex_id: the ID of the vertex to be updated
        :type vertex_id: str
        :param data: the body to update the vertex with
        :type data: dict
        :param rev: the vertex revision must match this value
        :type rev: str or None
        :param keep_none: whether or not to keep the keys with value None
        :type keep_none: bool
        :param wait_for_sync: wait for the update to sync to disk
        :type wait_for_sync: bool
        :return: the id, rev and key of the updated vertex
        :rtype: dict
        :raises: RevisionMismatchError, VertexUpdateError
        """
        params = {
            "waitForSync": wait_for_sync,
            "keepNull": keep_none
        }
        if rev is not None:
            params["rev"] = rev
        elif "_rev" in data:
            params["rev"] = data["_rev"]
        res = self._api.patch(
            "/_api/gharial/{}/vertex/{}".format(self.name, vertex_id),
            params=params,
            data=data
        )
        if res.status_code == 412:
            raise RevisionMismatchError(res)
        elif res.status_code not in {200, 202}:
            raise VertexUpdateError(res)
        return res.obj["vertex"]

    def replace_vertex(self, vertex_id, data, rev=None, wait_for_sync=False):
        """Replace a vertex of the specified ID in this graph.

        If ``data`` contains the ``_key`` key, it is ignored.

        If the ``_rev`` key is in ``data``, the revision of the target
        vertex must match against its value. Otherwise a RevisionMismatch
        error is thrown. If ``rev`` is also provided, its value is preferred.

        :param vertex_id: the ID of the vertex to be replaced
        :type vertex_id: str
        :param data: the body to replace the vertex with
        :type data: dict
        :param rev: the vertex revision must match this value
        :type rev: str or None
        :param wait_for_sync: wait for replace to sync to disk
        :type wait_for_sync: bool
        :return: the id, rev and key of the replaced vertex
        :rtype: dict
        :raises: RevisionMismatchError, VertexReplaceError
        """
        params = {"waitForSync": wait_for_sync}
        if rev is not None:
            params["rev"] = rev
        if "_rev" in data:
            params["rev"] = data["_rev"]
        res = self._api.put(
            "/_api/gharial/{}/vertex/{}".format(self.name, vertex_id),
            params=params,
            data=data
        )
        if res.status_code == 412:
            raise RevisionMismatchError(res)
        elif res.status_code not in {200, 202}:
            raise VertexReplaceError(res)
        return res.obj["vertex"]

    def remove_vertex(self, vertex_id, rev=None, wait_for_sync=False):
        """Remove the vertex of the specified ID from this graph.

        :param vertex_id: the ID of the vertex to be removed
        :type vertex_id: str
        :param rev: the vertex revision must match this value
        :type rev: str or None
        :raises: RevisionMismatchError, VertexRemoveError
        """
        params={"waitForSync": wait_for_sync}
        if rev is not None:
            params["rev"] = rev
        res = self._api.delete(
            "/_api/gharial/{}/vertex/{}".format(self.name, vertex_id),
            params=params
        )
        if res.status_code == 412:
            raise RevisionMismatchError(res)
        if res.status_code not in {200, 202}:
            raise VertexRemoveError(res)

    ##################
    # Handling Edges #
    ##################

    def get_edge(self, edge_id, rev=None):
        """Return the edge of the specified ID in this graph.

        If the edge revision ``rev`` is specified, it must match against
        the revision of the retrieved edge.

        :param edge_id: the ID of the edge to retrieve
        :type edge_id: str
        :param rev: the edge revision must match this value
        :type rev: str or None
        :returns: the requested edge or None if not found
        :rtype: dict or None
        :raises: RevisionMismatchError, EdgeGetError
        """
        res = self._api.get(
            "/_api/gharial/{}/edge/{}".format(self.name, edge_id),
            params={} if rev is None else {"rev": rev}
        )
        if res.status_code == 412:
            raise RevisionMismatchError(res)
        elif res.status_code == 404:
            return None
        elif res.status_code != 200:
            raise EdgeGetError(res)
        return res.obj["edge"]

    def add_edge(self, collection, data, wait_for_sync=False):
        """Add an edge to the specified edge collection of this graph.

        The ``data`` must contain ``_from`` and ``_to`` keys with valid
        vertex IDs as their values. If ``data`` contains the ``_key`` key,
        its value must be unused in the collection.

        :param collection: the name of the edge collection
        :type collection: str
        :param data: the body of the new edge
        :type data: dict
        :param wait_for_sync: wait for the add to sync to disk
        :type wait_for_sync: bool
        :return: the id, rev and key of the new edge
        :rtype: dict
        :raises: DocumentInvalidError, EdgeAddError
        """
        if "_to" not in data:
            raise DocumentInvalidError(
                "the new edge data is missing the '_to' key")
        if "_from" not in data:
            raise DocumentInvalidError(
                "the new edge data is missing the '_from' key")
        res = self._api.post(
            "/_api/gharial/{}/edge/{}".format(
                self.name, collection
            ),
            params={"waitForSync": wait_for_sync},
            data=data
        )
        if res.status_code not in {201, 202}:
            raise EdgeAddError(res)
        return res.obj["edge"]

    def update_edge(self, edge_id, data, rev=None, keep_none=True,
                    wait_for_sync=False):
        """Update the edge of the specified ID in this graph.

        If ``keep_none`` is set to True, then attributes with values None
        are retained. Otherwise, they are removed from the edge.

        If ``data`` contains the ``_key`` key, it is ignored.

        If the ``_rev`` key is in ``data``, the revision of the target
        edge must match against its value. Otherwise a RevisionMismatch
        error is thrown. If ``rev`` is also provided, its value is preferred.

        The ``_from`` and ``_to`` attributes are immutable, and they are
        ignored if present in ``data``

        :param edge_id: the ID of the edge to be removed
        :type edge_id: str
        :param data: the body to update the edge with
        :type data: dict
        :param rev: the edge revision must match this value
        :type rev: str or None
        :param keep_none: whether or not to keep the keys with value None
        :type keep_none: bool
        :param wait_for_sync: wait for the update to sync to disk
        :type wait_for_sync: bool
        :return: the id, rev and key of the updated edge
        :rtype: dict
        :raises: RevisionMismatchError, EdgeUpdateError
        """
        params = {
            "waitForSync": wait_for_sync,
            "keepNull": keep_none
        }
        if rev is not None:
            params["rev"] = rev
        elif "_rev" in data:
            params["rev"] = data["_rev"]
        res = self._api.patch(
            "/_api/gharial/{}/edge/{}".format(self.name, edge_id),
            params=params,
            data=data
        )
        if res.status_code == 412:
            raise RevisionMismatchError(res)
        elif res.status_code not in {200, 202}:
            raise EdgeUpdateError(res)
        return res.obj["edge"]

    def replace_edge(self, edge_id, data, rev=None, wait_for_sync=False):
        """Replace the edge of the specified ID in this graph.

        If ``data`` contains the ``_key`` key, it is ignored.

        If the ``_rev`` key is in ``data``, the revision of the target
        edge must match against its value. Otherwise a RevisionMismatch
        error is thrown. If ``rev`` is also provided, its value is preferred.

        The ``_from`` and ``_to`` attributes are immutable, and they are
        ignored if present in ``data``

        :param edge_id: the ID of the edge to be removed
        :type edge_id: str
        :param data: the body to replace the edge with
        :type data: dict
        :param rev: the edge revision must match this value
        :type rev: str or None
        :param wait_for_sync: wait for the replace to sync to disk
        :type wait_for_sync: bool
        :returns: the id, rev and key of the replaced edge
        :rtype: dict
        :raises: RevisionMismatchError, EdgeReplaceError
        """
        params = {"waitForSync": wait_for_sync}
        if rev is not None:
            params["rev"] = rev
        elif "_rev" in data:
            params["rev"] = data["_rev"]
        res = self._api.put(
            "/_api/gharial/{}/edge/{}".format(self.name, edge_id),
            params=params,
            data=data
        )
        if res.status_code == 412:
            raise RevisionMismatchError(res)
        elif res.status_code not in {200, 202}:
            raise EdgeReplaceError(res)
        return res.obj["edge"]

    def remove_edge(self, edge_id, rev=None, wait_for_sync=False):
        """Remove the edge of the specified ID from this graph.

        :param edge_id: the ID of the edge to be removed
        :type edge_id: str
        :param rev: the edge revision must match this value
        :type rev: str or None
        :raises: RevisionMismatchError, EdgeRemoveError
        """
        params = {"waitForSync": wait_for_sync}
        if rev is not None:
            params["rev"] = rev
        res = self._api.delete(
            "/_api/gharial/{}/edge/{}".format(self.name, edge_id),
            params=params
        )
        if res.status_code == 412:
            raise RevisionMismatchError(res)
        elif res.status_code not in {200, 202}:
            raise EdgeRemoveError(res)

    ###################
    # Graph Traversal #
    ###################

    def execute_traversal(self, start_vertex, direction=None,
            strategy=None, order=None, item_order=None, uniqueness=None,
            max_iterations=None, min_depth=None, max_depth=None,
            init=None, filters=None, visitor=None, expander=None, sort=None):
        """Execute a graph traversal and return the visited vertices.

        For more details on ``init``, ``filter``, ``visitor``, ``expander``
        and ``sort`` please refer to the ArangoDB HTTP API documentation:
        https://docs.arangodb.com/HttpTraversal/README.html

        :param start_vertex: the ID of the start vertex
        :type start_vertex: str
        :param direction: "outbound" or "inbound" or "any"
        :type direction: str
        :param strategy: "depthfirst" or "breadthfirst"
        :type strategy: str
        :param order: "preorder" or "postorder"
        :type order: str
        :param item_order: "forward" or "backward"
        :type item_order: str
        :param uniqueness: uniqueness of vertices and edges visited
        :type uniqueness: dict
        :param max_iterations: max number of iterations in each traversal
        :type max_iterations: int
        :param min_depth: minimum traversal depth
        :type min_depth: int
        :param max_depth: maximum traversal depth
        :type max_depth: int
        :param init: custom init function in Javascript
        :type init: str
        :param filters: custom filter function in Javascript
        :type filters: str
        :param visitor: custom visitor function in Javascript
        :type visitor: str
        :param expander: custom expander function in Javascript
        :type expander: str
        :param sort: custom sorting function in Javascript
        :type sort: str
        :returns: the traversal results
        :rtype: dict
        :raises: GraphTraversalError
        """
        data = {
            "startVertex": start_vertex,
            "graphName": self.name,
            "direction": direction,
            "strategy": strategy,
            "order": order,
            "itemOrder": item_order,
            "uniqueness": uniqueness,
            "maxIterations": max_iterations,
            "minDepth": min_depth,
            "maxDepth": max_depth,
            "init": init,
            "filter": filters,
            "visitor": visitor,
            "expander": expander,
            "sort": sort
        }
        data = {k: v for k, v in data.items() if v is not None}
        res = self._api.post("/_api/traversal", data=data)
        if res.status_code != 200:
            raise GraphTraversalError(res)
        return res.obj["result"]