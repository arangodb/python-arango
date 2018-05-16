from __future__ import absolute_import, unicode_literals

from arango.utils import get_col_name

__all__ = [
    'StandardDatabase',
    'AsyncDatabase',
    'BatchDatabase',
    'TransactionDatabase'
]

from datetime import datetime

from arango.api import APIWrapper
from arango.aql import AQL
from arango.executor import (
    DefaultExecutor,
    AsyncExecutor,
    BatchExecutor,
    TransactionExecutor,
)
from arango.collection import StandardCollection
from arango.exceptions import (
    AsyncJobClearError,
    AsyncJobListError,
    CollectionCreateError,
    CollectionDeleteError,
    CollectionListError,
    DatabaseDeleteError,
    DatabaseCreateError,
    DatabaseListError,
    DatabasePropertiesError,
    GraphListError,
    GraphCreateError,
    GraphDeleteError,
    PermissionListError,
    PermissionGetError,
    PermissionResetError,
    PermissionUpdateError,
    ServerConnectionError,
    ServerEndpointsError,
    ServerEngineError,
    ServerDetailsError,
    ServerEchoError,
    ServerLogLevelError,
    ServerLogLevelSetError,
    ServerReadLogError,
    ServerReloadRoutingError,
    ServerRequiredDBVersionError,
    ServerRoleError,
    ServerRunTestsError,
    ServerShutdownError,
    ServerStatisticsError,
    ServerTimeError,
    ServerVersionError,
    TaskCreateError,
    TaskDeleteError,
    TaskGetError,
    TaskListError,
    TransactionExecuteError,
    UserCreateError,
    UserDeleteError,
    UserGetError,
    UserListError,
    UserReplaceError,
    UserUpdateError,
)
from arango.foxx import Foxx
from arango.graph import Graph
from arango.pregel import Pregel
from arango.request import Request
from arango.wal import WAL


