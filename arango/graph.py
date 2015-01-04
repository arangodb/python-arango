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
        :raises: ArangoGraphPropertiesError
        """
        res = self._api.get(
            "/_api/gharial/{}".format(self.name)
        )
        if res.status_code != 200:
            raise ArangoGraphPropertiesError(res)
        return uncamelify(res.obj["graph"])

    @property
    def id(self):
        """Return the ID of this graph.

        :returns: the ID of this graph
        :rtype: str
        :raises: ArangoGraphPropertiesError
        """
        return self.properties["_id"]

    @property
    def revision(self):
        """Return the revision of this graph.

        :returns: the revision of this graph
        :rtype: str
        :raises: ArangoGraphPropertiesError
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
        :raises: ArangoGraphPropertiesError
        """
        return self.properties["orphan_collections"]

    @property
    def vertex_collections(self):
        """Return the vertex collections of this graph.

        :returns: the string names of the vertex collections
        :rtype: list
        :raises: ArangoVertexCollectionListError
        """
        res = self._api.get(
            "/_api/gharial/{}/vertex".format(self.name)
        )
        if res.status_code != 200:
            raise ArangoVertexCollectionListError(res)
        return res.obj["collections"]

    def add_vertex_collection(self, collection_name):
        """Add a vertex collection to this graph.

        :param collection_name: the name of the vertex collection to add
        :type collection_name: str
        :returns: the updated list of the vertex collection names
        :rtype: list
        :raises: ArangoVertexCollectionAddError
        """
        res = self._api.post(
            "/_api/gharial/{}/vertex".format(self.name),
            data={"collection": collection_name}
        )
        if res.status_code != 201:
            raise ArangoVertexCollectionAddError(res)
        return self.vertex_collections

    def remove_vertex_collection(self, collection_name, drop_collection=False):
        """Remove a vertex collection from this graph.

        :param collection_name: the name of the vertex collection to remove
        :type collection_name: str
        :param drop_collection: whether or not to drop the collection also
        :type drop_collection: bool
        :returns: the updated list of the vertex collection names
        :rtype: list
        :raises: ArangoVertexCollectionRemoveError
        """
        res = self._api.delete(
            "/_api/gharial/{}/vertex/{}".format(self.name, collection_name),
            params={"dropCollection": drop_collection}
        )
        if res.status_code != 200:
            raise ArangoVertexCollectionRemoveError(res)
        return self.vertex_collections

    #############################
    # Handling Edge Definitions #
    #############################

    @property
    def edge_definitions(self):
        """Return the edge definitions of this graph.

        :returns: the edge definitions of this graph
        :rtype: list
        :raises: ArangoGraphPropertiesError
        """
        return self.properties["edge_definitions"]

    def add_edge_definition(self, edge_definition):
        """Add a edge definition to this graph.

        An edge definition looks like this:
        {
            "collection" : "edge_col01",
            "from" : ["vertex_col01"],
            "to": ["vertex_col02"]
        }
        The object must contain valid collection names.

        :param edge_definition: the edge definition object
        :type edge_definition: dict
        :returns: the updated list of edge definitions
        :rtype: list
        :raises: ArangoEdgeDefinitionAddError
        """
        res = self._api.post(
            "/_api/gharial/{}/edge".format(self.name),
            data=edge_definition
        )
        if res.status_code != 201:
            raise ArangoEdgeDefinitionAddError(res)
        return res.obj["graph"]["edgeDefinitions"]

    def replace_edge_definition(self, edge_collection_name, edge_definition):
        """Replace an edge definition in this graph.

        An edge definition looks like this:
        {
            "collection" : "edge_col01",
            "from" : ["vertex_col01"],
            "to": ["vertex_col02"]
        }
        The object must contain valid collection names.

        :param edge_collection_name: the name of the edge collection
        :type edge_collection_name: str
        :param edge_definition: the new edge definition object
        :type edge_definition: dict
        :returns: the updated list of edge definitions
        :rtype: list
        :raises: ArangoEdgeDefinitionReplaceError
        """
        res = self._api.put(
            "/_api/gharial/{}/edge/{}".format(self.name, edge_collection_name),
            data=edge_definition
        )
        if res.status_code != 200:
            raise ArangoEdgeDefinitionReplaceError(res)
        return res.obj["graph"]["edgeDefinitions"]

    def remove_edge_definition(self, edge_collection_name,
                               drop_collection=False):
        """Remove the specified edge definition from this graph.

        :param edge_collection_name: the name of the edge collection to remove
        :type edge_collection_name: str
        :param drop_collection: whether or not to drop the collection also
        :type drop_collection: bool
        :returns: the updated list of edge definitions
        :rtype: list
        :raises: ArangoEdgeDefinitionRemoveError
        """
        res = self._api.delete(
            "/_api/gharial/{}/edge/{}".format(self.name, edge_collection_name),
            params={"dropCollection": drop_collection}
        )
        if res.status_code != 200:
            raise ArangoEdgeDefinitionRemoveError(res)
        return res.obj["graph"]["edgeDefinitions"]

    #####################
    # Handling Vertices #
    #####################

    def get_vertex(self, vertex_collection_name, key, rev=None):
        """Return the vertex of the specified ID.

        If the vertex revision ``rev`` is specified, the revision of the
        retrieved vertex must match against it.

        :param key: the vertex ID ("collection/key")
        :type key: str
        :param rev: the vertex revision
        :type rev: str
        :returns: the vertex
        :rtype: dict
        :raises: ArangoVertexGetError
        """
        res = self._api.get(
            "/_api/gharial/{}/vertex/{}/{}".format(
                self.name, vertex_collection_name, key
            ),
            params={"rev": rev} if rev is not None else {}
        )
        if res.status_code != 200:
            raise ArangoVertexGetError(res)
        return res.obj["vertex"]

    def add_vertex(self, vertex_collection_name, key=None, data=None,
                   wait_for_sync=False):
        """Add a new vertex to the specified vertex collection.

        :param vertex_collection_name: the name of the vertex collection
        :type vertex_collection_name: str
        :param data: the body of the new vertex
        :type data: dict
        :param key: the key of the new vertex (must not be in use)
        :type key: str
        :param wait_for_sync: wait for the add to sync to disk
        :type wait_for_sync: bool
        :return: the id, rev and key of the new vertex
        :rtype: dict
        :raises: ArangoVertexAddError
        """
        if data is None:
            data = {}
        if key is not None:
            data["_key"] = key
        res = self._api.post(
            "/_api/gharial/{}/vertex/{}".format(
                self.name, vertex_collection_name
            ),
            params={"waitForSync": wait_for_sync},
            data=data
        )
        if res.status_code not in {201, 202}:
            raise ArangoVertexAddError(res)
        return res.obj["vertex"]

    def update_vertex(self, vertex_collection_name, key, data, rev=None,
                      keep_none=True, wait_for_sync=False):
        """Update a vertex in the specified vertex collection.

        If ``rev`` is provided and the ``_rev`` attribute is in ``data``,
        the value of the former is preferred. If the revision is given it must
        match against that of the target document.

        :param vertex_collection_name: name of the vertex collection
        :type vertex_collection_name: str
        :param key: the vertex key
        :type key: str
        :param data: the body of the vertex to update with
        :type data: dict
        :param keep_none: whether or not to keep the keys with value None
        :type keep_none: bool
        :param wait_for_sync: wait for the update to sync to disk
        :type wait_for_sync: bool
        :return: the id, rev and key of the updated vertex
        :rtype: dict
        :raises: ArangoVertexUpdateError
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
            "/_api/gharial/{}/vertex/{}/{}".format(
                self.name, vertex_collection_name, key
            ),
            params=params,
            data=data
        )
        if res.status_code not in {200, 202}:
            raise ArangoVertexUpdateError(res)
        return res.obj["vertex"]

    def replace_vertex(self, vertex_collection_name, key, data, rev=None,
                       wait_for_sync=False):
        """Replace a vertex in the specified vertex collection.

        :param vertex_collection_name: name of the vertex collection
        :type vertex_collection_name: str
        :param key: the vertex key
        :type key: str
        :param data: the body of the vertex to replace
        :type data: dict
        :param wait_for_sync: wait for replace to sync to disk
        :type wait_for_sync: bool
        :return: the id, rev and key of the replaced vertex
        :rtype: dict
        :raises: ArangoVertexReplaceError
        """
        params = {"waitForSync": wait_for_sync}
        if rev is not None:
            params["rev"] = rev
        elif "_rev" in data:
            params["rev"] = data["_rev"]
        res = self._api.put(
            "/_api/gharial/{}/vertex/{}/{}".format(
                self.name, vertex_collection_name, key
            ),
            params=params,
            data=data
        )
        if res.status_code not in {200, 202}:
            raise ArangoVertexReplaceError(res)
        return res.obj["vertex"]

    def remove_vertex(self, vertex_collection_name, key, rev=None):
        """Remove a vertex from the specified vertex collection.

        :param vertex_collection_name: name of the vertex collection
        :type vertex_collection_name: str
        :param key: the vertex key
        :type key: str
        :param rev: the vertex revision
        :type rev: str
        :raises: ArangoVertexRemoveError
        """
        res = self._api.delete(
            "/_api/gharial/{}/vertex/{}/{}".format(
                self.name, vertex_collection_name, key
            ),
            params={"rev": rev} if rev is not None else {}
        )
        if res.status_code not in {200, 202}:
            raise ArangoVertexRemoveError(res)

    ##################
    # Handling Edges #
    ##################

    def get_edge(self, edge_collection_name, key, rev=None):
        """Return the edge from the edge collection in this graph

        If the revision ``rev`` is specified, it must match against
        the revision of the retrieved edge.

        :param edge_collection_name: the name of the edge collection
        :type edge_collection_name: str
        :param key: the vertex key
        :type key: str
        :param rev: the edge revision
        :type rev: str
        :returns: the edge object
        :rtype: dict
        :raises: ArangoEdgeGetError
        """
        res = self._api.get(
            "/_api/gharial/{}/edge/{}/{}".format(
                self.name, edge_collection_name, key
            ),
            params={} if rev is None else {"rev": rev}
        )
        if res.status_code != 200:
            raise ArangoEdgeGetError(res)
        return res.obj["edge"]

    def add_edge(self, edge_collection_name, from_vertex_id, to_vertex_id,
                 key=None, data=None, wait_for_sync=False):
        """Add a new edge to the specified edge collection of this graph.

        The ``from_vertex`` and ``to_vertex`` must be valid vertex IDs
        ("collection/key").

        :param edge_collection_name: the name of the edge collection
        :type edge_collection_name: str
        :param from_vertex_id: the ID ("collection/key") of the from vertex
        :type from_vertex_id: str
        :param to_vertex_id: the ID ("collection/key") of the to vertex
        :type to_vertex_id: str
        :param key: the key for the edge (must not be in use)
        :type key: str
        :param wait_for_sync: wait for the add to sync to disk
        :type wait_for_sync: bool
        :return: the id, rev and key of the new edge
        :rtype: dict
        :raises: ArangoEdgeAddError
        """
        if data is None:
            data = {}
        data["_from"] = from_vertex_id
        data["_to"] = to_vertex_id
        if key is not None:
            data["_key"] = key
        res = self._api.post(
            "/_api/gharial/{}/edge/{}".format(
                self.name, edge_collection_name
            ),
            params={"waitForSync": wait_for_sync},
            data=data
        )
        if res.status_code not in {201, 202}:
            raise ArangoEdgeAddError(res)
        return res.obj["edge"]

    def update_edge(self, edge_collection_name, key, data, rev=None,
                    keep_none=True, wait_for_sync=False):
        """Update an edge in the specified edge collection.

        :param edge_collection_name: the name of the edge collection
        :type edge_collection_name: str
        :param key: the key for the edge (must not be in use)
        :type key: str
        :param data: the body of the edge to update with
        :type data: dict
        :param keep_none: whether or not to keep the keys with value None
        :type keep_none: bool
        :param wait_for_sync: wait for the update to sync to disk
        :type wait_for_sync: bool
        :return: the id, rev and key of the updated edge
        :rtype: dict
        :raises: ArangoEdgeUpdateError
        """
        params = {
            "waitForSync": wait_for_sync,
            "keepNull": keep_none
        }
        if "_rev" in data:
            params["rev"] = data["_rev"]

        res = self._api.patch(
            "/_api/gharial/{}/edge/{}/{}".format(
                self.name, edge_collection_name, key
            ),
            params=params,
            data=data
        )
        if res.status_code not in {200, 202}:
            raise ArangoEdgeUpdateError(res)
        return res.obj["edge"]

    def replace_edge(self, edge_collection_name, key, data,
                     wait_for_sync=False):
        """Replace an edge in the specified edge collection.

        :param edge_collection_name: the name of the edge collection
        :type edge_collection_name: str
        :param key: the key for the edge (must not be in use)
        :type key: str
        :param data: the body of the edge to replace with
        :type data: dict
        :param wait_for_sync: wait for the replace to sync to disk
        :type wait_for_sync: bool
        :returns: the id, rev and key of the replaced edge
        :rtype: dict
        :raises: ArangoEdgeReplaceError
        """
        params = {"waitForSync": wait_for_sync}
        if "_rev" in data:
            params["rev"] = data["_rev"]
        res = self._api.put(
            "/_api/gharial/{}/edge/{}/{}".format(
                self.name, edge_collection_name, key
            ),
            params=params,
            data=data
        )
        if res.status_code not in {200, 202}:
            raise ArangoEdgeReplaceError(res)
        return res.obj["edge"]

    def remove_edge(self, edge_collection_name, key, rev=None):
        """Remove an edge from the graph.

        :param edge_collection_name: the name of the edge collection
        :type edge_collection_name: str
        :param key: the key for the edge (must not be in use)
        :type key: str
        :param rev: the edge revision
        :type rev: str or None
        :raises: ArangoEdgeRemoveError
        """
        res = self._api.delete(
            "/_api/gharial/{}/edge/{}/{}".format(
                self.name, edge_collection_name, key
            ),
            params={} if rev is None else {"rev": rev}
        )
        if res.status_code not in {200, 202}:
            raise ArangoEdgeRemoveError(res)
