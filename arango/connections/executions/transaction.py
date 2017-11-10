from __future__ import absolute_import, unicode_literals

from uuid import uuid4
from collections import deque

from arango.connections import BaseConnection
from arango.request import Request
from arango.utils import HTTP_OK
from arango.exceptions import TransactionError


class TransactionExecution(BaseConnection):
    """ArangoDB transaction object.

    API requests made in a transaction are queued in memory and executed as a
    whole in a single HTTP call to ArangoDB server.

    :param connection: ArangoDB database connection
    :type connection: arango.connection.Connection
    :param read: the name(s) of the collection(s) to read from
    :type read: str | unicode | list
    :param write: the name(s) of the collection(s) to write to
    :type write: str | unicode | list
    :param sync: wait for the operation to sync to disk
    :type sync: bool
    :param timeout: timeout on the collection locks
    :type timeout: int
    :param commit_on_error: only applicable when *context managers* are used
        to execute the transaction: if ``True``, the requests queued so
        far are committed even if an exception is raised before exiting out of
        the context
    :type commit_on_error: bool

    .. note::
        Only writes are possible at the moment in a transaction.
    """

    def __init__(self,
                 connection,
                 read=None,
                 write=None,
                 sync=None,
                 timeout=None,
                 commit_on_error=False):
        super(TransactionExecution, self).__init__(
            protocol=connection.protocol,
            host=connection.host,
            port=connection.port,
            username=connection.username,
            password=connection.password,
            http_client=connection.http_client,
            database=connection.database,
            enable_logging=connection.logging_enabled
        )
        self._id = uuid4().hex
        self._actions = []
        self._collections = {}
        if read:
            self._collections['read'] = read
        if write:
            self._collections['write'] = write
        self._timeout = timeout
        self._sync = sync
        self._commit_on_error = commit_on_error
        self._type = 'transaction'

        self._parent = connection

    def __repr__(self):
        return '<ArangoDB transaction {}>'.format(self._id)

    def __enter__(self):
        return self

    def __exit__(self, exception, *_):
        if exception is None or self._commit_on_error:
            return self.commit()

    @property
    def id(self):
        """Return the UUID of the transaction.

        :return: the UUID of the transaction
        :rtype: str | unicode
        """
        return self._id

    def handle_request(self, request, handler, **kwargs):
        """Handle the incoming request and response handler.

        :param request: the API request queued as part of the transaction, and
            executed only when the current transaction is committed via method
            :func:`arango.batch.BatchExecution.commit`
        :type request: arango.request.Request
        :param handler: the response handler
        :type handler: callable
        """
        if request.command is None:
            raise TransactionError('unsupported method')
        self._actions.append(request.command)

    def execute(self, command, params=None, sync=None, timeout=None):
        """Execute raw Javascript code in a transaction.

        :param command: the raw Javascript code
        :type command: str | unicode
        :param params: optional arguments passed into the code
        :type params: dict
        :param sync: wait for the operation to sync to disk (overrides the
            value specified during the transaction object instantiation)
        :type sync: bool
        :param timeout: timeout on the collection locks (overrides the value
            value specified during the transaction object instantiation)
        :type timeout: int
        :return: the result of the transaction
        :rtype: dict
        :raises arango.exceptions.TransactionError: if the transaction cannot
            be executed
        """

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise TransactionError(res)
            return res.body.get('result')

        data = {'collections': self._collections, 'action': command}

        if timeout is None:
            timeout = self._timeout

        if timeout is not None:
            data['lockTimeout'] = timeout

        if sync is None:
            sync = self._sync

        if sync is not None:
            data['waitForSync'] = sync

        if params is not None:
            data['params'] = params

        request = Request(
            method='post',
            url='/_api/transaction',
            data=data
        )

        return self.underlying.handle_request(request, handler)

    def commit(self):
        """Execute the queued API requests in a single atomic step.

        :return: the result of the transaction
        :rtype: :class:arango.jobs.Job
        :raises arango.exceptions.TransactionError: if the transaction cannot
            be executed
        """

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise TransactionError(res)
            return res.body.get('result')

        action_labels = ["a" + uuid4().hex for _ in self._actions]

        action_strings = deque()
        action_strings.append('db = require("internal").db;\n')

        for i in range(len(self._actions)):
            action_strings.append("var ")
            action_strings.append(action_labels[i])
            action_strings.append(" = ")
            action_strings.append(self._actions[i])
            action_strings.append(";\n")

        action_strings.append("return [")
        for label in action_labels:
            action_strings.append(label)
            action_strings.append(", ")

        if len(action_labels) > 0:
            action_strings.pop()

        action_strings.append("];\n")

        action = "".join(action_strings)

        request = Request(
            method='post',
            url='/_api/transaction',
            data={
                'collections': self._collections,
                'action': 'function () {{ {} }}'.format(action)
            },
            params={
                'lockTimeout': self._timeout,
                'waitForSync': self._sync,
            }
        )

        self._actions = ['db = require("internal").db']

        return self.underlying.handle_request(request, handler)
