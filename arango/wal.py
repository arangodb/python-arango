__all__ = ["WAL"]

from typing import Optional

from arango.api import ApiGroup
from arango.exceptions import (
    WALConfigureError,
    WALFlushError,
    WALLastTickError,
    WALPropertiesError,
    WALTailError,
    WALTickRangesError,
    WALTransactionListError,
)
from arango.formatter import (
    format_replication_header,
    format_tick_values,
    format_wal_properties,
    format_wal_transactions,
)
from arango.request import Request
from arango.response import Response
from arango.result import Result
from arango.typings import Json, Params


class WAL(ApiGroup):  # pragma: no cover
    """WAL (Write-Ahead Log) API wrapper."""

    def properties(self) -> Result[Json]:
        """Return WAL properties.

        :return: WAL properties.
        :rtype: dict
        :raise arango.exceptions.WALPropertiesError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_admin/wal/properties")

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_wal_properties(resp.body)
            raise WALPropertiesError(resp, request)

        return self._execute(request, response_handler)

    def configure(
        self,
        oversized_ops: Optional[bool] = None,
        log_size: Optional[int] = None,
        historic_logs: Optional[int] = None,
        reserve_logs: Optional[int] = None,
        throttle_wait: Optional[int] = None,
        throttle_limit: Optional[int] = None,
    ) -> Result[Json]:
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
        data: Json = {}
        if oversized_ops is not None:
            data["allowOversizeEntries"] = oversized_ops
        if log_size is not None:
            data["logfileSize"] = log_size
        if historic_logs is not None:
            data["historicLogfiles"] = historic_logs
        if reserve_logs is not None:
            data["reserveLogfiles"] = reserve_logs
        if throttle_wait is not None:
            data["throttleWait"] = throttle_wait
        if throttle_limit is not None:
            data["throttleWhenPending"] = throttle_limit

        request = Request(method="put", endpoint="/_admin/wal/properties", data=data)

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_wal_properties(resp.body)
            raise WALConfigureError(resp, request)

        return self._execute(request, response_handler)

    def transactions(self) -> Result[Json]:
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
        request = Request(method="get", endpoint="/_admin/wal/transactions")

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_wal_transactions(resp.body)
            raise WALTransactionListError(resp, request)

        return self._execute(request, response_handler)

    def flush(self, sync: bool = True, garbage_collect: bool = True) -> Result[bool]:
        """Synchronize WAL to disk.

        :param sync: Block until the synchronization is complete.
        :type sync: bool | None
        :param garbage_collect: Block until flushed data is garbage collected.
        :type garbage_collect: bool
        :return: True if WAL was flushed successfully.
        :rtype: bool
        :raise arango.exceptions.WALFlushError: If flush operation fails.
        """
        request = Request(
            method="put",
            endpoint="/_admin/wal/flush",
            params={"waitForSync": sync, "waitForCollector": garbage_collect},
        )

        def response_handler(resp: Response) -> bool:
            if resp.is_success:
                return True
            raise WALFlushError(resp, request)

        return self._execute(request, response_handler)

    def tick_ranges(self) -> Result[Json]:
        """Return the available ranges of tick values for all WAL files.

        :return: Ranges of tick values.
        :rtype: dict
        :raise arango.exceptions.WALTickRangesError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/wal/range")

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_tick_values(resp.body)
            raise WALTickRangesError(resp, request)

        return self._execute(request, response_handler)

    def last_tick(self) -> Result[Json]:
        """Return the last available tick value (last successful operation).

        :return: Last tick value in the WAL.
        :rtype: dict
        :raise arango.exceptions.WALLastTickError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/wal/lastTick")

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_tick_values(resp.body)
            raise WALLastTickError(resp, request)

        return self._execute(request, response_handler)

    def tail(
        self,
        lower: Optional[str] = None,
        upper: Optional[str] = None,
        last_scanned: Optional[str] = None,
        all_databases: Optional[bool] = None,
        chunk_size: Optional[int] = None,
        syncer_id: Optional[int] = None,
        server_id: Optional[int] = None,
        client_info: Optional[str] = None,
        barrier_id: Optional[int] = None,
        deserialize: bool = False,
    ) -> Result[Json]:
        """Fetch recent WAL operations.

        :param lower: Exclusive lower bound tick value. On successive calls to
            this method you should set this to the value of "last_included"
            from previous call (unless the value was 0).
        :type lower: str | None
        :param upper: Inclusive upper bound tick value for results.
        :type upper: str | None
        :param last_scanned: On successive calls to this method you should
            set this to the value of "last_scanned" from previous call (or 0
            on first try). This allows the rocksdb engine to break up large
            transactions over multiple responses.
        :type last_scanned: str | None
        :param all_databases: Whether operations for all databases should be
            included. When set to False only the operations for the current
            database are included. The value True is only valid on "_system"
            database. The default is False.
        :type all_databases: bool | None
        :param chunk_size: Approximate maximum size of the returned result.
        :type chunk_size: int | None
        :param syncer_id: ID of the client used to tail results. The server
            will use this to keep operations until the client has fetched them.
            Must be a positive integer. Note this or **server_id** is required
            to have a chance at fetching reading all operations with the
            rocksdb storage engine.
        :type syncer_id: int | None
        :param server_id: ID of the client machine. If unset, the server will
            use this to keep operations until the client has fetched them. Must
            be a positive integer. Note this or **syncer_id** is required to
            have a chance at fetching reading all operations with the rocksdb
            storage engine.
        :type server_id: int | None
        :param client_info: Short description of the client, used for
            informative purposes only.
        :type client_info: str | None
        :param barrier_id: ID of barrier used to keep WAL entries around.
        :type barrier_id: int | None
        :param deserialize: Deserialize the response content. Default is False.
        :type deserialize: bool
        :return: If **deserialize** is set to False, content is returned raw as
            a string. If **deserialize** is set to True, it is deserialized and
            returned as a list of dictionaries.
        :rtype: dict
        :raise arango.exceptions.WALTailError: If tail operation fails.
        """
        params: Params = {}
        if lower is not None:
            params["from"] = lower
        if upper is not None:
            params["to"] = upper
        if last_scanned is not None:
            params["lastScanned"] = last_scanned
        if all_databases is not None:
            params["global"] = all_databases
        if chunk_size is not None:
            params["chunkSize"] = chunk_size
        if syncer_id is not None:
            params["syncerId"] = syncer_id
        if server_id is not None:
            params["serverId"] = server_id
        if client_info is not None:
            params["clientInfo"] = client_info
        if barrier_id is not None:
            params["barrierId"] = barrier_id

        request = Request(
            method="get", endpoint="/_api/wal/tail", params=params, deserialize=False
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                result = format_replication_header(resp.headers)
                result["content"] = (
                    [
                        self._conn.deserialize(line)
                        for line in resp.body.split("\n")
                        if line
                    ]
                    if deserialize
                    else resp.body
                )
                return result

            raise WALTailError(resp, request)

        return self._execute(request, response_handler)
