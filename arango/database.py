from __future__ import absolute_import, unicode_literals

from datetime import datetime

from arango import Request
from arango.connections import (
    AsyncExecution,
    BatchExecution,
    ClusterTest,
    Transaction
)
from arango.connections import BaseConnection
from arango.collections import Collection
from arango.utils import HTTP_OK
from arango.exceptions import (
    AsyncJobClearError,
    AsyncJobListError,
    CollectionCreateError,
    CollectionDeleteError,
    CollectionListError,
    DatabaseListError,
    DatabasePropertiesError,
    DocumentGetError,
    DocumentRevisionError,
    GraphListError,
    GraphCreateError,
    GraphDeleteError,
    PregelJobCreateError,
    PregelJobDeleteError,
    PregelJobGetError,
    ServerConnectionError,
    ServerDetailsError,
    ServerEchoError,
    ServerExecuteError,
    ServerLogLevelError,
    ServerLogLevelSetError,
    ServerReadLogError,
    ServerReloadRoutingError,
    ServerRequiredDBVersionError,
    ServerRoleError,
    ServerRunTestsError,
    ServerShutdownError,
    ServerSleepError,
    ServerStatisticsError,
    ServerTimeError,
    ServerVersionError,
    TaskCreateError,
    TaskDeleteError,
    TaskGetError,
    TaskListError,
    UserAccessError,
    UserCreateError,
    UserDeleteError,
    UserGetError,
    UserGrantAccessError,
    UserListError,
    UserRevokeAccessError,
    UserReplaceError,
    UserUpdateError,
)
from arango.wrappers import Graph, AQL
from arango import APIWrapper
from arango import WriteAheadLog


