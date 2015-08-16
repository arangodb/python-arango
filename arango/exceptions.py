"""ArangoDB Exception."""


class ArangoRequestError(Exception):
    """Base class for ArangoDB request exceptions.

    :param response: the Response object
    :type response: arango.response.Response
    """

    def __init__(self, response):
        # Get the ArangoDB error message if given
        if response.obj is not None and "errorMessage" in response.obj:
            message = response.obj["errorMessage"]
        elif response.status_text is not None:
            message = response.status_text
        else:
            message = "not given"

        # Get the ArangoDB error number if given
        if response.obj is not None and "errorNum" in response.obj:
            error_num = response.obj["errorNum"]
        else:
            error_num = "not given"

        # Generate the error message for the exception
        super(ArangoRequestError, self).__init__(
            "HTTP Method: {method}, URL: {url}, "
            "HTTP Status Code: {status_code}, "
            "Server Error Number: {error_num}, "
            "Error Message: {message}".format(
                method=response.method,
                url=response.url,
                status_code=response.status_code,
                error_num=error_num,
                message=message,
            )
        )
        self.status_code = response.status_code
        self.status_text = response.status_text


class ArangoNotFoundError(KeyError):
    """Base ArangoDB "not found" exception class.

    :param name: the name of the missing ArangoDB object
    :type name: str
    """

    def __init__(self, name):
        self.name = name
        super(ArangoNotFoundError, self).__init__(name)


class ArangoConnectionError(ArangoRequestError):
    """Failed to connect to ArangoDB."""


class VersionGetError(ArangoRequestError):
    """Failed to retrieve the version."""


class InvalidArgumentError(Exception):
    """The given argument(s) are invalid."""


#######################
# Database Exceptions #
#######################


class DatabaseNotFoundError(ArangoNotFoundError):
    """Failed to find the database."""


class DatabaseListError(ArangoRequestError):
    """Failed to get the list of databases."""


class DatabasePropertyError(ArangoRequestError):
    """Failed to get the database property."""


class DatabaseGetError(ArangoRequestError):
    """Failed to get the database."""


class DatabaseCreateError(ArangoRequestError):
    """Failed to create the database."""


class DatabaseDeleteError(ArangoRequestError):
    """Failed to delete the database."""


###################
# User Exceptions #
###################


class UserGetAllError(ArangoRequestError):
    """Failed to get the list of users."""


class UserGetError(ArangoRequestError):
    """Failed to get the user."""


class UserCreateError(ArangoRequestError):
    """Failed to create the user."""


class UserUpdateError(ArangoRequestError):
    """Failed to update the user."""


class UserReplaceError(ArangoRequestError):
    """Failed to replace the user."""


class UserDeleteError(ArangoRequestError):
    """Failed to delete the user."""


#########################
# Collection Exceptions #
#########################


class CollectionCorruptedError(Exception):
    """The collection is corrupted (i.e. its status is ``unknown``)."""


class CollectionNotFoundError(ArangoNotFoundError):
    """Failed to find the collection."""


class CollectionListError(ArangoRequestError):
    """Failed to get the list of collections."""


class CollectionGetError(ArangoRequestError):
    """Failed to get the collection."""


class CollectionChecksumError(ArangoRequestError):
    """Failed to get the collection checksum."""


class CollectionCreateError(ArangoRequestError):
    """Failed to create the collection."""


class CollectionDeleteError(ArangoRequestError):
    """Failed to delete the collection"""


class CollectionUpdateError(ArangoRequestError):
    """Failed to update the collection."""


class CollectionRenameError(ArangoRequestError):
    """Failed to rename the collection."""


class CollectionTruncateError(ArangoRequestError):
    """Failed to truncate the collection."""


class CollectionLoadError(ArangoRequestError):
    """Failed to load the collection into memory."""


class CollectionUnloadError(ArangoRequestError):
    """Failed to unload the collection from memory."""


class CollectionRotateJournalError(ArangoRequestError):
    """Failed to rotate the journal of the collection."""


class CollectionExportError(ArangoRequestError):
    """Failed to export the collection."""

##########################
# Bulk Import Exceptions #
##########################


class BulkImportError(ArangoRequestError):
    """Failed to bulk import documents/edges."""


#######################
# Document Exceptions #
#######################


class DocumentInvalidError(Exception):
    """The document is invalid (malformed)."""


class DocumentRevisionError(ArangoRequestError):
    """The expected and actual document revisions do not match."""


class DocumentGetError(ArangoRequestError):
    """Failed to get the document."""


class DocumentCreateError(ArangoRequestError):
    """Failed to create the document."""


class DocumentReplaceError(ArangoRequestError):
    """Failed to replace the document."""


class DocumentUpdateError(ArangoRequestError):
    """Failed to update the document."""


class DocumentDeleteError(ArangoRequestError):
    """Failed to delete the document."""


###################
# Edge Exceptions #
###################


class EdgeInvalidError(Exception):
    """The edge is invalid (malformed)."""


class EdgeRevisionError(ArangoRequestError):
    """The expected and actual edge revisions do not match."""


class EdgeGetError(ArangoRequestError):
    """Failed to get the edge."""


class EdgeCreateError(ArangoRequestError):
    """Failed to create the edge."""


class EdgeReplaceError(ArangoRequestError):
    """Failed to replace the edge."""


class EdgeUpdateError(ArangoRequestError):
    """Failed to update the edge."""


class EdgeDeleteError(ArangoRequestError):
    """Failed to delete the edge."""


#####################
# Vertex Exceptions #
#####################


class VertexInvalidError(ArangoRequestError):
    """The vertex is invalid (malformed)."""


class VertexRevisionError(ArangoRequestError):
    """The expected and actual vertex revisions do not match."""


class VertexGetError(ArangoRequestError):
    """Failed to get the vertex."""


