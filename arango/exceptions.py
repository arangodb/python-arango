"""ArangoDB Exceptions."""


class ArangoError(Exception):
    """Base ArangoDB exception class."""

    def __init__(self, message, response=None):
        if response is not None:
            message = "{message} ({status_code} {reason})".format(
                message=message,
                status_code=response.status_code,
                reason=response.reason,
            )
        super(ArangoError, self).__init__(message)


class ArangoDatabaseReadError(ArangoError):
    """Failed to retrieve database information."""


class ArangoDatabaseCreateError(ArangoError):
    """Failed to create a new database"""


class ArangoDatabaseDeleteError(ArangoError):
    """Failed to delete a database."""
