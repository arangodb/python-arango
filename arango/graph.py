"""ArangoDB Graph."""
from arango.exceptions import *

class Graph(object):
    """A wrapper around ArangoDB graph API.

    :param name: the name of the graph
    :type name: str
    :param client: the http client
    :type client: arango.client.Client
    """

    def __init__(self, name, client):
        self.name = name
        self._client = client

    @property
    def properties(self):
        """Return the properties of this graph.

        :returns: the properties of this graph
        :rtype: dict
        :raises: ArangoGraphPropertiesError
        """
        res = self._client.get("/_api/gharial/{}".format(self.name))
        if res.status_code != 200:
            raise ArangoGraphPropertiesError(res)
        return res.obj["graph"]

    ###############################
    # Handling Vertex Collections #
    ###############################

    @property
    def orphan_collections(self):
        """Return the orphan collections of this graph.

        :returns: the names of the orphan collections
        :rtype: list
        :raises: ArangoGraphPropertiesError
        """
        return self.properties["orphanCollections"]

    @property
    def vertex_collections(self):
        """Return the vertex collections in this graph.

        :returns: the names of the vertex collections
        :rtype: list
        :raises: ArangoVertexCollectionListError
        """
        res = self._client.get("/_api/gharial/{}/vertex".format(self.name))
        if res.status_code != 200:
            raise ArangoVertexCollectionListError(res)
        return res.obj["collections"]

    def add_vertex_collection(self, col_name):
        """Add a vertex collection to this graph.

        :param col_name: the name of the vertex collection to add
        :type col_name: str
        :returns: the updated list of the vertex collections
        :rtype: list
        :raises: ArangoVertexCollectionAddError
        """
        res = self._client.post(
            "/_api/gharial/{}/vertex".format(self.name),
            data={"collection": col_name}
        )
        if res.status_code != 201:
            raise ArangoVertexCollectionAddError(res)
        return self.vertex_collections

    def remove_vertex_collection(self, col_name, drop_collection=False):
        """Remove a vertex collection from this graph.

        :param col_name: the name of the vertex collection to remove
        :type col_name: str
        :param drop_collection: whether or not to drop the collection as well
        :type drop_collection: bool
        :returns: the updated list of the vertex collections
        :rtype: list
        :raises: ArangoVertexCollectionRemoveError
        """
        res = self._client.delete(
            "/_api/gharial/{}/vertex/{}".format(self.name, col_name),
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
        return self.properties["edgeDefinitions"]

    def add_edge_definition(self, edge_definition):
        """Add a edge definition to this graph.

        :param edge_definition: the edge definition
        :type edge_definition: dict
        :returns: the updated list of edge definitions
        :rtype: list
        :raises: ArangoEdgeDefinitionAddError
        """
        res = self._client.post(
            "/_api/gharial/{}/edge".format(self.name),
            data=edge_definition
        )
        if res.status_code != 201:
            raise ArangoEdgeDefinitionAddError(res)
        return self.edge_definitions

    def replace_edge_definition(self, col_name, new_edge_definition):
        """Replace an edge definition in this graph.

        :param col_name: the name of the edge collection used in the definition
        :type col_name: str
        :param new_edge_definition: the edge definition
        :type new_edge_definition: dict
        :returns: the updated list of edge definitions
        :rtype: list
        :raises: ArangoEdgeDefinitionReplaceError
        """
        res = self._client.post(
            "/_api/gharial/{}/edge/{}".format(self.name, col_name),
            data=new_edge_definition
        )
        if res.status_code != 200:
            raise ArangoEdgeDefinitionReplaceError(res)
        return self.edge_definitions

    def remove_edge_definition(self, col_name, drop_collection=False):
        """Remove an edge definition from this graph.

        :param col_name: the name of the edge collection used in the definition
        :type col_name: str
        :param drop_collection: whether or not to drop the collection as well
        :type drop_collection: bool
        :returns: the updated list of edge definitions
        :rtype: list
        :raises: ArangoEdgeDefinitionRemoveError
        """
        res = self._client.delete(
            "/_api/gharial/{}/edge/{}".format(self.name, col_name),
            params={"dropCollection": drop_collection}
        )
        if res.status_code != 200:
            raise ArangoEdgeDefinitionRemoveError(res)
        return self.edge_definitions

    #####################
    # Handling Vertices #
    #####################

    def get_vertex(self, col_name, key, rev=None):
        """Return the vertex from the specified vertex collection.

        If the revision ``rev`` is specified, it is compared against
        the revision of the retrieved vertex.

        :param col_name: the name of the collection
        :type col_name: str
        :param key: the vertex key
        :type key: str
        :param rev: the vertex revision
        :type rev: str
        :returns: the vertex
        :rtype: dict
        :raises: ArangoVertexGetError
        """
        res = self._client.get(
            "/_api/gharial/{}/vertex/{}/{}".format(
                self.name, col_name, key
            ),
            params={"rev": rev} if rev is not None else {}
        )
        if res.status_code != 200:
            raise ArangoVertexGetError(res)
        return res.obj["vertex"]

    def create_vertex(self, col_name, data, wait_for_sync=False):
        """Create a new vertex in the specified vertex collection.

        :param col_name: the name of the vertex collection
        :type col_name: str
        :param data: the body of the new vertex
        :type data: dict
        :param wait_for_sync: wait for the create to sync to disk
        :type wait_for_sync: bool
        :return: the id, rev and key of the new vertex
        :rtype: dict
        :raises: ArangoVertexCreateError
        """
        res = self._client.post(
            "_api/gharial/{}/vertex/{}".format(self.name, col_name),
            params={"waitForSync": wait_for_sync},
            data=data
        )
        if res.status_code not in {201, 202}:
            raise ArangoVertexCreateError(res)
        return res.obj["vertex"]

    def patch_vertex(self, col_name, data, keep_none=True,
                      wait_for_sync=False):
        """Patch a vertex in the specified vertex collection.

        :param col_name: the name of the vertex collection
        :type col_name: str
        :param data: the body of the vertex to patch
        :type data: dict
        :param keep_none: whether or not to keep the keys with value None
        :type keep_none: bool
        :param wait_for_sync: wait for the patch to sync to disk
        :type wait_for_sync: bool
        :return: the id, rev and key of the patched vertex
        :rtype: dict
        :raises: ArangoVertexPatchError
        """
        if "_key" not in data:
            ArangoVertexInvalidError("'_key' is missing")
        params = {
            "waitForSync": wait_for_sync,
            "keepNull": keep_none
        }
        if "_rev" in data:
            params["rev"] = data["_rev"]

        res = self._client.patch(
            "_api/gharial/{}/vertex/{}/{}".format(
                self.name, col_name, data["_key"]
            ),
            params=params,
            data=data
        )
        if res.status_code not in {200, 202}:
            raise ArangoVertexPatchError(res)
        return res.obj["vertex"]

    def replace_vertex(self, col_name, data, wait_for_sync=False):
        """Replace a vertex in the specified vertex collection.

        :param col_name: the name of the vertex collection
        :type col_name: str
        :param data: the body of the vertex to replace
        :type data: dict
        :param wait_for_sync: wait for replace to sync to disk
        :type wait_for_sync: bool
        :return: the id, rev and key of the replaced vertex
        :rtype: dict
        :raises: ArangoVertexReplaceError
        """
        if "_key" not in data:
            ArangoVertexInvalidError("'_key' is missing")
        params = {"waitForSync": wait_for_sync}
        if "_rev" in data:
            params["rev"] = data["_rev"]
        res = self._client.put(
            "_api/gharial/{}/vertex/{}/{}".format(
                self.name, col_name, data["_key"]
            ),
            params=params,
            data=data
        )
        if res.status_code not in {200, 202}:
            raise ArangoVertexReplaceError(res)
        return res.obj["vertex"]

    def delete_vertex(self, col_name, key, rev=None):
        """Delete a vertex from the specified vertex collection.

        :param col_name: the name of the collection
        :type col_name: str
        :param key: the vertex key
        :type key: str
        :param rev: the vertex revision
        :type rev: str
        :returns: True
        :rtype: bool
        :raises: ArangoVertexDeleteError
        """
        res = self._client.delete(
            "/_api/gharial/{}/vertex/{}/{}".format(
                self.name, col_name, key
            ),
            params={"rev": rev} if rev is not None else {}
        )
        if res.status_code != 200:
            raise ArangoVertexDeleteError(res)
        return True

    ##################
    # Handling Edges #
    ##################

    def get_edge(self, col_name, key, rev=None):
        """Return the edge from the specified edge collection.

        If the revision ``rev`` is specified, it is compared against
        the revision of the retrieved edge.

        :param col_name: the name of the collection
        :type col_name: str
        :param key: the edge key
        :type key: str
        :param rev: the edge revision
        :type rev: str
        :returns: the edge
        :rtype: dict
        :raises: ArangoEdgeGetError
        """
        res = self._client.get(
            "/_api/gharial/{}/edge/{}/{}".format(
                self.name,
                col_name,
                key
            ),
            params={} if rev is None else {"rev": rev}
        )
        if res.status_code != 200:
            raise ArangoEdgeGetError(res)
        return res.obj["edge"]

    def create_edge(self, col_name, data, wait_for_sync=False):
        """Create a new edge in the specified edge collection.

        :param col_name: the name of the edge collection
        :type col_name: str
        :param data: the body of the new edge
        :type data: dict
        :param wait_for_sync: wait for the create to sync to disk
        :type wait_for_sync: bool
        :return: the id, rev and key of the new edge
        :rtype: dict
        :raises: ArangoEdgeCreateError
        """
        if "_from" not in data or "_to" not in data:
            raise ArangoEdgeInvalidError(
                "the '_from' and '_to' keys are missing"
            )
        res = self._client.post(
            "/_api/gharial/{}/edge/{}".format(self.name, col_name),
            params={"waitForSync": wait_for_sync},
            data=data
        )
        if res.status_code not in {201, 202}:
            raise ArangoEdgeCreateError(res)
        return res.obj["edge"]

    def patch_edge(self, col_name, data, keep_none=True,
                    wait_for_sync=False):
        """Patch an edge in the specified edge collection.

        :param col_name: the name of the edge collection
        :type col_name: str
        :param data: the body of the edge to patch
        :type data: dict
        :param keep_none: whether or not to keep the keys with value None
        :type keep_none: bool
        :param wait_for_sync: wait for the patch to sync to disk
        :type wait_for_sync: bool
        :return: the id, rev and key of the patched edge
        :rtype: dict
        :raises: ArangoEdgePatchError
        """
        if "_key" not in data:
            ArangoEdgeInvalidError("'_key' is missing")
        params = {
            "waitForSync": wait_for_sync,
            "keepNull": keep_none
        }
        if "_rev" in data:
            params["rev"] = data["_rev"]

        res = self._client.patch(
            "/_api/gharial/{}/edge/{}/{}".format(
                self.name,
                col_name,
                data["_key"]
            ),
            params=params,
            data=data
        )
        if res.status_code not in {200, 202}:
            raise ArangoEdgeModifyError(res)
        return res.obj["edge"]

    def replace_edge(self, col_name, data, wait_for_sync=False):
        """Replace an edge in the specified edge collection.

        :param col_name: the name of the edge collection
        :type col_name: str
        :param data: the body of the edge to replace
        :type data: dict
        :param wait_for_sync: wait for replace to sync to disk
        :type wait_for_sync: bool
        :return: the id, rev and key of the replaced edge
        :rtype: dict
        :raises: ArangoEdgeReplaceError
        """
        if "_key" not in data:
            ArangoEdgeInvalidError("'_key' is missing")
        params = {"waitForSync": wait_for_sync}
        if "_rev" in data:
            params["rev"] = data["_rev"]
        res = self._client.put(
            "_api/gharial/{}/edge/{}/{}".format(
                self.name, col_name, data["_key"]
            ),
            params=params,
            data=data
        )
        if res.status_code not in {200, 202}:
            raise ArangoEdgeReplaceError(res)
        return res.obj["edge"]

    def delete_edge(self, col_name, key, rev=None):
        """Delete an edge from the specified edge collection.

        :param col_name: the name of the edge collection
        :type col_name: str
        :param key: the edge key
        :type key: str
        :param rev: the edge revision
        :type rev: str or None
        :returns: True
        :rtype: bool
        :raises: ArangoEdgeDeleteError
        """
        res = self._client.delete(
            "/_api/gharial/{}/edge/{}/{}".format(
                self.name, col_name, key
            ),
            params={} if rev is None else {"rev": rev}
        )
        if res.status_code != 200:
            raise ArangoEdgeDeleteError(res)
        return True
