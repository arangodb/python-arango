from __future__ import absolute_import, unicode_literals

from arango import Request
from arango.utils import HTTP_OK
from arango.exceptions import (
    WALFlushError,
    WALPropertiesError,
    WALConfigureError,
    WALTransactionListError
)
from arango import APIWrapper


class WriteAheadLog(APIWrapper):
    """ArangoDB write-ahead log object.

    :param connection: ArangoDB database connection
    :type connection: arango.connection.Connection

    .. note::
        This class is designed to be instantiated internally only.
    """

    def __init__(self, connection):
        APIWrapper.__init__(self, connection)

    def __repr__(self):
        return "<ArangoDB write-ahead log>"

    def properties(self):
        """Return the configuration of the write-ahead log.

        :returns: the configuration of the write-ahead log
        :rtype: dict
        :raises arango.exceptions.WALPropertiesError: if the WAL properties
            cannot be retrieved from the server
        """
        request = Request(
            method='get',
            url='/_admin/wal/properties'
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise WALPropertiesError(res)
            return {
                'oversized_ops': res.body.get('allowOversizeEntries'),
                'log_size': res.body.get('logfileSize'),
                'historic_logs': res.body.get('historicLogfiles'),
                'reserve_logs': res.body.get('reserveLogfiles'),
                'sync_interval': res.body.get('syncInterval'),
                'throttle_wait': res.body.get('throttleWait'),
                'throttle_limit': res.body.get('throttleWhenPending')
            }

        response = self.handle_request(request, handler)

        return response

    def configure(self, oversized_ops=None, log_size=None, historic_logs=None,
                  reserve_logs=None, throttle_wait=None, throttle_limit=None):
        """Configure the parameters of the write-ahead log.

        :param oversized_ops: execute and store ops bigger than a log file
        :type oversized_ops: bool
        :param log_size: the size of each write-ahead log file
        :type log_size: int
        :param historic_logs: the number of historic log files to keep
        :type historic_logs: int
        :param reserve_logs: the number of reserve log files to allocate
        :type reserve_logs: int
        :param throttle_wait: wait time before aborting when throttled (in ms)
        :type throttle_wait: int
        :param throttle_limit: number of pending gc ops before write-throttling
        :type throttle_limit: int
        :returns: the new configuration of the write-ahead log
        :rtype: dict
        :raises arango.exceptions.WALPropertiesError: if the WAL properties
            cannot be modified
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
            url='/_admin/wal/properties',
            data=data
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise WALConfigureError(res)
            return {
                'oversized_ops': res.body.get('allowOversizeEntries'),
                'log_size': res.body.get('logfileSize'),
                'historic_logs': res.body.get('historicLogfiles'),
                'reserve_logs': res.body.get('reserveLogfiles'),
                'sync_interval': res.body.get('syncInterval'),
                'throttle_wait': res.body.get('throttleWait'),
                'throttle_limit': res.body.get('throttleWhenPending')
            }

        response = self.handle_request(request, handler)

        return response

    def transactions(self):
        """Return details on currently running transactions.

        Fields in the returned dictionary:

        - *last_collected*: the ID of the last collected log file (at the \
        start of each running transaction) or ``None`` if no transactions are \
        running

        - *last_sealed*: the ID of the last sealed log file (at the start \
        of each running transaction) or ``None`` if no transactions are \
        running

        - *count*: the number of current running transactions

        :returns: the information about the currently running transactions
        :rtype: dict
        :raises arango.exceptions.WALTransactionListError: if the details on
            the transactions cannot be retrieved
        """

        request = Request(
            method='get',
            url='/_admin/wal/transactions'
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise WALTransactionListError(res)
            return {
                'last_collected': res.body['minLastCollected'],
                'last_sealed': res.body['minLastSealed'],
                'count': res.body['runningTransactions']
            }

        response = self.handle_request(request, handler)

        return response

    def flush(self, sync=True, garbage_collect=True):
        """Flush the write-ahead log to collection journals and data files.

        :param sync: block until data is synced to disk
        :type sync: bool
        :param garbage_collect: block until flushed data is garbage collected
        :type garbage_collect: bool
        :returns: whether the write-ahead log was flushed successfully
        :rtype: bool
        :raises arango.exceptions.WALFlushError: it the WAL cannot
            be flushed
        """
        data = {
            'waitForSync': sync,
            'waitForCollector': garbage_collect
        }

        request = Request(
            method='put',
            url='/_admin/wal/flush',
            data=data
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise WALFlushError(res)
            return not res.body.get('error')

        response = self.handle_request(request, handler)

        return response
