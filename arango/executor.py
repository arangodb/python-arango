__all__ = [
    "ApiExecutor",
    "DefaultApiExecutor",
    "AsyncApiExecutor",
    "BatchApiExecutor",
    "TransactionApiExecutor",
    "OverloadControlApiExecutor",
]

from collections import OrderedDict
from typing import Any, Callable, Optional, Sequence, Tuple, TypeVar, Union
from urllib.parse import urlencode
from uuid import uuid4

from arango.connection import Connection
from arango.exceptions import (
    AsyncExecuteError,
    BatchExecuteError,
    BatchStateError,
    OverloadControlExecutorError,
    TransactionAbortError,
    TransactionCommitError,
    TransactionInitError,
    TransactionStatusError,
)
from arango.job import AsyncJob, BatchJob
from arango.request import Request
from arango.response import Response
from arango.typings import Fields, Json
from arango.utils import suppress_warning

ApiExecutor = Union[
    "DefaultApiExecutor",
    "AsyncApiExecutor",
    "BatchApiExecutor",
    "TransactionApiExecutor",
    "OverloadControlApiExecutor",
]

T = TypeVar("T")


class DefaultApiExecutor:
    """Default API executor.

    :param connection: HTTP connection.
    :type connection: arango.connection.BasicConnection |
        arango.connection.JwtConnection | arango.connection.JwtSuperuserConnection
    """

    def __init__(self, connection: Connection) -> None:
        self._conn = connection

    @property
    def context(self) -> str:
        return "default"

    def execute(self, request: Request, response_handler: Callable[[Response], T]) -> T:
        """Execute an API request and return the result.

        :param request: HTTP request.
        :type request: arango.request.Request
        :param response_handler: HTTP response handler.
        :type response_handler: callable
        :return: API execution result.
        """
        resp = self._conn.send_request(request)
        return response_handler(resp)


class AsyncApiExecutor:
    """Async API Executor.

    :param connection: HTTP connection.
    :type connection: arango.connection.BasicConnection |
        arango.connection.JwtConnection | arango.connection.JwtSuperuserConnection
    :param return_result: If set to True, API executions return instances of
        :class:`arango.job.AsyncJob` and results can be retrieved from server
        once available. If set to False, API executions return None and no
        results are stored on server.
    :type return_result: bool
    """

    def __init__(self, connection: Connection, return_result: bool) -> None:
        self._conn = connection
        self._return_result = return_result

    @property
    def context(self) -> str:
        return "async"

    def execute(
        self, request: Request, response_handler: Callable[[Response], T]
    ) -> Optional[AsyncJob[T]]:
        """Execute an API request asynchronously.

        :param request: HTTP request.
        :type request: arango.request.Request
        :param response_handler: HTTP response handler.
        :type response_handler: callable
        :return: Async job or None if **return_result** parameter was set to
            False during initialization.
        :rtype: arango.job.AsyncJob | None
        """
        if self._return_result:
            request.headers["x-arango-async"] = "store"
        else:
            request.headers["x-arango-async"] = "true"

        resp = self._conn.send_request(request)
        if not resp.is_success:
            raise AsyncExecuteError(resp, request)
        if not self._return_result:
            return None

        job_id = resp.headers["x-arango-async-id"]
        return AsyncJob(self._conn, job_id, response_handler)