class VertexCreateError(ArangoRequestError):
    """Failed to create the vertex."""


class VertexUpdateError(ArangoRequestError):
    """Failed to update the vertex."""


class VertexReplaceError(ArangoRequestError):
    """Failed to replace the vertex."""


class VertexDeleteError(ArangoRequestError):
    """Failed to delete the vertex."""


####################
# Index Exceptions #
####################


class IndexListError(ArangoRequestError):
    """Failed to get the list of indexes."""


class IndexCreateError(ArangoRequestError):
    """Failed to create the index."""


class IndexDeleteError(ArangoRequestError):
    """Failed to delete the index."""


########################
# AQL Query Exceptions #
########################


class AQLQueryExplainError(ArangoRequestError):
    """Failed to explain the AQL query."""


class AQLQueryValidateError(ArangoRequestError):
    """Failed to validate the AQL query."""


class AQLQueryExecuteError(ArangoRequestError):
    """Failed to execute the AQL query."""


#####################
# Cursor Exceptions #
#####################

class CursorGetNextError(ArangoRequestError):
    """Failed to get the next cursor result."""


class CursorDeleteError(ArangoRequestError):
    """Failed to delete the cursor."""


###########################
# AQL Function Exceptions #
###########################


class AQLFunctionListError(ArangoRequestError):
    """Failed to get the list of AQL functions."""


class AQLFunctionCreateError(ArangoRequestError):
    """Failed to create the AQL function."""


class AQLFunctionDeleteError(ArangoRequestError):
    """Failed to delete the AQL function."""


###########################
# Simple Query Exceptions #
###########################


class SimpleQueryGetByExampleError(ArangoRequestError):
    """Failed to execute the ``by-example`` simple query."""


class SimpleQueryFirstExampleError(ArangoRequestError):
    """Failed to execute the ``first-example`` simple query."""


class SimpleQueryReplaceByExampleError(ArangoRequestError):
    """Failed to execute the ``replace-by-example`` simple query."""


class SimpleQueryUpdateByExampleError(ArangoRequestError):
    """Failed to execute the ``update-by-example`` simple query."""


class SimpleQueryDeleteByExampleError(ArangoRequestError):
    """Failed to execute the ``Delete-by-example`` simple query."""


class SimpleQueryFirstError(ArangoRequestError):
    """Failed to execute the ``first`` simple query."""


class SimpleQueryLastError(ArangoRequestError):
    """Failed to execute the ``last`` simple query."""


class SimpleQueryAllError(ArangoRequestError):
    """Failed to execute the `all`` simple query."""


class SimpleQueryAnyError(ArangoRequestError):
    """Failed to execute the ``any`` simple query."""


class SimpleQueryRangeError(ArangoRequestError):
    """Failed to execute the ``range`` simple query."""


class SimpleQueryNearError(ArangoRequestError):
    """Failed to execute the ``near`` simple query."""


class SimpleQueryWithinError(ArangoRequestError):
    """Failed to execute the ``within`` simple query."""


class SimpleQueryFullTextError(ArangoRequestError):
    """Failed to execute the ``fulltext`` simple query."""


class SimpleQueryLookupByKeysError(ArangoRequestError):
    """Failed to execute the ``lookup-by-keys`` simple query."""


class SimpleQueryDeleteByKeysError(ArangoRequestError):
    """Failed to execute the ``Delete-by-keys`` simple query."""


class SimpleQueryError(ArangoRequestError):
    """Failed to execute a simple query."""


##########################
# Transaction Exceptions #
##########################


class TransactionExecuteError(ArangoRequestError):
    """Failed to execute a transaction."""


####################
# Batch Exceptions #
####################


class BatchInvalidError(Exception):
    """The batch request is invalid (malformed)."""


class BatchExecuteError(ArangoRequestError):
    """Failed to execute a batch request."""


####################
# Graph Exceptions #
####################


class GraphNotFoundError(ArangoNotFoundError):
    """Failed to find the graph."""


class GraphListError(ArangoRequestError):
    """Failed to get the list of graphs."""


class GraphGetError(ArangoRequestError):
    """Failed to get the graph."""


class GraphCreateError(ArangoRequestError):
    """Failed to create the graph."""


class GraphDeleteError(ArangoRequestError):
    """Failed to delete the graph."""


class GraphPropertyError(ArangoRequestError):
    """Failed to get the graph property."""


class GraphTraversalError(ArangoRequestError):
    """Failed to execute the graph traversal."""


######################
# Vertex Collections #
######################


class VertexCollectionListError(ArangoRequestError):
    """Failed to get the list of vertex collections."""


class VertexCollectionCreateError(ArangoRequestError):
    """Failed to create the vertex collection."""


class VertexCollectionDeleteError(ArangoRequestError):
    """Failed to delete the vertex collection."""


################################
# Edge Collections/Definitions #
################################


class EdgeDefinitionListError(ArangoRequestError):
    """Failed to get the list of edge definitions."""


class EdgeDefinitionCreateError(ArangoRequestError):
    """Failed to create the edge definition."""


class EdgeDefinitionReplaceError(ArangoRequestError):
    """Failed to replace the edge definition."""


class EdgeDefinitionDeleteError(ArangoRequestError):
    """Failed to delete the edge definition."""


##############
# Monitoring #
##############


class LogGetError(ArangoRequestError):
    """Failed to get the global log."""


class RountingInfoReloadError(ArangoRequestError):
    """Failed to reload the routing information."""


class StatisticsGetError(ArangoRequestError):
    """Failed to get the server statistics."""


class StatisticsDescriptionGetError(ArangoRequestError):
    """Failed to get the statistics description."""


class ServerRoleGetError(ArangoRequestError):
    """Failed to get the role of the server in a cluster."""


