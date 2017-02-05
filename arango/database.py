from __future__ import absolute_import, unicode_literals

from arango.async import AsyncExecution
from arango.batch import BatchExecution
from arango.cluster import ClusterTest
from arango.collections import Collection
from arango.utils import HTTP_OK
from arango.exceptions import *
from arango.graph import Graph
from arango.transaction import Transaction
from arango.aql import AQL


class Database(object):
    """ArangoDB database.

    :param connection: ArangoDB database connection
    :type connection: arango.connection.Connection

    """

    def __init__(self, connection):
        self._conn = connection
        self._aql = AQL(self._conn)

    def __repr__(self):
        return '<ArangoDB database "{}">'.format(self._conn.database)

    def __getitem__(self, name):
        return self.collection(name)

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

    def async(self, return_result=True):
        """Return the asynchronous request object.

        Refer to :class:`arango.async.AsyncExecution` for more information.

        :param return_result: store and return the result
        :type return_result: bool
        :returns: the async request object
        :rtype: arango.async.AsyncExecution
        """
        return AsyncExecution(self._conn, return_result)

    def batch(self, return_result=True, commit_on_error=True):
        """Return the batch request object.

        Refer to :class:`arango.batch.BatchExecution` for more information.

        :param return_result: store and return the result
        :type return_result: bool
        :param commit_on_error: commit when an exception is raised
            (this is only applicable when context managers are used)
        :returns: the batch request object
        :rtype: arango.batch.BatchExecution
        """
        return BatchExecution(self._conn, return_result, commit_on_error)

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
        :type shard_id: str | unicode
        :param transaction_id: the transaction ID for the request
        :type transaction_id: str | unicode
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
        res = self._conn.get('/_api/database/current')
        if res.status_code not in HTTP_OK:
            raise DatabasePropertiesError(res)
        result = res.body['result']
        result['system'] = result.pop('isSystem')
        return result

    def get_document(self, id, rev=None, match_rev=True):
        """Retrieve a document by its ID (collection/key)

        :param id: the document ID
        :type id: str | unicode
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
        res = self._conn.get(
            '/_api/document/{}'.format(id),
            headers=(
                {'If-Match' if match_rev else 'If-None-Match': rev}
                if rev is not None else {}
            )
        )
        if res.status_code in {304, 412}:
            raise DocumentRevisionError(res)
        elif res.status_code == 404 and res.error_code == 1202:
            return None
        elif res.status_code in HTTP_OK:
            return res.body
        raise DocumentGetError(res)

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
        res = self._conn.get('/_api/collection')
        if res.status_code not in HTTP_OK:
            raise CollectionListError(res)
        return [{
            'id': col['id'],
            'name': col['name'],
            'system': col['isSystem'],
            'type': Collection.TYPES[col['type']],
            'status': Collection.STATUSES[col['status']],
        } for col in map(dict, res.body['result'])]

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
                          key_generator="traditional",
                          shard_fields=None,
                          shard_count=None,
                          index_bucket_count=None):
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
            'type': 3 if edge else 2,
            'keyOptions': key_options
        }
        if journal_size is not None:
            data['journalSize'] = journal_size
        if shard_count is not None:
            data['numberOfShards'] = shard_count
        if shard_fields is not None:
            data['shardKeys'] = shard_fields
        if index_bucket_count is not None:
            data['indexBuckets'] = index_bucket_count

        res = self._conn.post('/_api/collection', data=data)
        if res.status_code not in HTTP_OK:
            raise CollectionCreateError(res)
        return self.collection(name)

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
        res = self._conn.delete(
            '/_api/collection/{}'.format(name),
            params={'isSystem': system}
            if system is not None else None  # pragma: no cover
        )
        if res.status_code not in HTTP_OK:
            if not (res.status_code == 404 and ignore_missing):
                raise CollectionDeleteError(res)
        return not res.body['error']

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
        res = self._conn.get('/_api/gharial')
        if res.status_code not in HTTP_OK:
            raise GraphListError(res)
        return [
            {
                'name': graph['_key'],
                'revision': graph['_rev'],
                'edge_definitions': graph['edgeDefinitions'],
                'orphan_collections': graph['orphanCollections']
            } for graph in map(dict, res.body['graphs'])
        ]

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
                     orphan_collections=None):
        """Create a new graph in the database.

        An edge definition should look like this:

        .. code-block:: python

            {
                'name': 'edge_collection_name',
                'from_collections': ['from_vertex_collection_name'],
                'to_collections': ['to_vertex_collection_name']
            }

        :param name: name of the new graph
        :type name: str | unicode
        :param edge_definitions: list of edge definitions
        :type edge_definitions: list
        :param orphan_collections: names of additional vertex collections
        :type orphan_collections: list
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

        res = self._conn.post('/_api/gharial', data=data)
        if res.status_code not in HTTP_OK:
            raise GraphCreateError(res)
        return Graph(self._conn, name)

    def delete_graph(self, name, ignore_missing=False):
        """Drop the graph of the given name from the database.

        :param name: the name of the graph to delete
        :type name: str | unicode
        :param ignore_missing: ignore HTTP 404
        :type ignore_missing: bool
        :returns: whether the drop was successful
        :rtype: bool
        :raises arango.exceptions.GraphDeleteError: if the graph cannot be
            deleted from the database
        """
        res = self._conn.delete('/_api/gharial/{}'.format(name))
        if res.status_code not in HTTP_OK:
            if not (res.status_code == 404 and ignore_missing):
                raise GraphDeleteError(res)
        return not res.body['error']

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
        res = self._conn.get('/_api/tasks')
        if res.status_code not in HTTP_OK:
            raise TaskListError(res)
        return res.body

    def task(self, task_id):
        """Return the active server task with the given id.

        :param task_id: the ID of the server task
        :type task_id: str | unicode
        :returns: the details on the active server task
        :rtype: dict
        :raises arango.exceptions.TaskGetError: if the task cannot be retrieved
            from the server
        """
        res = self._conn.get('/_api/tasks/{}'.format(task_id))
        if res.status_code not in HTTP_OK:
            raise TaskGetError(res)
        res.body.pop('code', None)
        res.body.pop('error', None)
        return res.body

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
            'command': command,
            'params': params if params else {},
        }
        if task_id is not None:
            data['id'] = task_id
        if period is not None:
            data['period'] = period
        if offset is not None:
            data['offset'] = offset
        res = self._conn.post(
            '/_api/tasks/{}'.format(task_id if task_id else ''),
            data=data
        )
        if res.status_code not in HTTP_OK:
            raise TaskCreateError(res)
        res.body.pop('code', None)
        res.body.pop('error', None)
        return res.body

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
        res = self._conn.delete('/_api/tasks/{}'.format(task_id))
        if res.status_code not in HTTP_OK:
            if not (res.status_code == 404 and ignore_missing):
                raise TaskDeleteError(res)
        return not res.body['error']
