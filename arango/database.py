from __future__ import absolute_import, unicode_literals

from arango.async import AsyncExecution
from arango.batch import BatchExecution
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
    def name(self):
        """Return the name of the database.

        :returns: the name of the database
        :rtype: str
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
        :type read: str | list
        :param write: the name(s) of the collection(s) to write to
        :type write: str | list
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

    def properties(self):
        """Return the database properties.

        :returns: the database properties
        :rtype: dict
        :raises arango.exceptions.DatabaseGetPropertiesError: if the properties
            of the database cannot be retrieved
        """
        res = self._conn.get('/_api/database/current')
        if res.status_code not in HTTP_OK:
            raise DatabaseGetPropertiesError(res)
        result = res.body['result']
        result['system'] = result.pop('isSystem')
        return result

    #########################
    # Collection Management #
    #########################

    def collections(self):
        """Return the collections in the database.

        :returns: the details of the collections in the database
        :rtype: list
        :raises arango.exceptions.CollectionsListError: if the list of
            collections cannot be retrieved
        """
        res = self._conn.get('/_api/collection')
        if res.status_code not in HTTP_OK:
            raise CollectionsListError(res)
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
        :type name: str
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

        :param name: the name of the collection
        :type name: str
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
        :type key_generator: str
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

    def delete_collection(self, name, ignore_missing=False):
        """Delete a collection.

        :param name: the name of the collection to delete
        :type name: str
        :param ignore_missing: do not raise if the collection is missing
        :type ignore_missing: bool
        :returns: whether the deletion was successful
        :rtype: bool
        :raises arango.exceptions.CollectionDeleteError: if the collection
            cannot be deleted from the database
        """
        res = self._conn.delete('/_api/collection/{}'.format(name))
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
        :raises arango.exceptions.GraphsListError: if the list of graphs
            cannot be retrieved
        """
        res = self._conn.get('/_api/gharial')
        if res.status_code not in HTTP_OK:
            raise GraphsListError(res)
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
        :type name: str
        :returns: the requested graph object
        :rtype: arango.graph.Graph
        """
        return Graph(self._conn, name)

    def create_graph(self,
                     name,
                     edge_definitions=None,
                     orphan_collections=None):
        """Create a new graph in the database.

        :param name: name of the new graph
        :type name: str
        :param edge_definitions: definitions for edges
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
            data['edgeDefinitions'] = edge_definitions
        if orphan_collections is not None:
            data['orphanCollections'] = orphan_collections

        res = self._conn.post('/_api/gharial', data=data)
        if res.status_code not in HTTP_OK:
            raise GraphCreateError(res)
        return Graph(self._conn, name)

    def delete_graph(self, name, ignore_missing=False):
        """Drop the graph of the given name from the database.

        :param name: the name of the graph to delete
        :type name: str
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
        :raises arango.exceptions.TasksListError: if the list of active server
            tasks cannot be retrieved from the server
        """
        res = self._conn.get('/_api/tasks')
        if res.status_code not in HTTP_OK:
            raise TasksListError(res)
        return res.body

    def task(self, task_id):
        """Return the active server task with the given id.

        :param task_id: the ID of the server task
        :type task_id: str
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
        :type name: str
        :param command: the Javascript code to execute
        :type command: str
        :param params: the parameters passed into the command
        :type params: dict
        :param period: the number of seconds to wait between executions (if
            set to 0, the new task will be ``"timed"``, which means it will
            execute only once and be deleted automatically afterwards
        :type period: int
        :param offset: the initial delay before execution in seconds
        :type offset: int
        :param task_id: pre-defined ID for the new server task
        :type task_id: str
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
        :type task_id: str
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
