"""ArangoDB Exceptions."""


class ArangoError(Exception):
    """Base ArangoDB exception class."""

    def __init__(self, res, name=None):
        if isinstance(res, str):
            super(ArangoError, self).__init__(res)
            self.status_code = None
        else:
            super(ArangoError, self).__init__(
                "{name}{msg} ({status_code})".format(
                    name="" if name is None else "{}: ".format(name),
                    msg=res.obj.get("errorMessage", res.reason),
                    status_code=res.status_code,
                )
            )
            self.status_code = res.status_code


class ArangoConnectionError(ArangoError):
    """Failed to connect to ArangoDB."""


class ArangoVersionError(ArangoError):
    """Failed to retrieve the version."""

#######################
# Database Exceptions #
#######################

class ArangoDatabaseListError(ArangoError):
    """Failed to retrieve the database list."""


class ArangoDatabaseNotFoundError(ArangoError):
    """Failed to locate database."""


class ArangoDatabasePropertyError(ArangoError):
    """Failed to retrieve the database property."""


class ArangoDatabaseCreateError(ArangoError):
    """Failed to create the database."""


class ArangoDatabaseDeleteError(ArangoError):
    """Failed to delete the database."""

#########################
# Collection Exceptions #
#########################

class ArangoCollectionNotFoundError(ArangoError):
    """Failed to locate the collection."""


class ArangoCollectionListError(ArangoError):
    """Failed to retrieve the collection list."""


class ArangoCollectionPropertyError(ArangoError):
    """Failed to retrieve the collection property."""


class ArangoCollectionCreateError(ArangoError):
    """Failed to create the collection."""


class ArangoCollectionDeleteError(ArangoError):
    """Failed to delete the collection"""


class ArangoCollectionModifyError(ArangoError):
    """Failed to modify the collection."""


class ArangoCollectionRenameError(ArangoError):
    """Failed to rename the collection."""


class ArangoCollectionTruncateError(ArangoError):
    """Failed to truncate the collection."""


class ArangoCollectionLoadError(ArangoError):
    """Failed to load the collection into memory."""


class ArangoCollectionUnloadError(ArangoError):
    """Failed to unload the collection from memory."""


class ArangoCollectionRotateJournalError(ArangoError):
    """Failed to rotate the journal of the collection."""

#######################
# Document Exceptions #
#######################

class ArangoDocumentGetError(ArangoError):
    """Failed to get the ArangoDB document(s)."""


class ArangoDocumentCreateError(ArangoError):
    """Failed to create the ArangoDB document(s)."""



####################
# Index Exceptions #
####################

class ArangoIndexListError(ArangoError):
    """Failed to list all the collections."""


class ArangoIndexCreateError(ArangoError):
    """Failed to create the index."""


class ArangoIndexDeleteError(ArangoError):
    """Failed to delete the index."""
