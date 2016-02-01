"""ArangoDB Database."""

from arango.utils import uncamelify
from arango.graph import Graph
from arango.collection import Collection
from arango.cursor import cursor
from arango.constants import HTTP_OK
from arango.exceptions import *


class Database(object):
    """Wrapper for ArangoDB's database-specific APIs:

    1. Database properties
    1. Collection Management
    2. AQL Queries
    3. Batch Requests
    4. AQL Functions
    5. Transaction
    6. Graph Management
    """

    def __init__(self, connection, name):
        """Initialize the wrapper object.

        :param connection: ArangoDB API connection object
        :type connection: arango.connection.Connection
        :param name: the name of this database
        :type name: str
        """
        self._conn = connection
        self._name = name

    def __repr__(self):
        """Return a descriptive string of this instance."""
        return "<ArangoDB database '{}'>".format(self._name)

    def properties(self):
        """Return all properties of this database.

        :returns: the database properties
        :rtype: dict
        :raises: DatabasePropertyError
        """
        res = self._conn.get('/_api/database/current')
        if res.status_code not in HTTP_OK:
            raise DatabasePropertyError(res)
        return uncamelify(res.body['result'])

    ###############
    # AQL Queries #
    ###############

    def explain_query(self, query, all_plans=False, max_plans=None,
                      optimizer_rules=None):
        """Explain the AQL query.

        This method does not execute the query, but only inspect it and
        return meta information about it.

        If ``all_plans`` is set to True, all possible execution plans are
        returned. Otherwise only the optimal plan is returned.

        For more information on optimizer_rules, please refer to:
        https://docs.arangodb.com/HttpAqlQuery/README.html

        :param query: the AQL query to explain
        :type query: str
        :param all_plans: whether or not to return all execution plans
        :type all_plans: bool
        :param max_plans: maximum number of plans the optimizer generates
        :type max_plans: None or int
        :param optimizer_rules: list of optimizer rules
        :type optimizer_rules: list
        :returns: the query plan or list of plans (if all_plans is True)
        :rtype: dict or list
        :raises: AQLQueryExplainError
        """
        options = {'allPlans': all_plans}
        if max_plans is not None:
            options['maxNumberOfPlans'] = max_plans
        if optimizer_rules is not None:
            options['optimizer'] = {'rules': optimizer_rules}
        res = self._conn.post(
            '/_api/explain', data={'query': query, 'options': options}
        )
        if res.status_code not in HTTP_OK:
            raise AQLQueryExplainError(res)
        if 'plan' in res.body:
            return uncamelify(res.body['plan'])
        else:
            return uncamelify(res.body['plans'])

    def validate_query(self, query):
        """Validate the AQL query.

        :param query: the AQL query to validate
        :type query: str
        :raises: AQLQueryValidateError
        """
        res = self._conn.post('/_api/query', data={'query': query})
        if res.status_code not in HTTP_OK:
            raise AQLQueryValidateError(res)

    def execute_query(self, query, count=False, batch_size=None, ttl=None,
                      bind_vars=None, full_count=None, max_plans=None,
                      optimizer_rules=None):
        """Execute the AQL query and return the result.

        For more information on ``full_count`` please refer to:
        https://docs.arangodb.com/HttpAqlQueryCursor/AccessingCursors.html

        :param query: the AQL query to execute
        :type query: str
        :param count: whether or not the document count should be returned
        :type count: bool
        :param batch_size: maximum number of documents in one round trip
        :type batch_size: int
        :param ttl: time-to-live for the cursor (in seconds)
        :type ttl: int
        :param bind_vars: key-value pairs of bind parameters
        :type bind_vars: dict
        :param full_count: whether or not to include count before last LIMIT
        :param max_plans: maximum number of plans the optimizer generates
        :type max_plans: None or int
        :param optimizer_rules: list of optimizer rules
        :type optimizer_rules: list
        :returns: the cursor from executing the query
        :raises: AQLQueryExecuteError, CursorDeleteError
        """
        options = {}
        if full_count is not None:
            options['fullCount'] = full_count
        if max_plans is not None:
            options['maxNumberOfPlans'] = max_plans
        if optimizer_rules is not None:
            options['optimizer'] = {'rules': optimizer_rules}

        data = {'query': query, 'count': count}
        if batch_size is not None:
            data['batchSize'] = batch_size
        if ttl is not None:
            data['ttl'] = ttl
        if bind_vars is not None:
            data['bindVars'] = bind_vars
        if options:
            data['options'] = options

        res = self._conn.post('/_api/cursor', data=data)
        if res.status_code not in HTTP_OK:
            raise AQLQueryExecuteError(res)
        return cursor(self._conn, res)

    #########################
    # Collection Management #
    #########################

    def list_collections(self, user_only=False):
        """Return the names of the collections in this database.

        :param user_only: return only the user collection names
        :type user_only: bool
        :returns: the names of the collections
        :rtype: dict
        :raises: CollectionListError
        """
        res = self._conn.get('/_api/collection')
        if res.status_code not in HTTP_OK:
            raise CollectionListError(res)
        return [
            collection['name'] for collection in res.body['collections']
            if not (user_only and collection['isSystem'])
        ]

    def col(self, name):
        """Return the Collection object of the specified name.

        :param name: the name of the collection
        :type name: str
        :returns: the requested collection object
        :rtype: arango.collection.Collection
        :raises: TypeError, CollectionNotFound
        """
        return self.collection(name)

    def collection(self, name):
        """Return the Collection object of the specified name.

        :param name: the name of the collection
        :type name: str
        :returns: the requested collection object
        :rtype: arango.collection.Collection
        :raises: TypeError
        """
        return Collection(self._conn, name)

    def create_collection(self, name, wait_for_sync=False, do_compact=True,
                          journal_size=None, is_system=False, is_edge=False,
                          is_volatile=False, key_generator_type="traditional",
                          shard_keys=None, allow_user_keys=True,
                          key_offset=None, key_increment=None,
                          number_of_shards=None):
        """Create a new collection to this database.

        :param name: name of the new collection
        :type name: str
        :param wait_for_sync: whether or not to wait for sync to disk
        :type wait_for_sync: bool
        :param do_compact: whether or not the collection is compacted
        :type do_compact: bool
        :param journal_size: the max size of the journal or datafile
        :type journal_size: int
        :param is_system: whether or not the collection is a system collection
        :type is_system: bool
        :param is_volatile: whether or not the collection is in-memory only
        :type is_volatile: bool
        :param key_generator_type: ``traditional`` or ``autoincrement``
        :type key_generator_type: str
        :param allow_user_keys: whether or not to allow users to supply keys
        :type allow_user_keys: bool
        :param key_increment: increment value for ``autoincrement`` generator
        :type key_increment: int
        :param key_offset: initial offset value for ``autoincrement`` generator
        :type key_offset: int
        :param is_edge: whether or not the collection is an edge collection
        :type is_edge: bool
        :param number_of_shards: the number of shards to create
        :type number_of_shards: int
        :param shard_keys: the attribute(s) used to determine the target shard
        :type shard_keys: list
        :raises: CollectionCreateError
        """
        key_options = {
            'type': key_generator_type,
            'allowUserKeys': allow_user_keys
        }
        if key_increment is not None:
            key_options['increment'] = key_increment
        if key_offset is not None:
            key_options['offset'] = key_offset
        data = {
            'name': name,
            'waitForSync': wait_for_sync,
            'doCompact': do_compact,
            'isSystem': is_system,
            'isVolatile': is_volatile,
            'type': 3 if is_edge else 2,
            'keyOptions': key_options
        }
        if journal_size is not None:
            data['journalSize'] = journal_size
        if number_of_shards is not None:
            data['numberOfShards'] = number_of_shards
        if shard_keys is not None:
            data['shardKeys'] = shard_keys

        res = self._conn.post('/_api/collection', data=data)
        if res.status_code not in HTTP_OK:
            raise CollectionCreateError(res)
        return self.collection(name)

    def delete_collection(self, name):
        """Delete the specified collection from this database.

        :param name: the name of the collection to delete
        :type name: str
        :raises: CollectionDeleteError
        """
        res = self._conn.delete('/_api/collection/{}'.format(name))
        if res.status_code not in HTTP_OK:
            raise CollectionDeleteError(res)

    def rename_collection(self, name, new_name):
        """Rename the specified collection in this database.

        :param name: the name of the collection to rename
        :type name: str
        :param new_name: the new name for the collection
        :type new_name: str
        :raises: CollectionRenameError
        """
        res = self._conn.put(
            '/_api/collection/{}/rename'.format(name),
            data={'name': new_name}
        )
        if res.status_code not in HTTP_OK:
            raise CollectionRenameError(res)

    def load_collection(self, name):
        """Load the specified collection into memory.

        :param name: the name of the collection
        :type name: str
        :returns: the status of the collection
        :rtype: str
        :raises: CollectionLoadError
        """
        self.collection(name).load()

    def unload_collection(self, name):
        """Unload the specified collection from memory.

        :param name: the name of the collection
        :type name: str
        :returns: the status of the collection
        :rtype: str
        :raises: CollectionUnloadError
        """
        self.collection(name).unload()

    def truncate_collection(self, name):
        """Delete all documents from the specified collection.

        :param name: the name of the collection
        :type name: str
        :raises: CollectionTruncateError
        """
        self.collection(name).truncate()

    ##################
    # Batch Requests #
    ##################

    def execute_batch(self, batch_steps):
        """Execute ArangoDB API calls in a batch.

        :param batch_steps: ArangoDB requests
        :type batch_steps: list
        :raises: BatchInvalidError, BatchExecuteError
        """
        pass

    #################
    # AQL Functions #
    #################

    @property
    def aql_functions(self):
        """List the AQL functions defined in this database.

        :returns: a mapping of AQL function names to its javascript code
        :rtype: dict
        :raises: AQLFunctionListError
        """
        res = self._conn.get('/_api/aqlfunction')
        if res.status_code not in HTTP_OK:
            raise AQLFunctionListError(res)
        return {func['name']: func['code']for func in res.body}

    def create_aql_function(self, name, code):
        """Create a new AQL function.

        :param name: the name of the new AQL function to create
        :type name: str
        :param code: the stringified javascript code of the new function
        :type code: str
        :returns: the updated AQL functions
        :rtype: dict
        :raises: AQLFunctionCreateError
        """
        data = {'name': name, 'code': code}
        res = self._conn.post('/_api/aqlfunction', data=data)
        if res.status_code not in (200, 201):
            raise AQLFunctionCreateError(res)
        return self.aql_functions

    def delete_aql_function(self, name, group=None):
        """Delete the AQL function of the given name.

        If ``group`` is set to True, then the function name provided in
        ``name`` is treated as a namespace prefix, and all functions in
        the specified namespace will be deleted. If set to False, the
        function name provided in ``name`` must be fully qualified,
        including any namespaces.

        :param name: the name of the AQL function to delete
        :type name: str
        :param group: whether or not to treat name as a namespace prefix
        :returns: the updated AQL functions
        :rtype: dict
        :raises: AQLFunctionDeleteError
        """
        res = self._conn.delete(
            '/_api/aqlfunction/{}'.format(name),
            params={'group': group} if group is not None else {}
        )
        if res.status_code not in HTTP_OK:
            raise AQLFunctionDeleteError(res)
        return self.aql_functions

    ################
    # Transactions #
    ################

    def execute_transaction(self, action, read_collections=None,
                            write_collections=None, params=None,
                            wait_for_sync=False, lock_timeout=None):
        """Execute the transaction and return the result.

        Setting the ``lock_timeout`` to 0 will make ArangoDB not time out
        waiting for a lock.

        :param action: the javascript commands to be executed
        :type action: str
        :param read_collections: the collections read
        :type read_collections: str or list or None
        :param write_collections: the collections written to
        :type write_collections: str or list or None
        :param params: Parameters for the function in action
        :type params: list or dict or None
        :param wait_for_sync: wait for the transaction to sync to disk
        :type wait_for_sync: bool
        :param lock_timeout: timeout for waiting on collection locks
        :type lock_timeout: int or None
        :returns: the results of the execution
        :rtype: dict
        :raises: TransactionExecuteError
        """
        path = '/_api/transaction'
        data = {'collections': {}, 'action': action}
        if read_collections is not None:
            data['collections']['read'] = read_collections
        if write_collections is not None:
            data['collections']['write'] = write_collections
        if params is not None:
            data['params'] = params
        http_params = {
            'waitForSync': wait_for_sync,
            'lockTimeout': lock_timeout,
        }
        res = self._conn.post(endpoint=path, data=data, params=http_params)
        if res.status_code not in HTTP_OK:
            raise TransactionExecuteError(res)
        return res.body['result']

    ####################
    # Graph Management #
    ####################

    def list_graphs(self):
        """List all graphs in this database.

        :returns: the graphs in this database
        :rtype: dict
        :raises: GraphGetError
        """
        res = self._conn.get('/_api/gharial')
        if res.status_code not in HTTP_OK:
            raise GraphListError(res)
        return [graph['_key'] for graph in res.body['graphs']]

    def graph(self, name):
        """Return the Graph object of the specified name.

        :param name: the name of the graph
        :type name: str
        :returns: the requested graph object
        :rtype: arango.graph.Graph
        :raises: TypeError, GraphNotFound
        """
        return Graph(self._conn, name)

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
        :returns: the graph object
        :rtype: arango.graph.Graph
        :raises: GraphCreateError
        """
        data = {'name': name}
        if edge_definitions is not None:
            data['edgeDefinitions'] = edge_definitions
        if orphan_collections is not None:
            data['orphanCollections'] = orphan_collections

        res = self._conn.post('/_api/gharial', data=data)
        if res.status_code not in HTTP_OK:
            raise GraphCreateError(res)
        return self.graph(name)

    def delete_graph(self, name):
        """Delete the graph of the given name from this database.

        :param name: the name of the graph to delete
        :type name: str
        :raises: GraphDeleteError
        """
        res = self._conn.delete('/_api/gharial/{}'.format(name))
        if res.status_code not in HTTP_OK:
            raise GraphDeleteError(res)
