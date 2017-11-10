from arango.exceptions import ArangoError


class AsyncError(ArangoError):
    """Base class for errors in Async queries"""


class AsyncExecuteError(AsyncError):
    """Failed to execute the asynchronous request."""


class AsyncJobListError(AsyncError):
    """Failed to list the IDs of the asynchronous jobs."""


class AsyncJobCancelError(AsyncError):
    """Failed to cancel the asynchronous job."""


class AsyncJobStatusError(AsyncError):
    """Failed to retrieve the asynchronous job result from the server."""


class AsyncJobResultError(AsyncError):
    """Failed to pop the asynchronous job result from the server."""


class AsyncJobClearError(AsyncError):
    """Failed to delete the asynchronous job result from the server."""
