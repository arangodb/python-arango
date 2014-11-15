"""ArangoDB Exceptions."""


class ArangoError(Exception):
    """Base ArangoDB exception class."""

    def __init__(self, message, response=None):
        if response is not None:
            self.status_code = response.status_code
            self.reason = response.reason
            message = "{message} ({status_code} {reason})".format(
                message=message,
                status_code=response.status_code,
                reason=response.reason,
            )
        else:
            self.status_code = None
            self.reason = None
        super(ArangoError, self).__init__(message)


class ArangoConnectionInitError(ArangoError):
    """Failed to initialize the connection to ArangoDB."""


class ArangoDatabaseNotFoundError(ArangoError):
    """The database does not exist in ArangoDB."""


class ArangoDatabaseReadError(ArangoError):
    """Failed to retrieve the database."""


class ArangoDatabaseCreateError(ArangoError):
    """Failed to create the database."""


class ArangoDatabaseDeleteError(ArangoError):
    """Failed to delete the database."""


class ArangoCollectionNotFoundError(ArangoError):
    """The collection does not exist in ArangoDB."""


class ArangoCollectionReadError(ArangoError):
    """Failed to retrieve the collection."""


class ArangoCollectionCreateError(ArangoError):
    """Failed to create the collection."""


class ArangoCollectionDeleteError(ArangoError):
    """Failed to delete the collection."""


class ArangoCollectionTruncateError(ArangoError):
    """Failed to delete the collection."""