class BatchApiExecutor:
    """Batch API executor.

    :param connection: HTTP connection.
    :param return_result: If set to True, API executions return instances of
        :class:`arango.job.BatchJob` that are populated with results on commit.
        If set to False, API executions return None and no results are tracked
        client-side.
    :type return_result: bool
    """

    def __init__(self, connection: Connection, return_result: bool) -> None:
        self._conn = connection
        self._return_result: bool = return_result
        self._queue: OrderedDict[str, Tuple[Request, BatchJob[Any]]] = OrderedDict()
        self._committed: bool = False

    @property
    def context(self) -> str:
        return "batch"

    def _stringify_request(self, request: Request) -> str:
        path = request.endpoint

        if request.params is not None:
            path += f"?{urlencode(request.params)}"
        buffer = [f"{request.method} {path} HTTP/1.1"]

        if request.headers is not None:
            for key, value in sorted(request.headers.items()):
                buffer.append(f"{key}: {value}")

        if request.data is not None:
            serialized = self._conn.serialize(request.data)
            buffer.append("\r\n" + serialized)

        return "\r\n".join(buffer)

    @property
    def jobs(self) -> Optional[Sequence[BatchJob[Any]]]:
        """Return the queued batch jobs.

        :return: Batch jobs or None if **return_result** parameter was set to
            False during initialization.
        :rtype: [arango.job.BatchJob] | None
        """
        if not self._return_result:
            return None
        return [job for _, job in self._queue.values()]

    def execute(
        self, request: Request, response_handler: Callable[[Response], T]
    ) -> Optional[BatchJob[T]]:
        """Place the request in the batch queue.

        :param request: HTTP request.
        :type request: arango.request.Request
        :param response_handler: HTTP response handler.
        :type response_handler: callable
        :return: Batch job or None if **return_result** parameter was set to
            False during initialization.
        :rtype: arango.job.BatchJob | None
        :raise arango.exceptions.BatchStateError: If batch was already
            committed.
        """
        if self._committed:
            raise BatchStateError("batch already committed")

        job = BatchJob(response_handler)
        self._queue[job.id] = (request, job)
        return job if self._return_result else None

    def commit(self) -> Optional[Sequence[BatchJob[Any]]]:
        """Execute the queued requests in a single batch API request.

        If **return_result** parameter was set to True during initialization,
        :class:`arango.job.BatchJob` instances are populated with results.

        :return: Batch jobs or None if **return_result** parameter was set to
            False during initialization.
        :rtype: [arango.job.BatchJob] | None
        :raise arango.exceptions.BatchStateError: If batch state is invalid
            (e.g. batch was already committed or size of response from server
            did not match the expected).
        :raise arango.exceptions.BatchExecuteError: If commit fails.
        """
        if self._committed:
            raise BatchStateError("batch already committed")
        else:
            self._committed = True

        if len(self._queue) == 0:
            return self.jobs

        # Boundary used for multipart request
        boundary = uuid4().hex

        # Build the batch request payload
        buffer = []
        for req, job in self._queue.values():
            buffer.append(f"--{boundary}")
            buffer.append("Content-Type: application/x-arango-batchpart")
            buffer.append(f"Content-Id: {job.id}")
            buffer.append("\r\n" + self._stringify_request(req))
        buffer.append(f"--{boundary}--")

        request = Request(
            method="post",
            endpoint="/_api/batch",
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            data="\r\n".join(buffer),
        )
        with suppress_warning("requests.packages.urllib3.connectionpool"):
            resp = self._conn.send_request(request)

        if not resp.is_success:
            raise BatchExecuteError(resp, request)

        if not self._return_result:
            return None

        url_prefix = resp.url.strip("/_api/batch")
        raw_responses = resp.raw_body.split(f"--{boundary}")[1:-1]

        if len(self._queue) != len(raw_responses):
            raise BatchStateError(
                "expecting {} parts in batch response but got {}".format(
                    len(self._queue), len(raw_responses)
                )
            )
        for raw_resp in raw_responses:
            # Parse and breakdown the batch response body
            resp_parts = raw_resp.strip().split("\r\n")
            raw_content_id = resp_parts[1]
            raw_body = resp_parts[-1]
            raw_status = resp_parts[3]
            job_id = raw_content_id.split(" ")[1]
            _, status_code, status_text = raw_status.split(" ", 2)

            # Update the corresponding batch job
            queued_req, queued_job = self._queue[job_id]

            queued_job._status = "done"
            resp = Response(
                method=queued_req.method,
                url=url_prefix + queued_req.endpoint,
                headers={},
                status_code=int(status_code),
                status_text=status_text,
                raw_body=raw_body,
            )
            queued_job._response = self._conn.prep_response(resp)

        return self.jobs


