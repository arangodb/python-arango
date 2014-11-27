"""ArangoDB Exception."""


class ArangoRequestError(Exception):
    """Base ArangoDB request exception class."""

    def __init__(self, res):
        if res.obj is not None and "errorMessage" in res.obj:
            message = res.obj["errorMessage"]
        else:
            message = res.reason
        super(ArangoRequestError, self).__init__(
            "{message} ({status_code})".format(
                message=message,
                status_code=res.status_code
            )
        )
        self.status_code = res.status_code


class ArangoNotFoundError(KeyError):
    """ArangoDB key error class."""

    def __init__(self, name):
        super(ArangoNotFoundError, self).__init__(name)

#########################
# Connection Exceptions #
#########################

class ArangoConnectionError(Exception):
    """Failed to connect to ArangoDB."""


class ArangoVersionError(ArangoRequestError):
    """Failed to retrieve the version."""

#######################
# Database Exceptions #
#######################

class ArangoDatabaseNotFoundError(ArangoNotFoundError):
    """Failed to locate database."""


class ArangoDatabaseListError(ArangoRequestError):
    """Failed to retrieve the database list."""


class ArangoDatabasePropertyError(ArangoRequestError):
    """Failed to retrieve the database property."""


class ArangoDatabaseCreateError(ArangoRequestError):
    """Failed to create the database."""


class ArangoDatabaseDeleteError(ArangoRequestError):
    """Failed to delete the database."""

#########################
# Collection Exceptions #
#########################

class ArangoCollectionNotFoundError(ArangoNotFoundError):
    """Failed to locate the collection."""


class ArangoCollectionListError(ArangoRequestError):
    """Failed to retrieve the collection list."""


class ArangoCollectionPropertyError(ArangoRequestError):
    """Failed to retrieve the collection property."""


class ArangoCollectionCreateError(ArangoRequestError):
    """Failed to create the collection."""


class ArangoCollectionDeleteError(ArangoRequestError):
    """Failed to delete the collection"""


class ArangoCollectionModifyError(ArangoRequestError):
    """Failed to modify the collection."""


class ArangoCollectionRenameError(ArangoRequestError):
    """Failed to rename the collection."""


class ArangoCollectionTruncateError(ArangoRequestError):
    """Failed to truncate the collection."""


class ArangoCollectionLoadError(ArangoRequestError):
    """Failed to load the collection into memory."""


class ArangoCollectionUnloadError(ArangoRequestError):
    """Failed to unload the collection from memory."""


class ArangoCollectionRotateJournalError(ArangoRequestError):
    """Failed to rotate the journal of the collection."""

#######################
# Document Exceptions #
#######################

class ArangoDocumentInvalidError(Exception):
    """The document is invalid."""


class ArangoDocumentGetError(ArangoRequestError):
    """Failed to get the ArangoDB document(s)."""


class ArangoDocumentCreateError(ArangoRequestError):
    """Failed to create the ArangoDB document(s)."""


class ArangoDocumentReplaceError(ArangoRequestError):
    """Failed to create the ArangoDB document(s)."""


class ArangoDocumentPatchError(ArangoRequestError):
    """Failed to create the ArangoDB document(s)."""


class ArangoDocumentDeleteError(ArangoRequestError):
    """Failed to create the ArangoDB document(s)."""

####################
# Index Exceptions #
####################

class ArangoIndexListError(ArangoRequestError):
    """Failed to list all the collections."""


class ArangoIndexCreateError(ArangoRequestError):
    """Failed to create the index."""


class ArangoIndexDeleteError(ArangoRequestError):
    """Failed to delete the index."""

##################
# AQL Exceptions #
##################

class ArangoQueryParseError(ArangoRequestError):
    """Failed to validate the query."""


class ArangoQueryExecuteError(ArangoRequestError):
    """Failed to execute the query."""


class ArangoCursorDeleteError(ArangoRequestError):
    """Failed to delete the query cursor."""


class ArangoAQLFunctionListError(ArangoRequestError):
    """Failed to get the list of AQL functions."""


class ArangoAQLFunctionCreateError(ArangoRequestError):
    """Failed to create the AQL function."""


class ArangoAQLFunctionDeleteError(ArangoRequestError):
    """Failed to delete the AQL function."""