class Database(APIWrapper):
    """Base class for Database API wrappers.

    :param connection: HTTP connection.
    :type connection: arango.connection.Connection
    :param executor: API executor.
    :type executor: arango.executor.Executor
    """

    def __init__(self, connection, executor):
        super(Database, self).__init__(connection, executor)

    def __getitem__(self, name):
        """Return the collection API wrapper.

        :param name: Collection name.
        :type name: str | unicode
        :return: Collection API wrapper.
        :rtype: arango.collection.StandardCollection
        """
        return self.collection(name)

    def _get_col_by_doc(self, document):
        """Return the collection of the given document.

        :param document: Document ID or body with "_id" field.
        :type document: str | unicode | dict
        :return: Collection API wrapper.
        :rtype: arango.collection.StandardCollection
        :raise arango.exceptions.DocumentParseError: On malformed document.
        """
        return self.collection(get_col_name(document))

    @property
    def name(self):
        """Return database name.

        :return: Database name.
        :rtype: str | unicode
        """
        return self.db_name

    @property
    def aql(self):
        """Return AQL (ArangoDB Query Language) API wrapper.

        :return: AQL API wrapper.
        :rtype: arango.aql.AQL
        """
        return AQL(self._conn, self._executor)

    @property
    def wal(self):
        """Return WAL (Write-Ahead Log) API wrapper.

        :return: WAL API wrapper.
        :rtype: arango.wal.WAL
        """
        return WAL(self._conn, self._executor)

    @property
    def foxx(self):
        """Return Foxx API wrapper.

        :return: Foxx API wrapper.
        :rtype: arango.foxx.Foxx
        """
        return Foxx(self._conn, self._executor)

    @property
    def pregel(self):
        """Return Pregel API wrapper.

        :return: Pregel API wrapper.
        :rtype: arango.pregel.Pregel
        """
        return Pregel(self._conn, self._executor)

    def properties(self):
        """Return database properties.

        :return: Database properties.
        :rtype: dict
        :raise arango.exceptions.DatabasePropertiesError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_api/database/current',
        )

        def response_handler(resp):
            if not resp.is_success:
                raise DatabasePropertiesError(resp, request)
            result = resp.body['result']
            result['system'] = result.pop('isSystem')
            return result

        return self._execute(request, response_handler)

    def execute_transaction(self,
                            command,
                            params=None,
                            read=None,
                            write=None,
                            sync=None,
                            timeout=None,
                            max_size=None,
                            allow_implicit=None,
                            intermediate_commit_count=None,
                            intermediate_commit_size=None):
        """Execute raw Javascript command in transaction.

        :param command: Javascript command to execute.
        :type command: str | unicode
        :param read: Names of collections read during transaction. If parameter
            **allow_implicit** is set to True, any undeclared read collections
            are loaded lazily.
        :type read: [str | unicode]
        :param write: Names of collections written to during transaction.
            Transaction fails on undeclared write collections.
        :type write: [str | unicode]
        :param params: Optional parameters passed into the Javascript command.
        :type params: dict
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool
        :param timeout: Timeout for waiting on collection locks. If set to 0,
            ArangoDB server waits indefinitely. If not set, system default
            value is used.
        :type timeout: int
        :param max_size: Max transaction size limit in bytes. Applies only
            to RocksDB storage engine.
        :type max_size: int
        :param allow_implicit: If set to True, undeclared read collections are
            loaded lazily. If set to False, transaction fails on any undeclared
            collections.
        :type allow_implicit: bool
        :param intermediate_commit_count: Max number of operations after which
            an intermediate commit is performed automatically. Applies only to
            RocksDB storage engine.
        :type intermediate_commit_count: int
        :param intermediate_commit_size: Max size of operations in bytes after
            which an intermediate commit is performed automatically. Applies
            only to RocksDB storage engine.
        :type intermediate_commit_size: int
        :return: Return value of **command**.
        :rtype: str | unicode
        :raise arango.exceptions.TransactionExecuteError: If execution fails.
        """
        collections = {'allowImplicit': allow_implicit}
        if read is not None:
            collections['read'] = read
        if write is not None:
            collections['write'] = write

        data = {'action': command}
        if collections:
            data['collections'] = collections
        if params is not None:
            data['params'] = params
        if timeout is not None:
            data['lockTimeout'] = timeout
        if sync is not None:
            data['waitForSync'] = sync
        if max_size is not None:
            data['maxTransactionSize'] = max_size
        if intermediate_commit_count is not None:
            data['intermediateCommitCount'] = intermediate_commit_count
        if intermediate_commit_size is not None:
            data['intermediateCommitSize'] = intermediate_commit_size

        request = Request(
            method='post',
            endpoint='/_api/transaction',
            data=data
        )

        def response_handler(resp):
            if not resp.is_success:
                raise TransactionExecuteError(resp, request)
            return resp.body.get('result')

        return self._execute(request, response_handler)

    def version(self):
        """Return ArangoDB server version.

        :return: Server version.
        :rtype: str | unicode
        :raise arango.exceptions.ServerVersionError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_api/version',
            params={'details': False}
        )

        def response_handler(resp):
            if not resp.is_success:
                raise ServerVersionError(resp, request)
            return resp.body['version']

        return self._execute(request, response_handler)

    def details(self):
        """Return ArangoDB server details.

        :return: Server details.
        :rtype: dict
        :raise arango.exceptions.ServerDetailsError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_api/version',
            params={'details': True}
        )

        def response_handler(resp):
            if not resp.is_success:
                raise ServerDetailsError(resp, request)
            return resp.body['details']

        return self._execute(request, response_handler)

    def required_db_version(self):
        """Return required version of target database.

        :return: Required version of target database.
        :rtype: str | unicode
        :raise arango.exceptions.ServerRequiredDBVersionError: If retrieval
            fails.
        """
        request = Request(
            method='get',
            endpoint='/_admin/database/target-version'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise ServerRequiredDBVersionError(resp, request)
            return resp.body['version']

        return self._execute(request, response_handler)

    def endpoints(self):  # pragma: no cover
        """Return coordinate endpoints. This method is for clusters only.

        :return: List of endpoints.
        :rtype: [str | unicode]
        :raise arango.exceptions.ServerEndpointsError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_api/cluster/endpoints'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise ServerEndpointsError(resp, request)
            return [item['endpoint'] for item in resp.body['endpoints']]

        return self._execute(request, response_handler)

    def engine(self):
        """Return the database engine details.

        :return: Database engine details.
        :rtype: str | unicode
        :raise arango.exceptions.ServerEngineError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_api/engine',
            command='db._engine()'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise ServerEngineError(resp, request)
            return resp.body

        return self._execute(request, response_handler)

    def ping(self):
        """Ping the ArangoDB server by sending a test request.

        :return: Response code from server.
        :rtype: int
        :raise arango.exceptions.ServerConnectionError: If ping fails.
        """
        request = Request(
            method='get',
            endpoint='/_api/collection',
        )

        def response_handler(resp):
            code = resp.status_code
            if code in {401, 403}:
                raise ServerConnectionError('bad username and/or password')
            if not resp.is_success:
                raise ServerConnectionError(
                    resp.error_message or 'bad server response')
            return code

        return self._execute(request, response_handler)

    def statistics(self, description=False):
        """Return server statistics.

        :return: Server statistics.
        :rtype: dict
        :raise arango.exceptions.ServerStatisticsError: If retrieval fails.
        """
        if description:
            url = '/_admin/statistics-description'
        else:
            url = '/_admin/statistics'

        request = Request(
            method='get',
            endpoint=url
        )

        def response_handler(resp):
            if not resp.is_success:
                raise ServerStatisticsError(resp, request)
            resp.body.pop('code')
            resp.body.pop('error')
            return resp.body

        return self._execute(request, response_handler)

    def role(self):
        """Return server role in cluster.

        :return: Server role. Possible values are "SINGLE" (server which is not
            in a cluster), "COORDINATOR" (cluster coordinator), "PRIMARY",
            "SECONDARY" or "UNDEFINED".
        :rtype: str | unicode
        :raise arango.exceptions.ServerRoleError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_admin/server/role'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise ServerRoleError(resp, request)
            return resp.body.get('role')

        return self._execute(request, response_handler)

    def time(self):
        """Return server system time.

        :return: Server system time.
        :rtype: datetime.datetime
        :raise arango.exceptions.ServerTimeError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_admin/time'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise ServerTimeError(resp, request)
            return datetime.fromtimestamp(resp.body['time'])

        return self._execute(request, response_handler)

    def echo(self):
        """Return details of the last request (e.g. headers, payload).

        :return: Details of the last request.
        :rtype: dict
        :raise arango.exceptions.ServerEchoError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_admin/echo'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise ServerEchoError(resp, request)
            return resp.body

        return self._execute(request, response_handler)

    def shutdown(self):  # pragma: no cover
        """Initiate server shutdown sequence.

        :return: True if the server was shutdown successfully.
        :rtype: bool
        :raise arango.exceptions.ServerShutdownError: If shutdown fails.
        """
        request = Request(
            method='delete',
            endpoint='/_admin/shutdown'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise ServerShutdownError(resp, request)
            return True

        return self._execute(request, response_handler)

    def run_tests(self, tests):  # pragma: no cover
        """Run available unittests on the server.

        :param tests: List of files containing the test suites.
        :type tests: [str | unicode]
        :return: Test results.
        :rtype: dict
        :raise arango.exceptions.ServerRunTestsError: If execution fails.
        """
        request = Request(
            method='post',
            endpoint='/_admin/test',
            data={'tests': tests}
        )

        def response_handler(resp):
            if not resp.is_success:
                raise ServerRunTestsError(resp, request)
            return resp.body

        return self._execute(request, response_handler)

    def read_log(self,
                 upto=None,
                 level=None,
                 start=None,
                 size=None,
                 offset=None,
                 search=None,
                 sort=None):
        """Read the global log from server.

        :param upto: Return the log entries up to the given level (mutually
            exclusive with parameter **level**). Allowed values are "fatal",
            "error", "warning", "info" (default) and "debug".
        :type upto: str | unicode | int
        :param level: Return the log entries of only the given level (mutually
            exclusive with **upto**). Allowed values are "fatal", "error",
            "warning", "info" (default) and "debug".
        :type level: str | unicode | int
        :param start: Return the log entries whose ID is greater or equal to
            the given value.
        :type start: int
        :param size: Restrict the size of the result to the given value. This
            can be used for pagination.
        :type size: int
        :param offset: Number of entries to skip (e.g. for pagination).
        :type offset: int
        :param search: Return only the log entries containing the given text.
        :type search: str | unicode
        :param sort: Sort the log entries according to the given fashion, which
            can be "sort" or "desc".
        :type sort: str | unicode
        :return: Server log entries.
        :rtype: dict
        :raise arango.exceptions.ServerReadLogError: If read fails.
        """
        params = dict()
        if upto is not None:
            params['upto'] = upto
        if level is not None:
            params['level'] = level
        if start is not None:
            params['start'] = start
        if size is not None:
            params['size'] = size
        if offset is not None:
            params['offset'] = offset
        if search is not None:
            params['search'] = search
        if sort is not None:
            params['sort'] = sort

        request = Request(
            method='get',
            endpoint='/_admin/log',
            params=params
        )

        def response_handler(resp):
            if not resp.is_success:
                raise ServerReadLogError(resp, request)
            if 'totalAmount' in resp.body:
                resp.body['total_amount'] = resp.body.pop('totalAmount')
            return resp.body

        return self._execute(request, response_handler)

    def log_levels(self):
        """Return current logging levels.

        :return: Current logging levels.
        :rtype: dict
        """
        request = Request(
            method='get',
            endpoint='/_admin/log/level'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise ServerLogLevelError(resp, request)
            return resp.body

        return self._execute(request, response_handler)

    def set_log_levels(self, **kwargs):
        """Set the logging levels.

        This method takes arbitrary keyword arguments where the keys are the
        logger names and the values are the logging levels. For example:

        .. code-block:: python

            arango.set_log_levels(
                agency='DEBUG',
                collector='INFO',
                threads='WARNING'
            )

        Keys that are not valid logger names are ignored.

        :return: New logging levels.
        :rtype: dict
        """
        request = Request(
            method='put',
            endpoint='/_admin/log/level',
            data=kwargs
        )

        def response_handler(resp):
            if not resp.is_success:
                raise ServerLogLevelSetError(resp, request)
            return resp.body

        return self._execute(request, response_handler)

    def reload_routing(self):
        """Reload the routing information.

        :return: True if routing was reloaded successfully.
        :rtype: bool
        :raise arango.exceptions.ServerReloadRoutingError: If reload fails.
        """
        request = Request(
            method='post',
            endpoint='/_admin/routing/reload'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise ServerReloadRoutingError(resp, request)
            return 'error' not in resp.body

        return self._execute(request, response_handler)

    #######################
    # Database Management #
    #######################

    def databases(self):
        """Return the names all databases.

        :return: Database names.
        :rtype: [str | unicode]
        :raise arango.exceptions.DatabaseListError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_api/database'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise DatabaseListError(resp, request)
            return resp.body['result']

        return self._execute(request, response_handler)

    def has_database(self, name):
        """Check if a database exists.

        :param name: Database name.
        :type name: str | unicode
        :return: True if database exists, False otherwise.
        :rtype: bool
        """
        return name in self.databases()

    def create_database(self, name, users=None):
        """Create a new database.

        :param name: Database name.
        :type name: str | unicode
        :param users: List of users with access to the new database, where each
            user is a dictionary with fields "username", "password", "active"
            and "extra" (see below for example). If not set, only the admin and
            current user are granted access.
        :type users: [dict]
        :return: True if database was created successfully.
        :rtype: bool
        :raise arango.exceptions.DatabaseCreateError: If create fails.

        Here is an example entry for parameter **users**:

        .. code-block:: python

            {
                'username': 'john',
                'password': 'password',
                'active': True,
                'extra': {'Department': 'IT'}
            }
        """
        data = {'name': name}
        if users is not None:
            data['users'] = [{
                'username': user['username'],
                'passwd': user['password'],
                'active': user.get('active', True),
                'extra': user.get('extra', {})
            } for user in users]

        request = Request(
            method='post',
            endpoint='/_api/database',
            data=data
        )

        def response_handler(resp):
            if not resp.is_success:
                raise DatabaseCreateError(resp, request)
            return True

        return self._execute(request, response_handler)

    def delete_database(self, name, ignore_missing=False):
        """Delete the database.

        :param name: Database name.
        :type name: str | unicode
        :param ignore_missing: Do not raise an exception on missing database.
        :type ignore_missing: bool
        :return: True if database was deleted successfully, False if database
            was not found and **ignore_missing** was set to True.
        :rtype: bool
        :raise arango.exceptions.DatabaseDeleteError: If delete fails.
        """
        request = Request(
            method='delete',
            endpoint='/_api/database/{}'.format(name)
        )

        def response_handler(resp):
            if resp.error_code == 1228 and ignore_missing:
                return False
            if not resp.is_success:
                raise DatabaseDeleteError(resp, request)
            return resp.body['result']

        return self._execute(request, response_handler)

    #########################
    # Collection Management #
    #########################

    def collection(self, name):
        """Return the standard collection API wrapper.

        :param name: Collection name.
        :type name: str | unicode
        :return: Standard collection API wrapper.
        :rtype: arango.collection.StandardCollection
        """
        return StandardCollection(self._conn, self._executor, name)

    def has_collection(self, name):
        """Check if collection exists in the database.

        :param name: Collection name.
        :type name: str | unicode
        :return: True if collection exists, False otherwise.
        :rtype: bool
        """
        return any(col['name'] == name for col in self.collections())

    def collections(self):
        """Return the collections in the database.

        :return: Collections in the database and their details.
        :rtype: [dict]
        :raise arango.exceptions.CollectionListError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_api/collection'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise CollectionListError(resp, request)
            return [{
                'id': col['id'],
                'name': col['name'],
                'system': col['isSystem'],
                'type': StandardCollection.types[col['type']],
                'status': StandardCollection.statuses[col['status']],
            } for col in map(dict, resp.body['result'])]

        return self._execute(request, response_handler)

    def create_collection(self,
                          name,
                          sync=False,
                          compact=True,
                          system=False,
                          journal_size=None,
                          edge=False,
                          volatile=False,
                          user_keys=True,
                          key_increment=None,
                          key_offset=None,
                          key_generator='traditional',
                          shard_fields=None,
                          shard_count=None,
                          index_bucket_count=None,
                          replication_factor=None,
                          shard_like=None,
                          sync_replication=None,
                          enforce_replication_factor=None):
        """Create a new collection.

        :param name: Collection name.
        :type name: str | unicode
        :param sync: If set to True, document operations via the collection
            will block until synchronized to disk by default.
        :type sync: bool
        :param compact: If set to True, the collection is compacted. Applies
            only to MMFiles storage engine.
        :type compact: bool
        :param system: If set to True, a system collection is created. The
            collection name must have leading underscore "_" character.
        :type system: bool
        :param journal_size: Max size of the journal in bytes.
        :type journal_size: int
        :param edge: If set to True, an edge collection is created.
        :type edge: bool
        :param volatile: If set to True, collection data is kept in-memory only
            and not made persistent. Unloading the collection will cause the
            collection data to be discarded. Stopping or re-starting the server
            will also cause full loss of data.
        :type volatile: bool
        :param key_generator: Used for generating document keys. Allowed values
            are "traditional" or "autoincrement".
        :type key_generator: str | unicode
        :param user_keys: If set to True, users are allowed to supply document
            keys. If set to False, the key generator is solely responsible for
            supplying the key values.
        :type user_keys: bool
        :param key_increment: Key increment value. Applies only when value of
            **key_generator** is set to "autoincrement".
        :type key_increment: int
        :param key_offset: Key offset value. Applies only when value of
            **key_generator** is set to "autoincrement".
        :type key_offset: int
        :param shard_fields: Field(s) used to determine the target shard.
        :type shard_fields: [str | unicode]
        :param shard_count: Number of shards to create.
        :type shard_count: int
        :param index_bucket_count: Number of buckets into which indexes using
            hash tables are split. The default is 16, and this number has to be
            a power of 2 and less than or equal to 1024. For large collections,
            one should increase this to avoid long pauses when the hash table
            has to be initially built or re-sized, since buckets are re-sized
            individually and can be initially built in parallel. For instance,
            64 may be a sensible value for 100 million documents.
        :type index_bucket_count: int
        :param replication_factor: Number of copies of each shard on different
            servers in a cluster. Allowed values are 1 (only one copy is kept
            and no synchronous replication), and n (n-1 replicas are kept and
            any two copies are replicated across servers synchronously, meaning
            every write to the master is copied to all slaves before operation
            is reported successful).
        :type replication_factor: int
        :param shard_like: Name of prototype collection whose sharding
            specifics are imitated. Prototype collections cannot be dropped
            before imitating collections. Applies to enterprise version of
            ArangoDB only.
        :type shard_like: str | unicode
        :param sync_replication: If set to True, server reports success only
            when collection is created in all replicas. You can set this to
            False for faster server response, and if full replication is not a
            concern.
        :type sync_replication: bool
        :param enforce_replication_factor: Check if there are enough replicas
            available at creation time, or halt the operation.
        :type enforce_replication_factor: bool
        :return: Standard collection API wrapper.
        :rtype: arango.collection.StandardCollection
        :raise arango.exceptions.CollectionCreateError: If create fails.
        """
        key_options = {'type': key_generator, 'allowUserKeys': user_keys}
        if key_increment is not None:
            key_options['increment'] = key_increment
        if key_offset is not None:
            key_options['offset'] = key_offset

        data = {
            'name': name,
            'waitForSync': sync,
            'doCompact': compact,
            'isSystem': system,
            'isVolatile': volatile,
            'keyOptions': key_options,
            'type': 3 if edge else 2
        }
        if journal_size is not None:
            data['journalSize'] = journal_size
        if shard_count is not None:
            data['numberOfShards'] = shard_count
        if shard_fields is not None:
            data['shardKeys'] = shard_fields
        if index_bucket_count is not None:
            data['indexBuckets'] = index_bucket_count
        if replication_factor is not None:
            data['replicationFactor'] = replication_factor
        if shard_like is not None:
            data['distributeShardsLike'] = shard_like

        params = {}
        if sync_replication is not None:
            params['waitForSyncReplication'] = sync_replication
        if enforce_replication_factor is not None:
            params['enforceReplicationFactor'] = enforce_replication_factor

        request = Request(
            method='post',
            endpoint='/_api/collection',
            params=params,
            data=data
        )

        def response_handler(resp):
            if resp.is_success:
                return self.collection(name)
            raise CollectionCreateError(resp, request)

        return self._execute(request, response_handler)

    def delete_collection(self, name, ignore_missing=False, system=None):
        """Delete the collection.

        :param name: Collection name.
        :type name: str | unicode
        :param ignore_missing: Do not raise an exception on missing collection.
        :type ignore_missing: bool
        :param system: Whether the collection is a system collection.
        :type system: bool
        :return: True if collection was deleted successfully, False if
            collection was not found and **ignore_missing** was set to True.
        :rtype: bool
        :raise arango.exceptions.CollectionDeleteError: If delete fails.
        """
        params = {}
        if system is not None:
            params['isSystem'] = system

        request = Request(
            method='delete',
            endpoint='/_api/collection/{}'.format(name),
            params=params
        )

        def response_handler(resp):
            if resp.error_code == 1203 and ignore_missing:
                return False
            if not resp.is_success:
                raise CollectionDeleteError(resp, request)
            return True

        return self._execute(request, response_handler)

    ####################
    # Graph Management #
    ####################

    def graph(self, name):
        """Return the graph API wrapper.

        :param name: Graph name.
        :type name: str | unicode
        :return: Graph API wrapper.
        :rtype: arango.graph.Graph
        """
        return Graph(self._conn, self._executor, name)

    def has_graph(self, name):
        """Check if a graph exists in the database.

        :param name: Graph name.
        :type name: str | unicode
        :return: True if graph exists, False otherwise.
        :rtype: bool
        """
        for graph in self.graphs():
            if graph['name'] == name:
                return True
        return False

    def graphs(self):
        """List all graphs in the database.

        :return: Graphs in the database.
        :rtype: [dict]
        :raise arango.exceptions.GraphListError: If retrieval fails.
        """
        request = Request(method='get', endpoint='/_api/gharial')

        def response_handler(resp):
            if not resp.is_success:
                raise GraphListError(resp, request)
            return [
                {
                    'id': body['_id'],
                    'name': body['_key'],
                    'revision': body['_rev'],
                    'orphan_collections': body['orphanCollections'],
                    'edge_definitions': [
                        {
                            'edge_collection': definition['collection'],
                            'from_vertex_collections': definition['from'],
                            'to_vertex_collections': definition['to'],
                        }
                        for definition in body['edgeDefinitions']
                    ],
                    'shard_count': body.get('numberOfShards'),
                    'replication_factor': body.get('replicationFactor')
                } for body in resp.body['graphs']
            ]

        return self._execute(request, response_handler)

    def create_graph(self,
                     name,
                     edge_definitions=None,
                     orphan_collections=None,
                     smart=None,
                     smart_field=None,
                     shard_count=None):
        """Create a new graph.

        :param name: Graph name.
        :type name: str | unicode
        :param edge_definitions: List of edge definitions, where each edge
            definition entry is a dictionary with fields "edge_collection",
            "from_vertex_collections" and "to_vertex_collections" (see below
            for example).
        :type edge_definitions: [dict]
        :param orphan_collections: Names of additional vertex collections that
            are not in edge definitions.
        :type orphan_collections: [str | unicode]
        :param smart: If set to True, sharding is enabled (see parameter
            **smart_field** below). Applies only to enterprise version of
            ArangoDB.
        :type smart: bool
        :param smart_field: Document field used to shard the vertices of the
            graph. To use this, parameter **smart** must be set to True and
            every vertex in the graph must have the smart field. Applies only
            to enterprise version of ArangoDB.
        :type smart_field: str | unicode
        :param shard_count: Number of shards used for every collection in the
            graph. To use this, parameter **smart** must be set to True and
            every vertex in the graph must have the smart field. This number
            cannot be modified later once set. Applies only to enterprise
            version of ArangoDB.
        :type shard_count: int
        :return: Graph API wrapper.
        :rtype: arango.graph.Graph
        :raise arango.exceptions.GraphCreateError: If create fails.

        Here is an example entry for parameter **edge_definitions**:

        .. code-block:: python

            {
                'edge_collection': 'teach',
                'from_vertex_collections': ['teachers'],
                'to_vertex_collections': ['lectures']
            }
        """
        data = {'name': name}
        if edge_definitions is not None:
            data['edgeDefinitions'] = [{
                'collection': definition['edge_collection'],
                'from': definition['from_vertex_collections'],
                'to': definition['to_vertex_collections']
            } for definition in edge_definitions]
        if orphan_collections is not None:
            data['orphanCollections'] = orphan_collections
        if smart is not None:  # pragma: no cover
            data['isSmart'] = smart
        if smart_field is not None:  # pragma: no cover
            data['smartGraphAttribute'] = smart_field
        if shard_count is not None:  # pragma: no cover
            data['numberOfShards'] = shard_count

        request = Request(
            method='post',
            endpoint='/_api/gharial',
            data=data
        )

        def response_handler(resp):
            if resp.is_success:
                return Graph(self._conn, self._executor, name)
            raise GraphCreateError(resp, request)

        return self._execute(request, response_handler)

    def delete_graph(self, name, ignore_missing=False, drop_collections=None):
        """Drop the graph of the given name from the database.

        :param name: Graph name.
        :type name: str | unicode
        :param ignore_missing: Do not raise an exception on missing graph.
        :type ignore_missing: bool
        :param drop_collections: Drop the collections of the graph also. This
            is only if they are not in use by other graphs.
        :type drop_collections: bool
        :return: True if graph was deleted successfully, False if graph was not
            found and **ignore_missing** was set to True.
        :rtype: bool
        :raise arango.exceptions.GraphDeleteError: If delete fails.
        """
        params = {}
        if drop_collections is not None:
            params['dropCollections'] = drop_collections

        request = Request(
            method='delete',
            endpoint='/_api/gharial/{}'.format(name),
            params=params
        )

        def response_handler(resp):
            if resp.error_code == 1924 and ignore_missing:
                return False
            if not resp.is_success:
                raise GraphDeleteError(resp, request)
            return True

        return self._execute(request, response_handler)

    #######################
    # Document Management #
    #######################

    def has_document(self, document, rev=None, check_rev=True):
        """Check if a document exists.

        :param document: Document ID or body with "_id" field.
        :type document: str | unicode | dict
        :param rev: Expected document revision. Overrides value of "_rev" field
            in **document** if present.
        :type rev: str | unicode
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :return: True if document exists, False otherwise.
        :rtype: bool
        :raise arango.exceptions.DocumentInError: If check fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_doc(document).has(
            document=document,
            rev=rev,
            check_rev=check_rev
        )

    def document(self, document, rev=None, check_rev=True):
        """Return a document.

        :param document: Document ID or body with "_id" field.
        :type document: str | unicode | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **document** if present.
        :type rev: str | unicode
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :return: Document, or None if not found.
        :rtype: dict | None
        :raise arango.exceptions.DocumentGetError: If retrieval fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_doc(document).get(
            document=document,
            rev=rev,
            check_rev=check_rev
        )

    def insert_document(self,
                        collection,
                        document,
                        return_new=False,
                        sync=None,
                        silent=False):
        """Insert a new document.

        :param collection: Collection name.
        :type collection: str | unicode
        :param document: Document to insert. If it contains the "_key" or "_id"
            field, the value is used as the key of the new document (otherwise
            it is auto-generated). Any "_rev" field is ignored.
        :type document: dict
        :param return_new: Include body of the new document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_new: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentInsertError: If insert fails.
        """
        return self.collection(collection).insert(
            document=document,
            return_new=return_new,
            sync=sync,
            silent=silent
        )

    def update_document(self,
                        document,
                        check_rev=True,
                        merge=True,
                        keep_none=True,
                        return_new=False,
                        return_old=False,
                        sync=None,
                        silent=False):
        """Update a document.

        :param document: Partial or full document with the updated values. It
            must contain the "_id" field.
        :type document: dict
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :param merge: If set to True, sub-dictionaries are merged instead of
            the new one overwriting the old one.
        :type merge: bool
        :param keep_none: If set to True, fields with value None are retained
            in the document. Otherwise, they are removed completely.
        :type keep_none: bool
        :param return_new: Include body of the new document in the result.
        :type return_new: bool
        :param return_old: Include body of the old document in the result.
        :type return_old: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentUpdateError: If update fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_doc(document).update(
            document=document,
            check_rev=check_rev,
            merge=merge,
            keep_none=keep_none,
            return_new=return_new,
            return_old=return_old,
            sync=sync,
            silent=silent
        )

    def replace_document(self,
                         document,
                         check_rev=True,
                         return_new=False,
                         return_old=False,
                         sync=None,
                         silent=False):
        """Replace a document.

        :param document: New document to replace the old one with. It must
            contain the "_id" field. Edge document must also have "_from" and
            "_to" fields.
        :type document: dict
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :param return_new: Include body of the new document in the result.
        :type return_new: bool
        :param return_old: Include body of the old document in the result.
        :type return_old: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentReplaceError: If replace fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_doc(document).replace(
            document=document,
            check_rev=check_rev,
            return_new=return_new,
            return_old=return_old,
            sync=sync,
            silent=silent
        )

    def delete_document(self,
                        document,
                        rev=None,
                        check_rev=True,
                        ignore_missing=False,
                        return_old=False,
                        sync=None,
                        silent=False):
        """Delete a document.

        :param document: Document ID, key or body. Document body must contain
            the "_id" field.
        :type document: str | unicode | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **document** if present.
        :type rev: str | unicode
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :param ignore_missing: Do not raise an exception on missing document.
            This parameter has no effect in transactions where an exception is
            always raised on failures.
        :type ignore_missing: bool
        :param return_old: Include body of the old document in the result.
        :type return_old: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: Document metadata (e.g. document key, revision), or True if
            parameter **silent** was set to True, or False if document was not
            found and **ignore_missing** was set to True (does not apply in
            transactions).
        :rtype: bool | dict
        :raise arango.exceptions.DocumentDeleteError: If delete fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_doc(document).delete(
            document=document,
            rev=rev,
            check_rev=check_rev,
            ignore_missing=ignore_missing,
            return_old=return_old,
            sync=sync,
            silent=silent
        )

    ###################
    # Task Management #
    ###################

    def tasks(self):
        """Return all currently active server tasks.

        :return: Currently active server tasks.
        :rtype: [dict]
        :raise arango.exceptions.TaskListError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_api/tasks'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise TaskListError(resp, request)
            return resp.body

        return self._execute(request, response_handler)

    def task(self, task_id):
        """Return the details of an active server task.

        :param task_id: Server task ID.
        :type task_id: str | unicode
        :return: Server task details.
        :rtype: dict
        :raise arango.exceptions.TaskGetError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_api/tasks/{}'.format(task_id)
        )

        def response_handler(resp):
            if not resp.is_success:
                raise TaskGetError(resp, request)
            resp.body.pop('code', None)
            resp.body.pop('error', None)
            return resp.body

        return self._execute(request, response_handler)

    def create_task(self,
                    name,
                    command,
                    params=None,
                    period=None,
                    offset=None,
                    task_id=None):
        """Create a new server task.

        :param name: Name of the server task.
        :type name: str | unicode
        :param command: Javascript command to execute.
        :type command: str | unicode
        :param params: Optional parameters passed into the Javascript command.
        :type params: dict
        :param period: Number of seconds to wait between executions. If set
            to 0, the new task will be "timed", meaning it will execute only
            once and be deleted afterwards.
        :type period: int
        :param offset: Initial delay before execution in seconds.
        :type offset: int
        :param task_id: Pre-defined ID for the new server task.
        :type task_id: str | unicode
        :return: Details of the new task.
        :rtype: dict
        :raise arango.exceptions.TaskCreateError: If create fails.
        """
        data = {'name': name, 'command': command}
        if params is not None:
            data['params'] = params
        if task_id is not None:
            data['id'] = task_id
        if period is not None:
            data['period'] = period
        if offset is not None:
            data['offset'] = offset

        if task_id is None:
            task_id = ''

        request = Request(
            method='post',
            endpoint='/_api/tasks/{}'.format(task_id),
            data=data
        )

        def response_handler(resp):
            if not resp.is_success:
                raise TaskCreateError(resp, request)
            resp.body.pop('code', None)
            resp.body.pop('error', None)
            return resp.body

        return self._execute(request, response_handler)

    def delete_task(self, task_id, ignore_missing=False):
        """Delete a server task.

        :param task_id: Server task ID.
        :type task_id: str | unicode
        :param ignore_missing: Do not raise an exception on missing task.
        :type ignore_missing: bool
        :return: True if task was successfully deleted, False if task was not
            found and **ignore_missing** was set to True.
        :rtype: bool
        :raise arango.exceptions.TaskDeleteError: If delete fails.
        """
        request = Request(
            method='delete',
            endpoint='/_api/tasks/{}'.format(task_id)
        )

        def response_handler(resp):
            if resp.error_code == 1852 and ignore_missing:
                return False
            if not resp.is_success:
                raise TaskDeleteError(resp, request)
            return True

        return self._execute(request, response_handler)

    ###################
    # User Management #
    ###################

    def has_user(self, username):
        """Check if user exists.

        :param username: Username.
        :type username: str | unicode
        :return: True if user exists, False otherwise.
        :rtype: bool
        """
        return any(user['username'] == username for user in self.users())

    def users(self):
        """Return all user details.

        :return: List of user details.
        :rtype: [dict]
        :raise arango.exceptions.UserListError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_api/user'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise UserListError(resp, request)
            return [{
                'username': record['user'],
                'active': record['active'],
                'extra': record['extra'],
            } for record in resp.body['result']]

        return self._execute(request, response_handler)

    def user(self, username):
        """Return user details.

        :param username: Username.
        :type username: str | unicode
        :return: User details.
        :rtype: dict
        :raise arango.exceptions.UserGetError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_api/user/{}'.format(username)
        )

        def response_handler(resp):
            if not resp.is_success:
                raise UserGetError(resp, request)
            return {
                'username': resp.body['user'],
                'active': resp.body['active'],
                'extra': resp.body['extra']
            }

        return self._execute(request, response_handler)

    def create_user(self, username, password, active=True, extra=None):
        """Create a new user.

        :param username: Username.
        :type username: str | unicode
        :param password: Password.
        :type password: str | unicode
        :param active: True if user is active, False otherwise.
        :type active: bool
        :param extra: Additional data for the user.
        :type extra: dict
        :return: New user details.
        :rtype: dict
        :raise arango.exceptions.UserCreateError: If create fails.
        """
        data = {'user': username, 'passwd': password, 'active': active}
        if extra is not None:
            data['extra'] = extra

        request = Request(
            method='post',
            endpoint='/_api/user',
            data=data
        )

        def response_handler(resp):
            if not resp.is_success:
                raise UserCreateError(resp, request)
            return {
                'username': resp.body['user'],
                'active': resp.body['active'],
                'extra': resp.body['extra'],
            }

        return self._execute(request, response_handler)

    def update_user(self, username, password=None, active=None, extra=None):
        """Update a user.

        :param username: Username.
        :type username: str | unicode
        :param password: New password.
        :type password: str | unicode
        :param active: Whether the user is active.
        :type active: bool
        :param extra: Additional data for the user.
        :type extra: dict
        :return: New user details.
        :rtype: dict
        :raise arango.exceptions.UserUpdateError: If update fails.
        """
        data = {}
        if password is not None:
            data['passwd'] = password
        if active is not None:
            data['active'] = active
        if extra is not None:
            data['extra'] = extra

        request = Request(
            method='patch',
            endpoint='/_api/user/{user}'.format(user=username),
            data=data
        )

        def response_handler(resp):
            if not resp.is_success:
                raise UserUpdateError(resp, request)
            return {
                'username': resp.body['user'],
                'active': resp.body['active'],
                'extra': resp.body['extra'],
            }

        return self._execute(request, response_handler)

    def replace_user(self, username, password, active=None, extra=None):
        """Replace a user.

        :param username: Username.
        :type username: str | unicode
        :param password: New password.
        :type password: str | unicode
        :param active: Whether the user is active.
        :type active: bool
        :param extra: Additional data for the user.
        :type extra: dict
        :return: New user details.
        :rtype: dict
        :raise arango.exceptions.UserReplaceError: If replace fails.
        """
        data = {'user': username, 'passwd': password}
        if active is not None:
            data['active'] = active
        if extra is not None:
            data['extra'] = extra

        request = Request(
            method='put',
            endpoint='/_api/user/{user}'.format(user=username),
            data=data
        )

        def response_handler(resp):
            if resp.is_success:
                return {
                    'username': resp.body['user'],
                    'active': resp.body['active'],
                    'extra': resp.body['extra'],
                }
            raise UserReplaceError(resp, request)

        return self._execute(request, response_handler)

    def delete_user(self, username, ignore_missing=False):
        """Delete a user.

        :param username: Username.
        :type username: str | unicode
        :param ignore_missing: Do not raise an exception on missing user.
        :type ignore_missing: bool
        :return: True if user was deleted successfully, False if user was not
            found and **ignore_missing** was set to True.
        :rtype: bool
        :raise arango.exceptions.UserDeleteError: If delete fails.
        """
        request = Request(
            method='delete',
            endpoint='/_api/user/{user}'.format(user=username)
        )

        def response_handler(resp):
            if resp.is_success:
                return True
            elif resp.status_code == 404 and ignore_missing:
                return False
            raise UserDeleteError(resp, request)

        return self._execute(request, response_handler)

    #########################
    # Permission Management #
    #########################

    def permissions(self, username):
        """Return user permissions for all databases and collections.

        :param username: Username.
        :type username: str | unicode
        :return: User permissions for all databases and collections.
        :rtype: dict
        :raise: arango.exceptions.PermissionListError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_api/user/{}/database'.format(username),
            params={'full': True}
        )

        def response_handler(resp):
            if resp.is_success:
                return resp.body['result']
            raise PermissionListError(resp, request)

        return self._execute(request, response_handler)

    def permission(self, username, database, collection=None):
        """Return user permission for a specific database or collection.

        :param username: Username.
        :type username: str | unicode
        :param database: Database name.
        :type database: str | unicode
        :param collection: Collection name.
        :type collection: str | unicode
        :return: Permission for given database or collection.
        :rtype: str | unicode
        :raise: arango.exceptions.PermissionGetError: If retrieval fails.
        """
        endpoint = '/_api/user/{}/database/{}'.format(username, database)
        if collection is not None:
            endpoint += '/' + collection
        request = Request(method='get', endpoint=endpoint)

        def response_handler(resp):
            if not resp.is_success:
                raise PermissionGetError(resp, request)
            return resp.body['result']

        return self._execute(request, response_handler)

    def update_permission(self,
                          username,
                          permission,
                          database,
                          collection=None):
        """Update user permission for a specific database or collection.

        :param username: Username.
        :type username: str | unicode
        :param database: Database name.
        :type database: str | unicode
        :param collection: Collection name.
        :type collection: str | unicode
        :param permission: Allowed values are "rw" (read and write), "ro"
            (read only) or "none" (no access).
        :type permission: str | unicode
        :return: True if access was granted successfully.
        :rtype: bool
        :raise arango.exceptions.PermissionUpdateError: If update fails.
        """
        endpoint = '/_api/user/{}/database/{}'.format(username, database)
        if collection is not None:
            endpoint += '/' + collection

        request = Request(
            method='put',
            endpoint=endpoint,
            data={'grant': permission}
        )

        def response_handler(resp):
            if resp.is_success:
                return True
            raise PermissionUpdateError(resp, request)

        return self._execute(request, response_handler)

    def reset_permission(self, username, database, collection=None):
        """Reset user permission for a specific database or collection.

        :param username: Username.
        :type username: str | unicode
        :param database: Database name.
        :type database: str | unicode
        :param collection: Collection name.
        :type collection: str | unicode
        :return: True if permission was reset successfully.
        :rtype: bool
        :raise arango.exceptions.PermissionRestError: If reset fails.
        """
        endpoint = '/_api/user/{}/database/{}'.format(username, database)
        if collection is not None:
            endpoint += '/' + collection

        request = Request(method='delete', endpoint=endpoint)

        def response_handler(resp):
            if resp.is_success:
                return True
            raise PermissionResetError(resp, request)

        return self._execute(request, response_handler)

    ########################
    # Async Job Management #
    ########################

    def async_jobs(self, status, count=None):
        """Return IDs of async jobs with given status.

        :param status: Job status (e.g. "pending", "done").
        :type status: str | unicode
        :param count: Max number of job IDs to return.
        :type count: int
        :return: List of job IDs.
        :rtype: [str | unicode]
        :raise arango.exceptions.AsyncJobListError: If retrieval fails.
        """
        params = {}
        if count is not None:
            params['count'] = count

        request = Request(
            method='get',
            endpoint='/_api/job/{}'.format(status),
            params=params
        )

        def response_handler(resp):
            if resp.is_success:
                return resp.body
            raise AsyncJobListError(resp, request)

        return self._execute(request, response_handler)

    def clear_async_jobs(self, threshold=None):
        """Clear async job results from the server.

        Async jobs that are still queued or running are not stopped.

        :param threshold: If specified, only the job results created prior to
            the threshold (a unix timestamp) are deleted. Otherwise, all job
            results are deleted.
        :type threshold: int
        :return: True if job results were cleared successfully.
        :rtype: bool
        :raise arango.exceptions.AsyncJobClearError: If operation fails.
        """
        if threshold is None:
            url = '/_api/job/all'
            params = None
        else:
            url = '/_api/job/expired'
            params = {'stamp': threshold}

        request = Request(
            method='delete',
            endpoint=url,
            params=params
        )

        def response_handler(resp):
            if resp.is_success:
                return True
            raise AsyncJobClearError(resp, request)

        return self._execute(request, response_handler)


class StandardDatabase(Database):
    """Standard database API wrapper.

    :param connection: HTTP connection.
    :type connection: arango.connection.Connection
    """

    def __init__(self, connection):
        super(StandardDatabase, self).__init__(
            connection=connection,
            executor=DefaultExecutor(connection)
        )

    def __repr__(self):
        return '<StandardDatabase {}>'.format(self.name)

    def begin_async_execution(self, return_result=True):
        """Begin async execution.

        :param return_result: If set to True, API executions return instances
            of :class:`arango.job.AsyncJob`, which you can use to retrieve
            results from server once available. If set to False, API executions
            return None and no results are stored on server.
        :type return_result: bool
        :return: Database API wrapper built specifically for async execution.
        :rtype: arango.database.AsyncDatabase
        """
        return AsyncDatabase(self._conn, return_result)

    def begin_batch_execution(self, return_result=True):
        """Begin batch execution.

        :param return_result: If set to True, API executions return instances
            of :class:`arango.job.BatchJob` that are populated with results on
            commit. If set to False, API executions return None and no results
            are tracked client-side.
        :type return_result: bool
        :return: Database API wrapper built specifically for batch execution.
        :rtype: arango.database.BatchDatabase
        """
        return BatchDatabase(self._conn, return_result)

    def begin_transaction(self,
                          return_result=True,
                          timeout=None,
                          sync=None,
                          read=None,
                          write=None):
        """Begin transaction.

        :param return_result: If set to True, API executions return instances
            of :class:`arango.job.TransactionJob` that are populated with
            results on commit. If set to False, API executions return None and
            no results are tracked client-side.
        :type return_result: bool
        :param read: Names of collections read during transaction. If not
            specified, they are added automatically as jobs are queued.
        :type read: [str | unicode]
        :param write: Names of collections written to during transaction.
            If not specified, they are added automatically as jobs are queued.
        :type write: [str | unicode]
        :param timeout: Timeout for waiting on collection locks. If set to 0,
            ArangoDB server waits indefinitely. If not set, system default
            value is used.
        :type timeout: int
        :param sync: Block until the transaction is synchronized to disk.
        :type sync: bool
        :return: Database API wrapper built specifically for transactions.
        :rtype: arango.database.TransactionDatabase
        """
        return TransactionDatabase(
            connection=self._conn,
            return_result=return_result,
            read=read,
            write=write,
            timeout=timeout,
            sync=sync
        )


class AsyncDatabase(Database):
    """Database API wrapper tailored specifically for async execution.

    See :func:`arango.database.StandardDatabase.begin_async_execution`.

    :param connection: HTTP connection.
    :type connection: arango.connection.Connection
    :param return_result: If set to True, API executions return instances of
        :class:`arango.job.AsyncJob`, which you can use to retrieve results
        from server once available. If set to False, API executions return None
        and no results are stored on server.
    :type return_result: bool
    """

    def __init__(self, connection, return_result):
        super(AsyncDatabase, self).__init__(
            connection=connection,
            executor=AsyncExecutor(connection, return_result)
        )

    def __repr__(self):
        return '<AsyncDatabase {}>'.format(self.name)


class BatchDatabase(Database):
    """Database API wrapper tailored specifically for batch execution.

    See :func:`arango.database.StandardDatabase.begin_batch_execution`.

    :param connection: HTTP connection.
    :type connection: arango.connection.Connection
    :param return_result: If set to True, API executions return instances of
        :class:`arango.job.BatchJob` that are populated with results on commit.
        If set to False, API executions return None and no results are tracked
        client-side.
    :type return_result: bool
    """

    def __init__(self, connection, return_result):
        super(BatchDatabase, self).__init__(
            connection=connection,
            executor=BatchExecutor(connection, return_result)
        )

    def __repr__(self):
        return '<BatchDatabase {}>'.format(self.name)

    def __enter__(self):
        return self

    def __exit__(self, exception, *_):
        if exception is None:
            self._executor.commit()

    def queued_jobs(self):
        """Return the queued batch jobs.

        :return: Queued batch jobs or None if **return_result** parameter was
            set to False during initialization.
        :rtype: [arango.job.BatchJob] | None
        """
        return self._executor.jobs

    def commit(self):
        """Execute the queued requests in a single batch API request.

        If **return_result** parameter was set to True during initialization,
        :class:`arango.job.BatchJob` instances are populated with results.

        :return: Batch jobs, or None if **return_result** parameter was set to
            False during initialization.
        :rtype: [arango.job.BatchJob] | None
        :raise arango.exceptions.BatchStateError: If batch state is invalid
            (e.g. batch was already committed or the response size did not
            match expected).
        :raise arango.exceptions.BatchExecuteError: If commit fails.
        """
        return self._executor.commit()


class TransactionDatabase(Database):
    """Database API wrapper tailored specifically for transactions.

    See :func:`arango.database.StandardDatabase.begin_transaction`.

    :param connection: HTTP connection.
    :type connection: arango.connection.Connection
    :param return_result: If set to True, API executions return instances of
        :class:`arango.job.TransactionJob` that are populated with results on
        commit. If set to False, API executions return None and no results are
        tracked client-side.
    :type return_result: bool
    :param read: Names of collections read during transaction.
    :type read: [str | unicode]
    :param write: Names of collections written to during transaction.
    :type write: [str | unicode]
    :param timeout: Timeout for waiting on collection locks. If set to 0, the
        ArangoDB server waits indefinitely. If not set, system default value
        is used.
    :type timeout: int
    :param sync: Block until operation is synchronized to disk.
    :type sync: bool
    """

    def __init__(self, connection, return_result, read, write, timeout, sync):
        super(TransactionDatabase, self).__init__(
            connection=connection,
            executor=TransactionExecutor(
                connection=connection,
                return_result=return_result,
                read=read,
                write=write,
                timeout=timeout,
                sync=sync
            )
        )

    def __repr__(self):
        return '<TransactionDatabase {}>'.format(self.name)

    def __enter__(self):
        return self

    def __exit__(self, exception, *_):
        if exception is None:
            self._executor.commit()

    def queued_jobs(self):
        """Return the queued transaction jobs.

        :return: Queued transaction jobs, or None if **return_result** was set
            to False during initialization.
        :rtype: [arango.job.TransactionJob] | None
        """
        return self._executor.jobs

    def commit(self):
        """Execute the queued requests in a single transaction API request.

        If **return_result** parameter was set to True during initialization,
        :class:`arango.job.TransactionJob` instances are populated with
        results.

        :return: Transaction jobs, or None if **return_result** parameter was
            set to False during initialization.
        :rtype: [arango.job.TransactionJob] | None
        :raise arango.exceptions.TransactionStateError: If the transaction was
            already committed.
        :raise arango.exceptions.TransactionExecuteError: If commit fails.
        """
        return self._executor.commit()
