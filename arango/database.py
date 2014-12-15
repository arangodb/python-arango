"""ArangoDB Database."""


from arango.utils import camelify, uncamelify
from arango.query import Query
from arango.batch import Batch
from arango.graph import Graph
from arango.collection import Collection
from arango.exceptions import *


class Database(object):
    """A wrapper around database specific API.

    :param name: the name of this database
    :type name: str
    :param client: the http client
    :type client: arango.client.Client
    """

    def __init__(self, name, client):
        self.name = name
        self._client = client
        self._collection_cache = {}
        self._graph_cache = {}
        self.query = Query(self._client)
        self.batch = Batch(self._client)

    def _update_collection_cache(self):
        """Invalidate the collection cache."""
        cols = self.collections
        real_cols = set(cols["user"] + cols["system"])
        cached_cols = set(self._collection_cache)
        for col_name in cached_cols - real_cols:
            del self._collection_cache[col_name]
        for col_name in real_cols - cached_cols:
            self._collection_cache[col_name] = Collection(
                name=col_name, client=self._client
            )

    def _update_graph_cache(self):
        """Invalidate the graph cache."""
        real_graphs = set(self.graphs)
        cached_graphs = set(self._graph_cache)
        for graph_name in cached_graphs - real_graphs:
            del self._graph_cache[graph_name]
        for graph_name in real_graphs - cached_graphs:
            self._graph_cache[graph_name] = Graph(
                name=graph_name, client=self._client
            )

    @property
    def properties(self):
        """Return all properties of this database.

        :returns: the database properties
        :rtype: dict
        :raises: ArangoDatabasePropertyError
        """
        res = self._client.get("/_api/database/current")
        if res.status_code != 200:
            raise ArangoDatabasePropertyError(res)
        return {uncamelify(k): v for k, v in res.obj["result"].items()}

    @property
    def id(self):
        """Return the ID of this database.

        :returns: the database ID
        :rtype: str
        :raises: ArangoDatabasePropertyError
        """
        return self.properties["id"]

    @property
    def path(self):
        """Return the file path of this database.

        :returns: the file path of this database
        :rtype: str
        :raises: ArangoDatabasePropertyError
        """
        return self.properties["path"]

    @property
    def is_system(self):
        """Return True if this is a system database, False otherwise.

        :returns: True if this is a system database, False otherwise
        :rtype: bool
        :raises: ArangoDatabasePropertyError
        """
        return self.properties["is_system"]

    ########################
    # Handling Collections #
    ########################

    @property
    def collections(self):
        """Return the names of the collections in this database.

        :returns: the names of the collections
        :rtype: dict
        :raises: ArangoCollectionListError
        """
        res = self._client.get("/_api/collection")
        if res.status_code != 200:
            raise ArangoCollectionListError(res)

        user_collections = []
        system_collections = []
        for collection in res.obj["collections"]:
            if collection["isSystem"]:
                system_collections.append(collection["name"])
            else:
                user_collections.append(collection["name"])
        return {"user": user_collections, "system": system_collections}

    def collection(self, name):
        """Return the Collection object of the specified name.

        :param name: the name of the collection
        :type name: str
        :returns: the requested collection object
        :rtype: arango.collection.Collection
        :raises: TypeError, ArangoCollectionNotFound
        """
        if not isinstance(name, str):
            raise TypeError("Expecting a str.")
        if name in self._collection_cache:
            return self._collection_cache[name]
        else:
            self._update_collection_cache()
            if name not in self._collection_cache:
                raise ArangoCollectionNotFoundError(name)
            return self._collection_cache[name]

    def add_collection(self, name, wait_for_sync=False, do_compact=True,
                       journal_size=None, is_system=False, is_volatile=False,
                       key_options=None, is_edge=False):
        """Add a new collection in this database.

        #TODO expand on key_options

        :param name: name of the new collection
        :type name: str
        :param wait_for_sync: whether or not the collection waits disk syncs
        :type wait_for_sync: bool
        :param do_compact: whether or not the collection is compacted
        :type do_compact: bool
        :param journal_size: the maximal size of journal or datafile
        :type journal_size: str or int
        :param is_system: whether or not the collection is a system collection
        :type is_system: bool
        :param is_volatile: whether or not the collection is in memory only
        :type is_volatile: bool
        :param key_options: settings for document key generation
        :type key_options: dict
        :param is_edge: whether or not the collection is an edge collection
        :type is_edge: bool
        :raises: ArangoCollectionAddError
        """
        data = {
            "name": name,
            "waitForSync": wait_for_sync,
            "doCompact": do_compact,
            "isSystem": is_system,
            "isVolatile": is_volatile,
            "type": 3 if is_edge else 2,
            "keyOptions": {} if key_options is None else key_options,
        }
        if journal_size:
            data["journalSize"] = journal_size

        res = self._client.post("/_api/collection", data=data)
        if res.status_code != 200:
            raise ArangoCollectionAddError(res)
        self._update_collection_cache()
        return {uncamelify(k): v for k, v in res.obj.items()}

    def remove_collection(self, name):
        """Remove the specified collection from this database.

        :param name: the name of the collection to remove
        :type name: str
        :returns: the updated names of the collection in this database
        :rtype: dict
        :raises: ArangoCollectionRemoveError
        """
        res = self._client.delete("/_api/collection/{}".format(name))
        if res.status_code != 200:
            raise ArangoCollectionRemoveError(res)
        self._update_collection_cache()
        return self.collections

    def rename_collection(self, name, new_name):
        """Rename the specified collection in this database.

        :param name: the name of the collection to rename
        :type name: str
        :param new_name: the new name for the collection
        :type new_name: str
        :returns: the updated names of the collections in this database
        :rtype: dict
        :raises: ArangoCollectionRenameError
        """
        res = self._client.put(
            "/_api/collection/{}/rename".format(name),
            data={"name": new_name}
        )
        if res.status_code != 200:
            raise ArangoCollectionRenameError(res)
        self._update_collection_cache()
        return self.collections

    ##########################
    # Handling AQL Functions #
    ##########################

    @property
    def aql_functions(self):
        """Return the AQL functions defined in this database.

        :returns: a mapping of AQL function names to its javascript code
        :rtype: dict
        :raises: ArangoAQLFunctionListError
        """
        res = self._client.get("/_api/aqlfunction")
        if res.status_code != 200:
            raise ArangoAQLFunctionListError(res)
        return {func["name"]: func["code"]for func in res.obj}

    def add_aql_function(self, name, code):
        """Add a new AQL function.

        :param name: the name of the new AQL function to add
        :type name: str
        :param code: the stringified javascript code of the new function
        :type code: str
        :returns: the updated AQL functions
        :rtype: dict
        :raises: ArangoAQLFunctionAddError
        """
        data = {"name": name, "code": code}
        res = self._client.post("/_api/aqlfunction", data=data)
        if res.status_code not in (200, 201):
            raise ArangoAQLFunctionAddError(res)
        return self.aql_functions

    def remove_aql_function(self, name, group=True):
        """Remove an existing AQL function.

        If ``group`` is set to True, then the function name provided in
        ``name`` is treated as a namespace prefix, and all functions in
        the specified namespace will be deleted. If set to False, the
        function name provided in ``name`` must be fully qualified,
        including any namespaces.

        :param name: the name of the AQL function to remove
        :type name: str
        :param group: whether or not to treat name as a namespace prefix
        :returns: the updated AQL functions
        :rtype: dict
        :raises: ArangoAQLFunctionRemoveError
        """
        res = self._client.delete(
            "/_api/aqlfunction/{}".format(name),
            params={"group": group}
        )
        if res.status_code != 200:
            raise ArangoAQLFunctionRemoveError(res)
        return self.aql_functions

    ################
    # Transactions #
    ################

    def execute_transaction(self, collections=None, action=None):
        """Execute the transaction and return the result.

        The ``collections`` dict can only have keys ``write`` or ``read``
        with str or list as values. The values must be name(s) of collections
        that exist in this database.

        :param collections: the collections read/modified
        :type collections: dict
        :param action: the ArangoDB commands (in javascript) to be executed
        :type action: str
        :returns: the result from executing the transaction
        :rtype: dict
        :raises: ArangoTransactionExecuteError
        """
        data = {
            collections: {} if collections is None else collections,
            action: "" if action is None else ""
        }
        res = self._client.post("/_api/transaction", data=data)
        if res != 200:
            raise ArangoTransactionExecuteError(res)
        return res.obj["result"]

    ###################
    # Handling Graphs #
    ###################

    @property
    def graphs(self):
        """List all graphs in this database.

        :returns: the graphs in this database
        :rtype: dict
        :raises: ArangoGraphGetError
        """
        res = self._client.get("/_api/gharial")
        if res.status_code not in (200, 202):
            raise ArangoGraphListError(res)
        return {graph["_key"]: graph for graph in res.obj["graphs"]}

    def graph(self, name):
        """Return the Graph object of the specified name.

        :param name: the name of the graph
        :type name: str
        :returns: the requested graph object
        :rtype: arango.graph.Graph
        :raises: TypeError, ArangoGraphNotFound
        """
        if not isinstance(name, str):
            raise TypeError("Expecting a str.")
        if name in self._graph_cache:
            return self._graph_cache[name]
        else:
            self._update_graph_cache()
            if name not in self._graph_cache:
                raise ArangoGraphNotFoundError(name)
            return self._graph_cache[name]

    def add_graph(self, name, edge_definitions=None,
                  orphan_collections=None):
        """Add a new graph in this database.

        # TODO expand on edge_definitions and orphan_collections

        :param name: name of the new graph
        :type name: str
        :param edge_definitions: definitions for edges
        :type edge_definitions: list
        :param orphan_collections: names of additional vertex collections
        :type orphan_collections: list
        :returns: the details on the new graph
        :rtype: dict
        :raises: ArangoGraphAddError
        """
        data = {"name": name}
        if edge_definitions is not None:
            data["edgeDefinitions"] = edge_definitions
        if orphan_collections is not None:
            data["orphanCollections"] = orphan_collections

        res = self._client.post("/_api/gharial", data=data)
        if res.status_code != 201:
            raise ArangoGraphAddError(res)
        self._update_graph_cache()
        return res.obj["graph"]

    def remove_graph(self, name):
        """Delete the graph of the given name from this database.

        :param name: the name of the graph to delete
        :type name: str
        :raises: ArangoGraphRemoveError
        """
        res = self._client.delete("/_api/gharial/{}".format(name))
        if res.status_code != 200:
            raise ArangoGraphRemoveError(res)
        self._update_graph_cache()

    def execute_traversal(self, start_vertex, edge_collection=None,
            graph_name=None, direction=None, strategy=None,
            order=None, item_order=None, uniqueness=None,
            max_iterations=None, min_depth=None, max_depth=None,
            init=None, filter=None, visitor=None, expander=None,
            sort=None):
        """Execute a graph traversal and return the visited vertices.

        Either ``edge_collection`` and ``graph_name`` should be provided.
        If both are set, the value ``graph_name`` is preferred.

        For more details on ``init``, ``filter``, ``visitor``, ``expander``
        and ``sort`` please refer to the ArangoDB HTTP API documentation:
        https://docs.arangodb.com/HttpTraversal/README.html

        :param start_vertex: the ID of the start vertex (e.g. "col/key")
        :type start_vertex: str
        :param edge_collection: the name of the edge collection
        :type edge_collection: str
        :param graph_name: the name of the graph that contains the edges
        :type graph_name: str
        :param direction: traversal direction ("outbound/inbound/any")
        :type direction: str
        :param strategy: ``depthfirst`` or ``breadthfirst``
        :type strategy: str
        :param order: ``preorder`` or ``postorder``
        :type order: str
        :param item_order: ``forward`` or ``backward``
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
        :param filter: custom filter function in Javascript
        :type filter: str
        :param visitor: custom visitor function in Javascript
        :type visitor: str
        :param expander: custom expander function in Javascript
        :type expander: str
        :param sort: custom sorting function in Javascript
        :type sort: str
        :returns:
        :rtype: dict
        :raises: ArangoGraphTraversalError
        """
        res = self._client.post(
            "/_api/traversal",
            params = {
                camelify(arg): val
                for arg, val in locals().iteritems()
                if val is not None
            }
        )
        if res.status_code != 200:
            raise ArangoGraphTraversalError(res)
        return res.obj["result"]
