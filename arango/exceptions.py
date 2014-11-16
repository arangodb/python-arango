"""ArangoDB Exceptions."""


class ArangoError(Exception):
    """Base ArangoDB exception class."""

    def __init__(self, message, response=None):
        if response:
            super(ArangoError, self).__init__(
                "{message} ({status_code}: {reason})".format(
                    message=message,
                    status_code=response.status_code,
                    reason=response.reason,
                )
            )
            self.url= response.url
            self.status_code = response.status_code
            self.reason = response.reason
        else:
            super(ArangoError, self).__init__(message)
            self.url = self.status_code = self.reason = None


class ArangoConnectionInitError(ArangoError):
    """Failed to initialize the connection to ArangoDB."""

#############
# Databases #
#############

class ArangoDatabaseError(ArangoError):
    """Request failed on a database endpoint."""


class ArangoDatabaseNotFoundError(ArangoError):
    """The database does not exist."""


class ArangoDatabaseCreateError(ArangoError):
    """Failed to create the database."""


class ArangoDatabaseDeleteError(ArangoError):
    """Failed to delete the database."""


##############
# Collection #
##############

class ArangoCollectionNotFoundError(ArangoError):
    """The collection does not exist in ArangoDB."""


class ArangoCollectionError(ArangoError):
    """Failed to retrieve the collection."""


class ArangoCollectionCreateError(ArangoError):
    """Failed to create the collection."""


class ArangoCollectionDeleteError(ArangoError):
    """Failed to delete the collection."""


class ArangoCollectionTruncateError(ArangoError):
    """Failed to delete the collection."""