class TransactionApiExecutor:
    """Executes transaction API requests.

    :param connection: HTTP connection.
    :param read: Name(s) of collections read during transaction. Read-only
        collections are added lazily but should be declared if possible to
        avoid deadlocks.
    :type read: str | [str]
    :param write: Name(s) of collections written to during transaction with
        shared access.
    :type write: str | [str]
    :param exclusive: Name(s) of collections written to during transaction
        with exclusive access.
    :type exclusive: str | [str]
    :param sync: Block until operation is synchronized to disk.
    :type sync: bool | None
    :param allow_implicit: Allow reading from undeclared collections.
    :type allow_implicit: bool
    :param lock_timeout: Timeout for waiting on collection locks. If not given,
        a default value is used. Setting it to 0 disables the timeout.
    :type lock_timeout: int
    :param max_size: Max transaction size in bytes.
    :type max_size: int
    :param allow_dirty_read: Allow reads from followers in a cluster.
    :type allow_dirty_read: bool | None
    """

    def __init__(
        self,
        connection: Connection,
        read: Optional[Fields] = None,
        write: Optional[Fields] = None,
        exclusive: Optional[Fields] = None,
        sync: Optional[bool] = None,
        allow_implicit: Optional[bool] = None,
        lock_timeout: Optional[int] = None,
        max_size: Optional[int] = None,
        allow_dirty_read: bool = False,
    ) -> None:
        self._conn = connection

        collections: Json = {}
        if read is not None:
            collections["read"] = read
        if write is not None:
            collections["write"] = write
        if exclusive is not None:
            collections["exclusive"] = exclusive

        data: Json = {"collections": collections}
        if sync is not None:
            data["waitForSync"] = sync
        if allow_implicit is not None:
            data["allowImplicit"] = allow_implicit
        if lock_timeout is not None:
            data["lockTimeout"] = lock_timeout
        if max_size is not None:
            data["maxTransactionSize"] = max_size

        request = Request(
            method="post",
            endpoint="/_api/transaction/begin",
            data=data,
            headers={"x-arango-allow-dirty-read": "true"} if allow_dirty_read else None,
        )
        resp = self._conn.send_request(request)

        if not resp.is_success:
            raise TransactionInitError(resp, request)

        result: Json = resp.body["result"]
        self._id: str = result["id"]

    @property
    def context(self) -> str:
        return "transaction"

    @property
    def id(self) -> str:
        """Return the transaction ID.

        :return: Transaction ID.
        :rtype: str
        """
        return self._id

    def execute(
        self,
        request: Request,
        response_handler: Callable[[Response], T],
        allow_dirty_read: bool = False,
    ) -> T:
        """Execute API request in a transaction and return the result.

        :param request: HTTP request.
        :type request: arango.request.Request
        :param response_handler: HTTP response handler.
        :type response_handler: callable
        :param allow_dirty_read: Allow reads from followers in a cluster.
        :type allow_dirty_read: bool | None
        :return: API execution result.
        """
        request.headers["x-arango-trx-id"] = self._id
        if allow_dirty_read:
            request.headers["x-arango-allow-dirty-read"] = "true"
        resp = self._conn.send_request(request)
        return response_handler(resp)

    def status(self) -> str:
        """Return the transaction status.

        :return: Transaction status.
        :rtype: str
        :raise arango.exceptions.TransactionStatusError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint=f"/_api/transaction/{self._id}",
        )
        resp = self._conn.send_request(request)

        if resp.is_success:
            return str(resp.body["result"]["status"])
        raise TransactionStatusError(resp, request)

    def commit(self) -> bool:
        """Commit the transaction.

        :return: True if commit was successful.
        :rtype: bool
        :raise arango.exceptions.TransactionCommitError: If commit fails.
        """
        request = Request(
            method="put",
            endpoint=f"/_api/transaction/{self._id}",
        )
        resp = self._conn.send_request(request)

        if resp.is_success:
            return True
        raise TransactionCommitError(resp, request)

    def abort(self) -> bool:
        """Abort the transaction.

        :return: True if the abort operation was successful.
        :rtype: bool
        :raise arango.exceptions.TransactionAbortError: If abort fails.
        """
        request = Request(
            method="delete",
            endpoint=f"/_api/transaction/{self._id}",
        )
        resp = self._conn.send_request(request)

        if resp.is_success:
            return True
        raise TransactionAbortError(resp, request)


class OverloadControlApiExecutor:
    """Allows setting the maximum acceptable server-side queuing time
        for client requests.

    :param connection: HTTP connection.
    :type connection: arango.connection.BasicConnection |
        arango.connection.JwtConnection | arango.connection.JwtSuperuserConnection
    :param max_queue_time_seconds: Maximum server-side queuing time in seconds.
    :type max_queue_time_seconds: float
    """

    def __init__(
        self, connection: Connection, max_queue_time_seconds: Optional[float] = None
    ) -> None:
        self._conn = connection
        self._max_queue_time_seconds = max_queue_time_seconds
        self._queue_time_seconds = 0.0

    @property
    def context(self) -> str:  # pragma: no cover
        return "overload-control"

    @property
    def queue_time_seconds(self) -> float:
        """Return the most recent request queuing/de-queuing time.
            Defaults to 0 if no request has been sent.

        :return: Server-side queuing time in seconds.
        :rtype: float
        """
        return self._queue_time_seconds

    @property
    def max_queue_time_seconds(self) -> Optional[float]:
        """Return the maximum server-side queuing time.

        :return: Maximum server-side queuing time in seconds.
        :rtype: Optional[float]
        """
        return self._max_queue_time_seconds

    @max_queue_time_seconds.setter
    def max_queue_time_seconds(self, value: Optional[float]) -> None:
        """Set the maximum server-side queuing time.
            Setting it to None disables the feature.

        :param value: Maximum server-side queuing time in seconds.
        :type value: Optional[float]
        """
        self._max_queue_time_seconds = value

    def execute(
        self,
        request: Request,
        response_handler: Callable[[Response], T],
    ) -> T:
        """Execute an API request and return the result.

        :param request: HTTP request.
        :type request: arango.request.Request
        :param response_handler: HTTP response handler.
        :type response_handler: callable
        :return: API execution result.
        """
        if self._max_queue_time_seconds is not None:
            request.headers["x-arango-queue-time-seconds"] = str(
                self._max_queue_time_seconds
            )
        resp = self._conn.send_request(request)

        if not resp.is_success:
            raise OverloadControlExecutorError(resp, request)

        if "X-Arango-Queue-Time-Seconds" in resp.headers:
            self._queue_time_seconds = float(
                resp.headers["X-Arango-Queue-Time-Seconds"]
            )

        return response_handler(resp)