class Database(APIWrapper):
    """ArangoDB database.

    :param connection: ArangoDB database connection
    :type connection: arango.connection.Connection

    """

    def __init__(self, connection):
        super(Database, self).__init__(connection)
        self._aql = AQL(self._conn)
        self._wal = WriteAheadLog(self._conn)

    def __repr__(self):
        return '<ArangoDB database "{}">'.format(self.name)

    def __getitem__(self, name):
        return self.collection(name)

    @property
    def protocol(self):
        """Return the internet transfer protocol.

        :returns: the internet transfer protocol
        :rtype: str | unicode
        """
        return self._conn.protocol

    @property
    def host(self):
        """Return the ArangoDB host.

        :returns: the ArangoDB host
        :rtype: str | unicode
        """
        return self._conn.host

    @property
    def port(self):
        """Return the ArangoDB port.

        :returns: the ArangoDB port
        :rtype: int
        """
        return self._conn.port

    @property
    def username(self):
        """Return the ArangoDB username.

        :returns: the ArangoDB username
        :rtype: str | unicode
        """
        return self._conn.username

    @property
    def password(self):
        """Return the ArangoDB user password.

        :returns: the ArangoDB user password
        :rtype: str | unicode
        """
        return self._conn.password

    @property
    def http_client(self):
        """Return the HTTP client.

        :returns: the HTTP client
        :rtype: arango.http_clients.base.BaseHTTPClient
        """
        return self._conn.http_client

    @property
    def logging_enabled(self):
        """Return True if logging is enabled, False otherwise.

        :returns: whether logging is enabled
        :rtype: bool
        """
        return self._conn.logging_enabled

    @property
    def connection(self):
        """Return the connection object.

        :return: the database connection object
        :rtype: arango.connection.Connection
        """
        return self._conn

    @property
    def name(self):
        """Return the name of the database.

        :returns: the name of the database
        :rtype: str | unicode
        """
        return self._conn.database

    @property
    def aql(self):
        """Return the AQL object used to execute AQL statements.

        Refer to :class:`arango.query.Query` for more information.

        :returns: the AQL object
        :rtype: arango.query.AQL
        """
        return self._aql

    @property
    def wal(self):
        """Return the write-ahead log object.

        :returns: the write-ahead log object
        :rtype: arango.wal.WriteAheadLog
        """
        return self._wal

    def db(self, name, username=None, password=None):
        """Return the database object.

        This is an alias for
        :func:`arango.api.databases.BaseDatabase.database`.

        :param name: the name of the database
        :type name: str | unicode
        :param username: the username for authentication (if set, overrides
            the username specified during the client initialization)
        :type username: str | unicode
        :param password: the password for authentication (if set, overrides
            the password specified during the client initialization
        :type password: str | unicode
        :returns: the database object
        :rtype: arango.database.Database
        """
        db = self.database(name, username, password)
        return db

    def database(self, name, username=None, password=None):
        """Return the database object.

        :param name: the name of the database
        :type name: str | unicode
        :param username: the username for authentication (if set, overrides
            the username specified during the client initialization)
        :type username: str | unicode
        :param password: the password for authentication (if set, overrides
            the password specified during the client initialization
        :type password: str | unicode
        :returns: the database object
        :rtype: arango.database.Database
        """

        if username is None:
            username = self.username

        if password is None:
            password = self.password

        return Database(BaseConnection(
            protocol=self.protocol,
            host=self.host,
            port=self.port,
            database=name,
            username=username,
            password=password,
            http_client=self.http_client,
            enable_logging=self.logging_enabled,
            async_ready=self._conn.async_ready
        ))

    def verify(self):
        """Verify the connection to ArangoDB server.

        :returns: ``True`` if the connection is successful
        :rtype: bool
        :raises arango.exceptions.ServerConnectionError: if the connection to
            the ArangoDB server fails
        """
        
        request = Request(
            method='head',
            endpoint='/_api/version'
        )

        def handler(res):
            x = res.status_code
            if x not in HTTP_OK:
                raise ServerConnectionError(res)
            return True

        return self.handle_request(request, handler)

    def version(self):
        """Return the version of the ArangoDB server.

        :returns: the server version
        :rtype: str | unicode
        :raises arango.exceptions.ServerVersionError: if the server version
            cannot be retrieved
        """

        request = Request(
            method='get',
            endpoint='/_api/version',
            params={'details': False}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise ServerVersionError(res)
            return res.body['version']

        return self.handle_request(request, handler)

    def details(self):
        """Return the component details on the ArangoDB server.

        :returns: the server details
        :rtype: dict
        :raises arango.exceptions.ServerDetailsError: if the server details
            cannot be retrieved
        """

        request = Request(
            method='get',
            endpoint='/_api/version',
            params={'details': True}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise ServerDetailsError(res)
            return res.body['details']

        return self.handle_request(request, handler)

    def required_db_version(self):
        """Return the required version of the target database.

        :returns: the required version of the target database
        :rtype: str | unicode
        :raises arango.exceptions.ServerRequiredDBVersionError: if the
            required database version cannot be retrieved
        """

        request = Request(
            method='get',
            endpoint='/_admin/database/target-version'
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise ServerRequiredDBVersionError(res)
            return res.body['version']

        return self.handle_request(request, handler)

    def databases(self, user_only=False):
        """Return the database names.

        :param user_only: list only the databases accessible by the user
        :type user_only: bool
        :returns: the database names
        :rtype: list
        :raises arango.exceptions.DatabaseListError: if the retrieval fails
        """

        # Get the current user's databases
        if user_only:
            url = '/_api/database/user'
        else:
            url = '/_api/database'

        request = Request(
            method='get',
            endpoint=url
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DatabaseListError(res)
            return res.body['result']

        return self.handle_request(request, handler)

    def statistics(self, description=False):
        """Return the server statistics.

        :returns: the statistics information
        :rtype: dict
        :raises arango.exceptions.ServerStatisticsError: if the server
            statistics cannot be retrieved
        """

        if description:
            url = '/_admin/statistics-description'
        else:
            url = '/_admin/statistics'

        request = Request(
            method='get',
            endpoint=url
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise ServerStatisticsError(res)
            res.body.pop('code', None)
            res.body.pop('error', None)
            return res.body

        return self.handle_request(request, handler)

    def role(self):
        """Return the role of the server in the cluster if any.

        :returns: the server role which can be ``"SINGLE"`` (the server is not
            in a cluster), ``"COORDINATOR"`` (the server is a coordinator in
            the cluster), ``"PRIMARY"`` (the server is a primary database in
            the cluster), ``"SECONDARY"`` (the server is a secondary database
            in the cluster) or ``"UNDEFINED"`` (the server role is undefined,
            the only possible value for a single server)
        :rtype: str | unicode
        :raises arango.exceptions.ServerRoleError: if the server role cannot
            be retrieved
        """

        request = Request(
            method='get',
            endpoint='/_admin/server/role'
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise ServerRoleError(res)
            return res.body.get('role')

        return self.handle_request(request, handler)

    def time(self):
        """Return the current server system time.

        :returns: the server system time
        :rtype: datetime.datetime
        :raises arango.exceptions.ServerTimeError: if the server time
            cannot be retrieved
        """

        request = Request(
            method='get',
            endpoint='/_admin/time'
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise ServerTimeError(res)
            return datetime.fromtimestamp(res.body['time'])

        return self.handle_request(request, handler)

    def echo(self):
        """Return information on the last request (headers, payload etc.)

        :returns: the details of the last request
        :rtype: dict
        :raises arango.exceptions.ServerEchoError: if the last request cannot
            be retrieved from the server
        """
        request = Request(
            method='get',
            endpoint='/_admin/echo'
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise ServerEchoError(res)
            return res.body

        return self.handle_request(request, handler)

    def sleep(self, seconds):
        """Suspend the execution for a specified duration before returning.

        :param seconds: the number of seconds to suspend
        :type seconds: int
        :returns: the number of seconds suspended
        :rtype: int
        :raises arango.exceptions.ServerSleepError: if the server cannot be
            suspended
        """
        request = Request(
            method='get',
            endpoint='/_admin/sleep',
            params={'duration': seconds}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise ServerSleepError(res)
            return res.body['duration']

        return self.handle_request(request, handler)

    def shutdown(self):  # pragma: no cover
        """Initiate the server shutdown sequence.

        :returns: whether the server was shutdown successfully
        :rtype: bool
        :raises arango.exceptions.ServerShutdownError: if the server shutdown
            sequence cannot be initiated
        """

        request = Request(
            method='delete',
            endpoint='/_admin/shutdown'
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise ServerShutdownError(res)
            return True

        return self.handle_request(request, handler)

    def run_tests(self, tests):  # pragma: no cover
        """Run the available unittests on the server.

        :param tests: list of files containing the test suites
        :type tests: list
        :returns: the test results
        :rtype: dict
        :raises arango.exceptions.ServerRunTestsError: if the test suites fail
        """

        request = Request(
            method='post',
            endpoint='/_admin/test',
            data={'tests': tests}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise ServerRunTestsError(res)
            return res.body

        return self.handle_request(request, handler)

    def execute(self, program):  # pragma: no cover
        """Execute a Javascript program on the server.

        :param program: the body of the Javascript program to execute.
        :type program: str | unicode
        :returns: the result of the execution
        :rtype: str | unicode
        :raises arango.exceptions.ServerExecuteError: if the program cannot
            be executed on the server
        """

        request = Request(
            method='post',
            endpoint='/_admin/execute',
            data=program
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise ServerExecuteError(res)
            return res.body

        return self.handle_request(request, handler)

    def read_log(self,
                 upto=None,
                 level=None,
                 start=None,
                 size=None,
                 offset=None,
                 search=None,
                 sort=None):
        """Read the global log from the server.

        :param upto: return the log entries up to the given level (mutually
            exclusive with argument **level**), which must be ``"fatal"``,
            ``"error"``, ``"warning"``, ``"info"`` (default) or ``"debug"``
        :type upto: str | unicode | int
        :param level: return the log entries of only the given level (mutually
            exclusive with **upto**), which must be ``"fatal"``, ``"error"``,
            ``"warning"``, ``"info"`` (default) or ``"debug"``
        :type level: str | unicode | int
        :param start: return the log entries whose ID is greater or equal to
            the given value
        :type start: int
        :param size: restrict the size of the result to the given value (this
            setting can be used for pagination)
        :type size: int
        :param offset: the number of entries to skip initially (this setting
            can be setting can be used for pagination)
        :type offset: int
        :param search: return only the log entries containing the given text
        :type search: str | unicode
        :param sort: sort the log entries according to the given fashion, which
            can be ``"sort"`` or ``"desc"``
        :type sort: str | unicode
        :returns: the server log entries
        :rtype: dict
        :raises arango.exceptions.ServerReadLogError: if the server log entries
            cannot be read
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

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise ServerReadLogError(res)
            if 'totalAmount' in res.body:
                res.body['total_amount'] = res.body.pop('totalAmount')
            return res.body

        return self.handle_request(request, handler)

    def log_levels(self):
        """Return the current logging levels.

        :return: the current logging levels
        :rtype: dict

        .. note::
            This method is only compatible with ArangoDB version 3.1+ only.
        """

        request = Request(
            method='get',
            endpoint='/_admin/log/level'
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise ServerLogLevelError(res)
            return res.body

        return self.handle_request(request, handler)

    def set_log_levels(self, **kwargs):
        """Set the logging levels.

        This method takes arbitrary keyword arguments where the keys are the
        logger names and the values are the logging levels. For example:

        .. code-block:: python

            arango.set_log_level(
                agency='DEBUG',
                collector='INFO',
                threads='WARNING'
            )

        :return: the new logging levels
        :rtype: dict

        .. note::
            Keys that are not valid logger names are simply ignored.

        .. note::
            This method is only compatible with ArangoDB version 3.1+ only.
        """

        request = Request(
            method='put',
            endpoint='/_admin/log/level',
            data=kwargs
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise ServerLogLevelSetError(res)
            return res.body

        return self.handle_request(request, handler)

    def reload_routing(self):
        """Reload the routing information from the collection *routing*.

        :returns: whether the routing was reloaded successfully
        :rtype: bool
        :raises arango.exceptions.ServerReloadRoutingError: if the routing
            cannot be reloaded
        """

        request = Request(
            method='post',
            endpoint='/_admin/routing/reload'
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise ServerReloadRoutingError(res)
            return 'error' not in res.body

        return self.handle_request(request, handler)

    def asynchronous(self, return_result=True):
        """Return the asynchronous request object.

        Refer to :class:`arango.async.AsyncExecution` for more information.

        :param return_result: store and return the result
        :type return_result: bool
        :returns: the async request object
        :rtype: :class:`arango.async.AsyncExecution`
        """
        return AsyncExecution(self._conn, return_result)

    def batch(self, return_result=True, commit_on_error=True,
              submit_timeout=-1):
        """Return the batch request object.

        Refer to :class:`arango.batch.BatchExecution` for more information.

        :param return_result: store and return the result
        :type return_result: bool
        :param commit_on_error: commit when an exception is raised
            (this is only applicable when context managers are used)
        :type commit_on_error: bool
        :param submit_timeout: the timeout to use for acquiring the lock
        necessary to submit a batch.  Only relevant in multi-threaded contexts.
        In single threaded contexts, acquiring this lock will never fail.
        A value of <= 0 means wait forever, a positive value indicates the
        number of seconds to wait.
        :type submit_timeout: int
        :returns: the batch request object
        :rtype: :class:`arango.batch.BatchExecution`
        """
        return BatchExecution(self._conn, return_result, commit_on_error,
                              submit_timeout)

    def transaction(self,
                    read=None,
                    write=None,
                    sync=None,
                    timeout=None,
                    commit_on_error=True):
        """Return the transaction object.

        Refer to :class:`arango.transaction.Transaction` for more information.

        :param read: the name(s) of the collection(s) to read from
        :type read: str | unicode | list
        :param write: the name(s) of the collection(s) to write to
        :type write: str | unicode | list
        :param sync: wait for the operation to sync to disk
        :type sync: bool
        :param timeout: timeout on the collection locks
        :type timeout: int
        :param commit_on_error: only applicable when *context managers* are
            used to execute the transaction: if ``True``, the requests
            queued so far are committed even if an exception is raised before
            exiting out of the context
        :type commit_on_error: bool
        """
        return Transaction(
            connection=self._conn,
            read=read,
            write=write,
            timeout=timeout,
            sync=sync,
            commit_on_error=commit_on_error
        )

    def cluster(self, shard_id, transaction_id=None, timeout=None, sync=None):
        """Return the cluster round-trip test object.

        :param shard_id: the ID of the shard to which the request is sent
        :type shard_id: str | unicode | int
        :param transaction_id: the transaction ID for the request
        :type transaction_id: str | unicode | int
        :param timeout: the timeout in seconds for the cluster operation, where
            an error is returned if the response does not arrive within the
            given limit (default: 24 hrs)
        :type timeout: int
        :param sync: if set to ``True``, the test uses synchronous mode,
            otherwise asynchronous mode is used (this is mainly for debugging
            purposes)
        :param sync: bool
        """
        return ClusterTest(
            connection=self._conn,
            shard_id=shard_id,
            transaction_id=transaction_id,
            timeout=timeout,
            sync=sync
        )

    def properties(self):
        """Return the database properties.

        :returns: the database properties
        :rtype: dict
        :raises arango.exceptions.DatabasePropertiesError: if the properties
            of the database cannot be retrieved
        """

        request = Request(
            method='get',
            endpoint='/_api/database/current'
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DatabasePropertiesError(res)
            result = res.body['result']
            result['system'] = result.pop('isSystem')
            return result

        return self.handle_request(request, handler)

    def get_document(self, document_id, rev=None, match_rev=True):
        """Retrieve a document by its ID (collection/key)

        :param document_id: the document ID
        :type document_id: str | unicode
        :returns: the document or ``None`` if the document is missing
        :rtype: dict
        :param rev: the revision to compare with that of the retrieved document
        :type rev: str | unicode
        :param match_rev: if ``True``, check if the given revision and
            the target document's revisions are the same, otherwise check if
            the revisions are different (this flag has an effect only when
            **rev** is given)
        :type match_rev: bool
        :raises arango.exceptions.DocumentRevisionError: if the given revision
            does not match the revision of the retrieved document
        :raises arango.exceptions.DocumentGetError: if the document cannot
            be retrieved from the collection
        """

        headers = {}

        if rev is not None:
            if match_rev:
                headers['If-Match'] = rev
            else:
                headers['If-None-Match'] = rev

        request = Request(
            method='get',
            endpoint='/_api/document/{}'.format(document_id),
            headers=headers
        )

        def handler(res):
            if res.status_code in {304, 412}:
                raise DocumentRevisionError(res)
            elif res.status_code == 404 and res.error_code == 1202:
                return None
            elif res.status_code in HTTP_OK:
                return res.body
            raise DocumentGetError(res)

        return self.handle_request(request, handler)

    #########################
    # Collection Management #
    #########################

    def collections(self):
        """Return the collections in the database.

        :returns: the details of the collections in the database
        :rtype: [dict]
        :raises arango.exceptions.CollectionListError: if the list of
            collections cannot be retrieved
        """

        request = Request(
            method='get',
            endpoint='/_api/collection'
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise CollectionListError(res)
            return [{
                'id': col['id'],
                'name': col['name'],
                'system': col['isSystem'],
                'type': Collection.TYPES[col['type']],
                'status': Collection.STATUSES[col['status']],
            } for col in map(dict, res.body['result'])]

        return self.handle_request(request, handler)

    def collection(self, name):
        """Return the collection object.

        :param name: the name of the collection
        :type name: str | unicode
        :returns: the collection object
        :rtype: arango.collections.Collection
        """
        return Collection(self._conn, name)

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
                          replication_factor=None):
        """Create a new collection.

        .. note::

            Starting from ArangoDB version 3.1+, system collections must have
            a name with a leading underscore ``_`` character.

        :param name: the name of the collection
        :type name: str | unicode
        :param sync: wait for the operation to sync to disk
        :type sync: bool
        :param compact: compact the collection
        :type compact: bool
        :param system: the collection is a system collection
        :type system: bool
        :param journal_size: the max size of the journal
        :type journal_size: int
        :param edge: the collection is an edge collection
        :type edge: bool
        :param volatile: the collection is in-memory only
        :type volatile: bool
        :param key_generator: "traditional" or "autoincrement"
        :type key_generator: str | unicode
        :param user_keys: allow users to supply keys
        :type user_keys: bool
        :param key_increment: the increment value (autoincrement only)
        :type key_increment: int
        :param key_offset: the offset value (autoincrement only)
        :type key_offset: int
        :param shard_fields: the field(s) used to determine the target shard
        :type shard_fields: list
        :param shard_count: the number of shards to create
        :type shard_count: int
        :param index_bucket_count: the number of buckets into which indexes
            using a hash table are split (the default is 16 and this number
            has to be a power of 2 and less than or equal to 1024); for very
            large collections one should increase this to avoid long pauses
            when the hash table has to be initially built or re-sized, since
            buckets are re-sized individually and can be initially built in
            parallel (e.g. 64 might be a sensible value for a collection with
            100,000,000 documents.
        :type index_bucket_count: int
        :param replication_factor: the number of copies of each shard on
            different servers in a cluster, whose allowed values are:

            .. code-block:: none

                1: only one copy is kept (no synchronous replication).

                k: k-1 replicas are kept and any two copies are replicated
                   across different DBServers synchronously, meaning every
                   write to the master is copied to all slaves before the
                   operation is reported successful.

            Default: ``1``.

        :type replication_factor: int
        :returns: the new collection object
        :rtype: arango.collections.Collection
        :raises arango.exceptions.CollectionCreateError: if the collection
            cannot be created in the database
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
            'keyOptions': key_options
        }

        if edge:
            data['type'] = 3
        else:
            data['type'] = 2

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

        request = Request(
            method='post',
            endpoint='/_api/collection',
            data=data
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise CollectionCreateError(res)
            return self.collection(name)

        return self.handle_request(request, handler)

    def delete_collection(self, name, ignore_missing=False, system=None):
        """Delete a collection.

        :param name: the name of the collection to delete
        :type name: str | unicode
        :param ignore_missing: do not raise if the collection is missing
        :type ignore_missing: bool
        :param system: whether the collection is a system collection (this
            option is only available with ArangoDB 3.1+, lower versions do
            distinguish between system or non-system collections)
        :type system: bool
        :returns: whether the deletion was successful
        :rtype: bool
        :raises arango.exceptions.CollectionDeleteError: if the collection
            cannot be deleted from the database
        """

        params = {}

        if system is not None:
            params['isSystem'] = system

        request = Request(
            method='delete',
            endpoint='/_api/collection/{}'.format(name),
            params=params
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                if not (res.status_code == 404 and ignore_missing):
                    raise CollectionDeleteError(res)
            return not res.body['error']

        return self.handle_request(request, handler)

    ####################
    # Graph Management #
    ####################

    def graphs(self):
        """List all graphs in the database.

        :returns: the graphs in the database
        :rtype: dict
        :raises arango.exceptions.GraphListError: if the list of graphs
            cannot be retrieved
        """

        request = Request(
            method='get',
            endpoint='/_api/gharial'
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise GraphListError(res)

            return [
                {
                    'name': record['_key'],
                    'revision': record['_rev'],
                    'edge_definitions': record['edgeDefinitions'],
                    'orphan_collections': record['orphanCollections'],
                    'smart': record.get('isSmart'),
                    'smart_field': record.get('smartGraphAttribute'),
                    'shard_count': record.get('numberOfShards')
                } for record in map(dict, res.body['graphs'])
            ]

        return self.handle_request(request, handler)

    def graph(self, name):
        """Return the graph object.

        :param name: the name of the graph
        :type name: str | unicode
        :returns: the requested graph object
        :rtype: arango.graph.Graph
        """
        return Graph(self._conn, name)

    def create_graph(self,
                     name,
                     edge_definitions=None,
                     orphan_collections=None,
                     smart=None,
                     smart_field=None,
                     shard_count=None):
        """Create a new graph in the database.

        An edge definition should look like this:

        .. code-block:: python

            {
                'name': 'edge_collection_name',
                'from_collections': ['from_vertex_collection_name'],
                'to_collections': ['to_vertex_collection_name']
            }

        :param name: The name of the new graph.
        :type name: str | unicode
        :param edge_definitions: The list of edge definitions.
        :type edge_definitions: list
        :param orphan_collections: The names of additional vertex collections.
        :type orphan_collections: list
        :param smart: Whether or not the graph is smart. Set this to ``True``
            to enable sharding (see parameter **smart_field** below). This
            only has an effect for the enterprise version of ArangoDB.
        :type smart: bool
        :param smart_field: The document field used to shard the vertices of
            the graph. To use this option, parameter **smart** must be set to
            ``True`` and every vertex in the graph must have the smart field.
        :type smart_field: str | unicode
        :param shard_count: The number of shards used for every collection in
            the graph. To use this option, parameter **smart** must be set to
            ``True`` and every vertex in the graph must have the smart field.
            This number cannot be modified later once set.
        :type shard_count: int
        :returns: the graph object
        :rtype: arango.graph.Graph
        :raises arango.exceptions.GraphCreateError: if the graph cannot be
            created in the database
        """

        data = {'name': name}
        if edge_definitions is not None:
            data['edgeDefinitions'] = [{
                'collection': definition['name'],
                'from': definition['from_collections'],
                'to': definition['to_collections']
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

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise GraphCreateError(res)
            return Graph(self._conn, name)

        return self.handle_request(request, handler)

    def delete_graph(self, name, ignore_missing=False, drop_collections=None):
        """Drop the graph of the given name from the database.

        :param name: The name of the graph to delete/drop.
        :type name: str | unicode
        :param ignore_missing: Ignore HTTP 404 (graph not found) from the
            server. If this is set to ``True`` an exception is not raised.
        :type ignore_missing: bool
        :param drop_collections: Whether to drop the collections of the graph
            as well. The collections can only be dropped if they are not in use
            by other graphs.
        :type drop_collections: bool
        :returns: Whether the deletion was successful.
        :rtype: bool
        :raises arango.exceptions.GraphDeleteError: if the graph cannot be
            deleted from the database
        """

        params = {}

        if drop_collections is not None:
            params['dropCollections'] = drop_collections

        request = Request(
            method='delete',
            endpoint='/_api/gharial/{}'.format(name),
            params=params
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                if not (res.status_code == 404 and ignore_missing):
                    raise GraphDeleteError(res)
            return not res.body['error']

        return self.handle_request(request, handler)

    ###################
    # Task Management #
    ###################

    def tasks(self):
        """Return all server tasks that are currently active.

        :returns: the server tasks that are currently active
        :rtype: [dict]
        :raises arango.exceptions.TaskListError: if the list of active server
            tasks cannot be retrieved from the server
        """

        request = Request(
            method='get',
            endpoint='/_api/tasks'
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise TaskListError(res)
            return res.body

        return self.handle_request(request, handler)

    def task(self, task_id):
        """Return the active server task with the given id.

        :param task_id: the ID of the server task
        :type task_id: str | unicode
        :returns: the details on the active server task
        :rtype: dict
        :raises arango.exceptions.TaskGetError: if the task cannot be retrieved
            from the server
        """

        request = Request(
            method='get',
            endpoint='/_api/tasks/{}'.format(task_id)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise TaskGetError(res)
            res.body.pop('code', None)
            res.body.pop('error', None)
            return res.body

        return self.handle_request(request, handler)

    # TODO verify which arguments are optional
    def create_task(self,
                    name,
                    command,
                    params=None,
                    period=None,
                    offset=None,
                    task_id=None):
        """Create a new server task.

        :param name: the name of the server task
        :type name: str | unicode
        :param command: the Javascript code to execute
        :type command: str | unicode
        :param params: the parameters passed into the command
        :type params: dict
        :param period: the number of seconds to wait between executions (if
            set to 0, the new task will be ``"timed"``, which means it will
            execute only once and be deleted automatically afterwards
        :type period: int
        :param offset: the initial delay before execution in seconds
        :type offset: int
        :param task_id: pre-defined ID for the new server task
        :type task_id: str | unicode
        :returns: the details on the new task
        :rtype: dict
        :raises arango.exceptions.TaskCreateError: if the task cannot be
            created on the server
        """
        data = {
            'name': name,
            'command': command
        }
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

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise TaskCreateError(res)
            res.body.pop('code', None)
            res.body.pop('error', None)
            return res.body

        return self.handle_request(request, handler)

    def delete_task(self, task_id, ignore_missing=False):
        """Delete the server task specified by ID.

        :param task_id: the ID of the server task
        :type task_id: str | unicode
        :param ignore_missing: ignore missing tasks
        :type ignore_missing: bool
        :returns: whether the deletion was successful
        :rtype: bool
        :raises arango.exceptions.TaskDeleteError: when the task cannot be
            deleted from the server
        """

        request = Request(
            method='delete',
            endpoint='/_api/tasks/{}'.format(task_id)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                if not (res.status_code == 404 and ignore_missing):
                    raise TaskDeleteError(res)
            return not res.body['error']

        return self.handle_request(request, handler)

    ###################
    # User Management #
    ###################

    def users(self):
        """Return the details of all users.

        :returns: the details of all users
        :rtype: [dict]
        :raises arango.exceptions.UserListError: if the retrieval fails
        """

        request = Request(
            method='get',
            endpoint='/_api/user'
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise UserListError(res)
            return [{
                'username': record['user'],
                'active': record['active'],
                'extra': record['extra'],
            } for record in res.body['result']]

        return self.handle_request(request, handler)

    def user(self, username):
        """Return the details of a user.

        :param username: the details of the user
        :type username: str | unicode
        :returns: the user details
        :rtype: dict
        :raises arango.exceptions.UserGetError: if the retrieval fails
        """

        request = Request(
            method='get',
            endpoint='/_api/user/{}'.format(username)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise UserGetError(res)
            return {
                'username': res.body['user'],
                'active': res.body['active'],
                'extra': res.body['extra']
            }

        return self.handle_request(request, handler)

    def create_user(self, username, password, active=None, extra=None):
        """Create a new user.

        :param username: the name of the user
        :type username: str | unicode
        :param password: the user's password
        :type password: str | unicode
        :param active: whether the user is active
        :type active: bool
        :param extra: any extra data on the user
        :type extra: dict
        :returns: the details of the new user
        :rtype: dict
        :raises arango.exceptions.UserCreateError: if the user create fails
        """

        data = {'user': username, 'passwd': password}
        if active is not None:
            data['active'] = active
        if extra is not None:
            data['extra'] = extra

        request = Request(
            method='post',
            endpoint='/_api/user',
            data=data
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise UserCreateError(res)
            return {
                'username': res.body['user'],
                'active': res.body['active'],
                'extra': res.body['extra'],
            }

        return self.handle_request(request, handler)

    def update_user(self, username, password=None, active=None, extra=None):
        """Update an existing user.

        :param username: the name of the existing user
        :type username: str | unicode
        :param password: the user's new password
        :type password: str | unicode
        :param active: whether the user is active
        :type active: bool
        :param extra: any extra data on the user
        :type extra: dict
        :returns: the details of the updated user
        :rtype: dict
        :raises arango.exceptions.UserUpdateError: if the user update fails
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

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise UserUpdateError(res)
            return {
                'username': res.body['user'],
                'active': res.body['active'],
                'extra': res.body['extra'],
            }

        return self.handle_request(request, handler)

    def replace_user(self, username, password, active=None, extra=None):
        """Replace an existing user.

        :param username: the name of the existing user
        :type username: str | unicode
        :param password: the user's new password
        :type password: str | unicode
        :param active: whether the user is active
        :type active: bool
        :param extra: any extra data on the user
        :type extra: dict
        :returns: the details of the replaced user
        :rtype: dict
        :raises arango.exceptions.UserReplaceError: if the user replace fails
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

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise UserReplaceError(res)
            return {
                'username': res.body['user'],
                'active': res.body['active'],
                'extra': res.body['extra'],
            }

        return self.handle_request(request, handler)

    def delete_user(self, username, ignore_missing=False):
        """Delete an existing user.

        :param username: the name of the existing user
        :type username: str | unicode
        :param ignore_missing: ignore missing users
        :type ignore_missing: bool
        :returns: ``True`` if the operation was successful, ``False`` if the
            user was missing but **ignore_missing** was set to ``True``
        :rtype: bool
        :raises arango.exceptions.UserDeleteError: if the user delete fails
        """

        request = Request(
            method='delete',
            endpoint='/_api/user/{user}'.format(user=username)
        )

        def handler(res):
            if res.status_code in HTTP_OK:
                return True
            elif res.status_code == 404 and ignore_missing:
                return False
            raise UserDeleteError(res)

        return self.handle_request(request, handler)

    def user_access(self, username, full=False):
        """Return a user's access details for databases (and collections).

        :param username: The name of the user.
        :type username: str | unicode
        :param full: Return the full set of access levels for all databases and
            collections for the user.
        :type full: bool
        :returns: The names of the databases (and collections) the user has
            access to, with their access levels
        :rtype: dict TODO CHANGED return structure due to mismatch with
        return from database
        :raises: arango.exceptions.UserAccessError: If the retrieval fails.
        """

        request = Request(
            method='get',
            endpoint='/_api/user/{}/database'.format(username),
            params={'full': full}
        )

        def handler(res):
            if res.status_code in HTTP_OK:
                return res.body['result']
            raise UserAccessError(res)

        return self.handle_request(request, handler)

    def grant_user_access(self, username, database=None):
        """Grant user access to the database.

        Appropriate permissions are required in order to execute this method.

        :param username: The name of the user.
        :type username: str | unicode
        :param database: The name of the database. If a name is not specified,
            the name of the current database is used.
        :type database: str | unicode
        :returns: Whether the operation was successful or not.
        :rtype: bool
        :raises arango.exceptions.UserGrantAccessError: If the operation fails.
        """

        if database is None:
            database = self.name

        request = Request(
            method='put',
            endpoint='/_api/user/{}/database/{}'.format(username, database),
            data={'grant': 'rw'}
        )

        def handler(res):
            if res.status_code in HTTP_OK:
                return True
            raise UserGrantAccessError(res)

        return self.handle_request(request, handler)

    def revoke_user_access(self, username, database=None):
        """Revoke user access to the database.

        Appropriate permissions are required in order to execute this method.

        :param username: The name of the user.
        :type username: str | unicode
        :param database: The name of the database. If a name is not specified,
            the name of the current database is used.
        :type database: str | unicode | unicode
        :returns: Whether the operation was successful or not.
        :rtype: bool
        :raises arango.exceptions.UserRevokeAccessError: If operation fails.
        """
        if database is None:
            database = self.name

        request = Request(
            method='delete',
            endpoint='/_api/user/{}/database/{}'.format(username, database)
        )

        def handler(res):
            if res.status_code in HTTP_OK:
                return True
            raise UserRevokeAccessError(res)

        return self.handle_request(request, handler)

    ########################
    # Async Job Management #
    ########################

    def async_jobs(self, status, count=None):
        """Return the IDs of asynchronous jobs with the specified status.

        :param status: The job status (``"pending"`` or ``"done"``).
        :type status: str | unicode
        :param count: The maximum number of job IDs to return.
        :type count: int
        :returns: The list of job IDs.
        :rtype: [str]
        :raises arango.exceptions.AsyncJobListError: If the retrieval fails.
        """

        params = {}

        if count is not None:
            params['count'] = count

        request = Request(
            method='get',
            endpoint='/_api/job/{}'.format(status),
            params=params
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise AsyncJobListError(res)
            return res.body

        return self.handle_request(request, handler)

    def clear_async_jobs(self, threshold=None):
        """Delete asynchronous job results from the server.

        :param threshold: If specified, only the job results created prior to
            the threshold (a unix timestamp) are deleted, otherwise *all* job
            results are deleted.
        :type threshold: int
        :returns: Whether the deletion of results was successful.
        :rtype: bool
        :raises arango.exceptions.AsyncJobClearError: If the operation fails.

        .. note::
            Async jobs currently queued or running are not stopped.
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

        def handler(res):
            if res.status_code in HTTP_OK:
                return True
            raise AsyncJobClearError(res)

        return self.handle_request(request, handler)

    ###############
    # Pregel Jobs #
    ###############

    def create_pregel_job(self,
                          algorithm,
                          graph,
                          store=None,
                          max_gss=None,
                          thread_count=None,
                          async_mode=None,
                          result_field=None,
                          algorithm_params=None):
        """Start/create a Pregel job.

        :param algorithm: The name of the algorithm (e.g. ``"pagerank"``).
        :type algorithm: str | unicode
        :param graph: The name of the graph.
        :type graph: str | unicode
        :param store: If set to ``True`` (default), the Pregel engine writes
            results back to the database. If set to ``False``, the results can
            be queried via AQL.
        :type store: bool
        :param max_gss: The maximum number of global iterations for the
            algorithm.
        :type max_gss: int
        :param thread_count: The number of parallel threads to use per worker.
            This does not influence the number of threads used to load or store
            data from the database (depends on the number of shards).
        :type thread_count: int
        :param async_mode: Algorithms which support async mode will run without
            synchronized global iterations. This might lead to performance
            increase if there are load imbalances.
        :type async_mode: bool
        :param result_field: If set, most algorithms write the result into
            this field.
        :type result_field: str | unicode
        :param algorithm_params: Algorithm specific parameters.
        :type algorithm_params: dict
        :returns: The ID of the Pregel job.
        :rtype: int
        :raises arango.exceptions.PregelJobCreateError: If the operation fails.

        """

        data = {
            'algorithm': algorithm,
            'graphName': graph,
        }

        if algorithm_params is None:
            algorithm_params = {}

        if store is not None:
            algorithm_params['store'] = store
        if max_gss is not None:
            algorithm_params['maxGSS'] = max_gss
        if thread_count is not None:
            algorithm_params['parallelism'] = thread_count
        if async_mode is not None:
            algorithm_params['async'] = async_mode
        if result_field is not None:
            algorithm_params['resultField'] = result_field
        if algorithm_params:
            data['params'] = algorithm_params

        request = Request(
            method='post',
            endpoint='/_api/control_pregel',
            data=data
        )

        def handler(res):
            if res.status_code in HTTP_OK:
                return res.body
            raise PregelJobCreateError(res)

        return self.handle_request(request, handler)

    def pregel_job(self, job_id):
        """Return the details of a Pregel job.

        :param job_id: The Pregel job ID.
        :type job_id: int
        :returns: The details of the Pregel job.
        :rtype: dict
        :raises arango.exceptions.PregelJobGetError: If the lookup fails.
        """

        request = Request(
            method='get',
            endpoint='/_api/control_pregel/{}'.format(job_id)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise PregelJobGetError(res)

            if 'edgeCount' in res.body:
                res.body['edge_count'] = res.body.pop('edgeCount')
            if 'receivedCount' in res.body:
                res.body['received_count'] = res.body.pop('receivedCount')
            if 'sendCount' in res.body:
                res.body['send_count'] = res.body.pop('sendCount')
            if 'totalRuntime' in res.body:
                res.body['total_runtime'] = res.body.pop('totalRuntime')
            if 'vertexCount' in res.body:
                res.body['vertex_count'] = res.body.pop('vertexCount')
            return res.body

        return self.handle_request(request, handler)

    def delete_pregel_job(self, job_id):
        """Cancel/delete a Pregel job.

        :param job_id: The Pregel job ID.
        :type job_id: int
        :returns: ``True`` if the Pregel job was successfully cancelled.
        :rtype: bool
        :raises arango.exceptions.PregelJobDeleteError: If the deletion fails.
        """

        request = Request(
            method='delete',
            endpoint='/_api/control_pregel/{}'.format(job_id)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise PregelJobDeleteError(res)
            return True

        return self.handle_request(request, handler)
