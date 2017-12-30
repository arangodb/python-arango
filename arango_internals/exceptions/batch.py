from arango_internals.exceptions import ArangoError


class BatchExecuteError(ArangoError):
    """Failed to execute the batch request."""
