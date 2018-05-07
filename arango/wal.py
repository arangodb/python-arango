from __future__ import absolute_import, unicode_literals

__all__ = ['WAL']

from arango.api import APIWrapper
from arango.exceptions import (
    WALFlushError,
    WALPropertiesError,
    WALConfigureError,
    WALTransactionListError
)
from arango.request import Request


class WAL(APIWrapper):
    """WAL (Write-Ahead Log) API wrapper.

    :param connection: HTTP connection.
    :type connection: arango.connection.Connection
    :param executor: API executor.
    :type executor: arango.executor.Executor
    """

    def __init__(self, connection, executor):
        super(WAL, self).__init__(connection, executor)

    # noinspection PyMethodMayBeStatic
    def _format_properties(self, body):
        """Format WAL properties.

        :param body: Response body.
        :type body: dict
        :return: Formatted body.
        :rtype: dict
        """
        if 'allowOversizeEntries' in body:
            body['oversized_ops'] = body.pop('allowOversizeEntries')
        if 'logfileSize' in body:
            body['log_size'] = body.pop('logfileSize')
        if 'historicLogfiles' in body:
            body['historic_logs'] = body.pop('historicLogfiles')
        if 'reserveLogfiles' in body:
            body['reserve_logs'] = body.pop('reserveLogfiles')
        if 'syncInterval' in body:
            body['sync_interval'] = body.pop('syncInterval')
        if 'throttleWait' in body:
            body['throttle_wait'] = body.pop('throttleWait')
        if 'throttleWhenPending' in body:
            body['throttle_limit'] = body.pop('throttleWhenPending')
        return body

    def properties(self):
        """Return WAL properties.

        :return: WAL properties.
        :rtype: dict
        :raise arango.exceptions.WALPropertiesError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_admin/wal/properties'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise WALPropertiesError(resp, request)
            return self._format_properties(resp.body)

        return self._execute(request, response_handler)

    def configure(self,
                  oversized_ops=None,
                  log_size=None,
                  historic_logs=None,
                  reserve_logs=None,
                  throttle_wait=None,
                  throttle_limit=None):
        """Configure WAL properties.

        :param oversized_ops: If set to True, operations bigger than a single
            log file are allowed to be executed and stored.
        :type oversized_ops: bool
        :param log_size: Size of each write-ahead log file in bytes.
        :type log_size: int
        :param historic_logs: Max number of historic log files to keep.
        :type historic_logs: int
        :param reserve_logs: Max number of reserve log files to allocate.
        :type reserve_logs: int
        :param throttle_wait: Wait time before aborting when write-throttled
            in milliseconds.
        :type throttle_wait: int
        :param throttle_limit: Number of pending garbage collector operations
            that, when reached, activates write-throttling. Value of 0 means
            no throttling is triggered.
        :type throttle_limit: int
        :return: New WAL properties.
        :rtype: dict
        :raise arango.exceptions.WALConfigureError: If operation fails.
        """
        data = {}
        if oversized_ops is not None:
            data['allowOversizeEntries'] = oversized_ops
        if log_size is not None:
            data['logfileSize'] = log_size
        if historic_logs is not None:
            data['historicLogfiles'] = historic_logs
        if reserve_logs is not None:
            data['reserveLogfiles'] = reserve_logs
        if throttle_wait is not None:
            data['throttleWait'] = throttle_wait
        if throttle_limit is not None:
            data['throttleWhenPending'] = throttle_limit

        request = Request(
            method='put',
            endpoint='/_admin/wal/properties',
            data=data
        )

        def response_handler(resp):
            if not resp.is_success:
                raise WALConfigureError(resp, request)
            return self._format_properties(resp.body)

        return self._execute(request, response_handler)

    def transactions(self):
        """Return details on currently running WAL transactions.

        Fields in the returned details are as follows:

        .. code-block:: none

            "last_collected"    : ID of the last collected log file (at the
                                  start of each running transaction) or None
                                  if no transactions are running.

            "last_sealed"       : ID of the last sealed log file (at the start
                                  of each running transaction) or None if no
                                  transactions are running.

            "count"             : Number of currently running transactions.

        :return: Details on currently running WAL transactions.
        :rtype: dict
        :raise arango.exceptions.WALTransactionListError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_admin/wal/transactions'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise WALTransactionListError(resp, request)
            if 'minLastCollected' in resp.body:
                resp.body['last_collected'] = resp.body.pop('minLastCollected')
            if 'minLastSealed' in resp.body:
                resp.body['last_sealed'] = resp.body.pop('minLastSealed')
            if 'runningTransactions' in resp.body:
                resp.body['count'] = resp.body.pop('runningTransactions')
            return resp.body

        return self._execute(request, response_handler)

    def flush(self, sync=True, garbage_collect=True):
        """Synchronize WAL to disk.

        :param sync: Block until the synchronization is complete.
        :type sync: bool
        :param garbage_collect: Block until flushed data is garbage collected.
        :type garbage_collect: bool
        :return: True if WAL was flushed successfully.
        :rtype: bool
        :raise arango.exceptions.WALFlushError: If flush operation fails.
        """
        request = Request(
            method='put',
            endpoint='/_admin/wal/flush',
            params={
                'waitForSync': sync,
                'waitForCollector': garbage_collect
            }
        )

        def response_handler(resp):
            if not resp.is_success:
                raise WALFlushError(resp, request)
            return True

        return self._execute(request, response_handler)
