"""ArangoDB Database."""


from arango.query import Query
from arango.graph import Graph
from arango.collection import Collection
from arango.exceptions import *


class Database(object):
    """A wrapper around ArangoDB database API.

    :param name: the name of this database
    :param client: the http client
    :type name: str
    :type client: arango.client.Client
    """

    def __init__(self, name, client):
        self.name = name
        self._client = client
        self._collection_cache = {}
        self._graph_cache = {}
        self._query = Query(self._client)

    def _update_collection_cache(self):
        """Invalidate the collection cache."""
        real_cols = set(self.collections)
        cached_cols = set(self._collection_cache)
        for col_name in cached_cols - real_cols:
            del self._collection_cache[col_name]
        for col_name in real_cols - cached_cols:
            self._collection_cache[col_name] = Collection(
                name=col_name,
                client=self._client
            )

    def _update_graph_cache(self):
        """Invalidate the graph cache."""
        real_graphs = set(self.graphs)
        cached_graphs = set(self._graph_cache)
        for graph_name in cached_graphs - real_graphs:
            del self._graph_cache[graph_name]
        for graph_name in real_graphs - cached_graphs:
            self._graph_cache[graph_name] = Graph(
                name=graph_name,
                client=self._client
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
        return res.obj["result"]

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
        return self.properties["isSystem"]

    ########################
    # Handling Collections #
    ########################

    @property
    def collections(self):
        """Return the names of the collections in this database.

        :returns: the list of string names of the collections
        :rtype: list
        :raises: ArangoCollectionListError
        """
        res = self._client.get("/_api/collection")
        if res.status_code != 200:
            raise ArangoCollectionListError(res)
        return res.obj["names"]

    def col(self, name):
        """Alias for self.collection"""
        return self.collection(name)

    def collection(self, name):
        """Return the Collection object of the specified name.

        :param name: the name of the collection
        :type name: str
        :returns: the requested collection object
        :rtype: Collection
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

    def create_collection(self, name, wait_for_sync=False, do_compact=True,
                          journal_size=None, is_system=False, is_volatile=False,
                          key_options=None, is_edge=False):
        """Create a new collection in this database.

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
        :raises: ArangoCollectionCreateError
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
            raise ArangoCollectionCreateError(res)
        self._update_collection_cache()
        return res.obj

    def delete_collection(self, name):
        """Delete the specified collection in this database.

        :param name: the name of the collection to delete
        :type name: str
        :returns: True
        :rtype: boolean
        :raises: ArangoCollectionDeleteError
        """
        res = self._client.delete("/_api/collection/{}".format(name))
        if res.status_code != 200:
            raise ArangoCollectionDeleteError(res)
        self._update_collection_cache()
        return True

    def rename_collection(self, name, new_name):
        """Rename the specified collection in this database.

        :param name: the name of the collection to rename
        :type name: str
        :param new_name: the new name for the collection
        :type new_name: str
        :returns: True
        :rtype: boolean
        :raises: ArangoCollectionRenameError
        """
        res = self._client.put(
            "/_api/collection/{}/rename".format(name),
            data={"name": new_name}
        )
        if res.status_code != 200:
            raise ArangoCollectionRenameError(res)
        self._update_collection_cache()
        return True

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

    def create_aql_function(self, name, code, **kwargs):
        """Create a new AQL function.

        :param name: the name of the new AQL function to create
        :type name: str
        :param code: the stringified javascript code of the new function
        :type code: str
        :param kwargs: optional parameters
        :returns: True
        :rtype: boolean
        :raises: ArangoAQLFunctionCreateError
        """
        data = {"name": name, "code": code}
        data.update(kwargs)
        res = self._client.post("/_api/aqlfunction", data=data)
        if res.status_code not in (200, 201):
            raise ArangoAQLFunctionCreateError(res)
        return True

    def delete_aql_function(self, name, **kwargs):
        """Delete an AQL function.

        :param name: the name of the AQL function to delete
        :type name: str
        :param kwargs: optional parameters
        :returns: True
        :rtype: boolean
        :raises: ArangoAQLFunctionDeleteError
        """
        res = self._client.delete(
            "/_api/aqlfunction/{}".format(name), data=kwargs
        )
        if res.status_code != 200:
            raise ArangoAQLFunctionDeleteError(res)
        return True

    ###############
    # AQL Queries #
    ###############

    def parse_query(self, query):
        """Validate the AQL query.

        :param query: the AQL query to validate
        :type query: str
        :returns: True
        :rtype: boolean
        :raises: ArangoQueryParseError
        """
        self._query.parse(query)
        return True

    def execute_query(self, query, **kwargs):
        """Execute the AQL query and return the result.

        :param query: the AQL query to execute
        :type query: str
        :param kwargs: optional parameters
        :returns: the result from executing the query
        :rtype: types.GeneratorType
        :raises: ArangoQueryExecuteError, ArangoCursorDeleteError
        """
        return self._query.execute(query, **kwargs)

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
        :raises: ArangoTransactionError
        """
        data = {
            collections: {} if collections is None else collections,
            action: "" if action is None else ""
        }
        res = self._client.post("/_api/transaction", data=data)
        if res != 200:
            raise ArangoTransactionError(res)
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

    def create_graph(self, name, edge_definitions=None,
                     orphan_collections=None):
        """Create a new graph in this database.

        # TODO expand on edge_definitions and orphan_collections

        :param name: name of the new graph
        :type name: str
        :param edge_definitions: definitions for edges
        :type edge_definitions: list
        :param orphan_collections: names of additional vertex collections
        :type orphan_collections: list
        :returns: the details on the created graph
        :rtype: dict
        :raises: ArangoGraphCreateError
        """
        data = {"name": name}
        if edge_definitions is not None:
            data["edgeDefinitions"] = edge_definitions
        if orphan_collections is not None:
            data["orphanCollections"] = orphan_collections

        res = self._client.post("/_api/gharial", data=data)
        if res.status_code != 201:
            raise ArangoGraphCreateError(res)
        self._update_graph_cache()
        return res.obj["graph"]

    def delete_graph(self, name):
        """Delete the graph of the given name.

        :param name: the name of the graph to delete
        :type name: str
        :returns: True
        :rtype: boolean
        :raises: ArangoGraphDeleteError
        """
        res = self._client.delete("/_api/gharial/{}".format(name))
        if res.status_code != 200:
            raise ArangoGraphDeleteError(res)
        self._update_graph_cache()
        return True