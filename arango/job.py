__all__ = ["AsyncJob", "BatchJob"]

from concurrent.futures import Future
from typing import Callable, Generic, Optional, TypeVar
from uuid import uuid4

from arango.connection import Connection
from arango.exceptions import (
    AsyncJobCancelError,
    AsyncJobClearError,
    AsyncJobResultError,
    AsyncJobStatusError,
    BatchJobResultError,
)
from arango.request import Request
from arango.response import Response

T = TypeVar("T")


class AsyncJob(Generic[T]):
    """Job for tracking and retrieving result of an async API execution.

    :param connection: HTTP connection.
    :param job_id: Async job ID.
    :type job_id: str
    :param response_handler: HTTP response handler.
    :type response_handler: callable
    """

    __slots__ = ["_conn", "_id", "_response_handler"]

    def __init__(
        self,
        connection: Connection,
        job_id: str,
        response_handler: Callable[[Response], T],
    ) -> None:
        self._conn = connection
        self._id = job_id
        self._response_handler = response_handler

    def __repr__(self) -> str:
        return f"<AsyncJob {self._id}>"

    @property
    def id(self) -> str:
        """Return the async job ID.

        :return: Async job ID.
        :rtype: str
        """
        return self._id

    def status(self) -> str:
        """Return the async job status from server.

        Once a job result is retrieved via func:`arango.job.AsyncJob.result`
        method, it is deleted from server and subsequent status queries will
        fail.

        :return: Async job status. Possible values are "pending" (job is still
            in queue), "done" (job finished or raised an error), or "cancelled"
            (job was cancelled before completion).
        :rtype: str
        :raise arango.exceptions.AsyncJobStatusError: If retrieval fails.
        """
        request = Request(method="get", endpoint=f"/_api/job/{self._id}")
        resp = self._conn.send_request(request)

        if resp.status_code == 204:
            return "pending"
        elif resp.is_success:
            return "done"
        elif resp.error_code == 404:
            error_message = f"job {self._id} not found"
            raise AsyncJobStatusError(resp, request, error_message)
        else:
            raise AsyncJobStatusError(resp, request)

    def result(self) -> T:
        """Return the async job result from server.

        If the job raised an exception, it is propagated up at this point.

        Once job result is retrieved, it is deleted from server and subsequent
        queries for result will fail.

        :return: Async job result.
        :raise arango.exceptions.ArangoError: If the job raised an exception.
        :raise arango.exceptions.AsyncJobResultError: If retrieval fails.
        """
        request = Request(method="put", endpoint=f"/_api/job/{self._id}")
        resp = self._conn.send_request(request)

        if "X-Arango-Async-Id" in resp.headers or "x-arango-async-id" in resp.headers:
            return self._response_handler(resp)

        if resp.status_code == 204:
            error_message = f"job {self._id} not done"
            raise AsyncJobResultError(resp, request, error_message)
        elif resp.error_code == 404:
            error_message = f"job {self._id} not found"
            raise AsyncJobResultError(resp, request, error_message)
        else:
            raise AsyncJobResultError(resp, request)

    def cancel(self, ignore_missing: bool = False) -> bool:
        """Cancel the async job.

        An async job cannot be cancelled once it is taken out of the queue.

        :param ignore_missing: Do not raise an exception on missing job.
        :type ignore_missing: bool
        :return: True if job was cancelled successfully, False if the job
            was not found but **ignore_missing** was set to True.
        :rtype: bool
        :raise arango.exceptions.AsyncJobCancelError: If cancel fails.
        """
        request = Request(method="put", endpoint=f"/_api/job/{self._id}/cancel")
        resp = self._conn.send_request(request)

        if resp.status_code == 200:
            return True
        elif resp.error_code == 404:
            if ignore_missing:
                return False
            error_message = f"job {self._id} not found"
            raise AsyncJobCancelError(resp, request, error_message)
        else:
            raise AsyncJobCancelError(resp, request)

    def clear(self, ignore_missing: bool = False) -> bool:
        """Delete the job result from the server.

        :param ignore_missing: Do not raise an exception on missing job.
        :type ignore_missing: bool
        :return: True if result was deleted successfully, False if the job
            was not found but **ignore_missing** was set to True.
        :rtype: bool
        :raise arango.exceptions.AsyncJobClearError: If delete fails.
        """
        request = Request(method="delete", endpoint=f"/_api/job/{self._id}")
        resp = self._conn.send_request(request)

        if resp.is_success:
            return True
        elif resp.error_code == 404:
            if ignore_missing:
                return False
            error_message = f"job {self._id} not found"
            raise AsyncJobClearError(resp, request, error_message)
        else:
            raise AsyncJobClearError(resp, request)


class BatchJob(Generic[T]):
    """Job for tracking and retrieving result of batch API execution.

    :param response_handler: HTTP response handler.
    :type response_handler: callable
    """

    __slots__ = ["_id", "_status", "_response_handler", "_future"]

    def __init__(self, response_handler: Callable[[Response], T]) -> None:
        self._id = uuid4().hex
        self._status = "pending"
        self._response_handler = response_handler
        self._future: Optional[Future[Response]] = None

    def __repr__(self) -> str:
        return f"<BatchJob {self._id}>"

    @property
    def id(self) -> str:
        """Return the batch job ID.

        :return: Batch job ID.
        :rtype: str
        """
        return self._id

    def status(self) -> str:
        """Return the batch job status.

        :return: Batch job status. Possible values are "pending" (job is still
            waiting for batch to be committed), or "done" (batch was committed
            and the job is updated with the result).
        :rtype: str
        """
        return self._status

    def result(self) -> T:
        """Return the batch job result.

        If the job raised an exception, it is propagated up at this point.

        :return: Batch job result.
        :raise arango.exceptions.ArangoError: If the job raised an exception.
        :raise arango.exceptions.BatchJobResultError: If job result is not
            available (i.e. batch is not committed yet).
        """
        if self._status == "pending" or self._future is None or not self._future.done():
            raise BatchJobResultError("result not available yet")

        return self._response_handler(self._future.result())
