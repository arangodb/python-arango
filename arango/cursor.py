__all__ = ["Cursor"]

from collections import deque
from typing import Any, Deque, Optional, Sequence

from arango.connection import BaseConnection
from arango.exceptions import (
    CursorCloseError,
    CursorCountError,
    CursorEmptyError,
    CursorNextError,
    CursorStateError,
)
from arango.request import Request
from arango.typings import Json


class Cursor:
    """Cursor API wrapper.

    Cursors fetch query results from ArangoDB server in batches. Cursor objects
    are *stateful* as they store the fetched items in-memory. They must not be
    shared across threads without proper locking mechanism.

    :param connection: HTTP connection.
    :param init_data: Cursor initialization data.
    :type init_data: dict
    :param cursor_type: Cursor type ("cursor" or "export").
    :type cursor_type: str
    :param allow_retry: If set to True, the cursor will always attempt to fetch
            the latest batch from server even if the previous attempt failed.
            This option is only available for server versions 3.11 and above.
    :type allow_retry: bool
    """

    __slots__ = [
        "_conn",
        "_type",
        "_id",
        "_count",
        "_cached",
        "_stats",
        "_profile",
        "_warnings",
        "_has_more",
        "_batch",
        "_next_batch_id",
        "_allow_retry",
    ]

    def __init__(
        self,
        connection: BaseConnection,
        init_data: Json,
        cursor_type: str = "cursor",
        allow_retry: bool = False,
    ) -> None:
        self._conn = connection
        self._type = cursor_type
        self._allow_retry = allow_retry
        self._batch: Deque[Any] = deque()
        self._id = None
        self._count: Optional[int] = None
        self._cached = None
        self._stats = None
        self._profile = None
        self._warnings = None
        self._next_batch_id: Optional[str] = None
        self._update(init_data)

    def __iter__(self) -> "Cursor":
        return self

    def __next__(self) -> Any:  # pragma: no cover
        return self.next()

    def __enter__(self) -> "Cursor":
        return self

    def __len__(self) -> int:
        if self._count is None:
            raise CursorCountError("cursor count not enabled")
        return self._count

    def __exit__(self, *_: Any) -> None:
        self.close(ignore_missing=True)

    def __repr__(self) -> str:
        return f"<Cursor {self._id}>" if self._id else "<Cursor>"

    def _update(self, data: Json) -> Json:
        """Update the cursor using data from ArangoDB server.

        :param data: Cursor data from ArangoDB server (e.g. results).
        :type data: dict
        :return: Update cursor data.
        :rtype: dict
        """
        result: Json = {}

        if "id" in data:
            self._id = data["id"]
            result["id"] = data["id"]
        if "count" in data:
            self._count = data["count"]
            result["count"] = data["count"]
        if "cached" in data:
            self._cached = data["cached"]
            result["cached"] = data["cached"]

        # New in 3.11
        if "nextBatchId" in data:
            # This is only available for server versions 3.11 and above.
            # Currently, we are testing against 3.10.9
            self._next_batch_id = data["nextBatchId"]  # pragma: no cover
            result["next_batch_id"] = data["nextBatchId"]  # pragma: no cover

        self._has_more = bool(data["hasMore"])
        result["has_more"] = data["hasMore"]

        self._batch.extend(data["result"])
        result["batch"] = data["result"]

        if "extra" in data:
            extra = data["extra"]

            if "profile" in extra:
                self._profile = extra["profile"]
                result["profile"] = extra["profile"]

            if "warnings" in extra:
                self._warnings = extra["warnings"]
                result["warnings"] = extra["warnings"]

            if "stats" in extra:
                stats = extra["stats"]
                if "writesExecuted" in stats:
                    stats["modified"] = stats.pop("writesExecuted")
                if "writesIgnored" in stats:
                    stats["ignored"] = stats.pop("writesIgnored")
                if "scannedFull" in stats:
                    stats["scanned_full"] = stats.pop("scannedFull")
                if "scannedIndex" in stats:
                    stats["scanned_index"] = stats.pop("scannedIndex")
                if "executionTime" in stats:
                    stats["execution_time"] = stats.pop("executionTime")
                if "httpRequests" in stats:
                    stats["http_requests"] = stats.pop("httpRequests")
                if "cursorsCreated" in stats:
                    stats["cursorsCreated"] = stats.pop("cursorsCreated")
                if "cursorsRearmed" in stats:
                    stats["cursorsRearmed"] = stats.pop("cursorsRearmed")
                if "cacheHits" in stats:
                    stats["cacheHits"] = stats.pop("cacheHits")
                if "cacheMisses" in stats:
                    stats["cacheMisses"] = stats.pop("cacheMisses")

                # New in 3.11
                if "peakMemoryUsage" in stats:
                    stats["peak_memory_usage"] = stats.pop("peakMemoryUsage")

                self._stats = stats
                result["statistics"] = stats

        return result

    @property
    def id(self) -> Optional[str]:
        """Return the cursor ID.

        :return: Cursor ID.
        :rtype: str
        """
        return self._id

    @property
    def type(self) -> str:
        """Return the cursor type.

        :return: Cursor type ("cursor" or "export").
        :rtype: str
        """
        return self._type

    def batch(self) -> Optional[Deque[Any]]:
        """Return the current batch of results.

        :return: Current batch.
        :rtype: collections.deque
        """
        return self._batch

    def has_more(self) -> Optional[bool]:
        """Return True if more results are available on the server.

        :return: True if more results are available on the server.
        :rtype: bool
        """
        return self._has_more

    def count(self) -> Optional[int]:
        """Return the total number of documents in the entire result set.

        :return: Total number of documents, or None if the count option
            was not enabled during cursor initialization.
        :rtype: int | None
        """
        return self._count

    def cached(self) -> Optional[bool]:
        """Return True if results are cached.

        :return: True if results are cached.
        :rtype: bool
        """
        return self._cached

    def statistics(self) -> Optional[Json]:
        """Return cursor statistics.

        :return: Cursor statistics.
        :rtype: dict
        """
        return self._stats

    def profile(self) -> Optional[Json]:
        """Return cursor performance profile.

        :return: Cursor performance profile.
        :rtype: dict
        """
        return self._profile

    def warnings(self) -> Optional[Sequence[Json]]:
        """Return any warnings from the query execution.

        :return: Warnings, or None if there are none.
        :rtype: [str]
        """
        return self._warnings

    def empty(self) -> bool:
        """Check if the current batch is empty.

        :return: True if current batch is empty, False otherwise.
        :rtype: bool
        """
        return len(self._batch) == 0

    def next(self) -> Any:
        """Pop the next item from the current batch.

        If current batch is empty/depleted, an API request is automatically
        sent to ArangoDB server to fetch the next batch and update the cursor.

        :return: Next item in current batch.
        :raise StopIteration: If the result set is depleted.
        :raise arango.exceptions.CursorNextError: If batch retrieval fails.
        :raise arango.exceptions.CursorStateError: If cursor ID is not set.
        """
        if self.empty():
            if not self.has_more():
                raise StopIteration
            self.fetch()

        return self.pop()

    def pop(self) -> Any:
        """Pop the next item from current batch.

        If current batch is empty/depleted, an exception is raised. You must
        call :func:`arango.cursor.Cursor.fetch` to manually fetch the next
        batch from server.

        :return: Next item in current batch.
        :raise arango.exceptions.CursorEmptyError: If current batch is empty.
        """
        if len(self._batch) == 0:
            raise CursorEmptyError("current batch is empty")
        return self._batch.popleft()

    def fetch(self) -> Json:
        """Fetch the next batch from server and update the cursor.

        :return: New batch details.
        :rtype: dict
        :raise arango.exceptions.CursorNextError: If batch retrieval fails.
        :raise arango.exceptions.CursorStateError: If cursor ID is not set.
        """
        if self._id is None:
            raise CursorStateError("cursor ID not set")

        endpoint = f"/_api/{self._type}/{self._id}"
        if self._allow_retry and self._next_batch_id is not None:
            endpoint += f"/{self._next_batch_id}"  # pragma: no cover

        request = Request(method="post", endpoint=endpoint)
        resp = self._conn.send_request(request)

        if not resp.is_success:
            raise CursorNextError(resp, request)

        return self._update(resp.body)

    def close(self, ignore_missing: bool = False) -> Optional[bool]:
        """Close the cursor and free any server resources tied to it.

        :param ignore_missing: Do not raise exception on missing cursors.
        :type ignore_missing: bool
        :return: True if cursor was closed successfully, False if cursor was
            missing on the server and **ignore_missing** was set to True, None
            if there are no cursors to close server-side (e.g. result set is
            smaller than the batch size).
        :rtype: bool | None
        :raise arango.exceptions.CursorCloseError: If operation fails.
        :raise arango.exceptions.CursorStateError: If cursor ID is not set.
        """
        if self._id is None:
            return None
        request = Request(method="delete", endpoint=f"/_api/{self._type}/{self._id}")
        resp = self._conn.send_request(request)
        if resp.is_success:
            return True
        if resp.status_code == 404 and ignore_missing:
            return False
        raise CursorCloseError(resp, request)
