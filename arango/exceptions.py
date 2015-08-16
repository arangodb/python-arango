"""ArangoDB Exceptions."""


class RequestError(Exception):
    """Base class for ArangoDB request errors.

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
        super(RequestError, self).__init__(
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


class NotFoundError(KeyError):
    """Base ArangoDB "not found" exception class.

    :param name: the name of the missing ArangoDB object
    :type name: str
    """

    def __init__(self, name):
        self.name = name
        super(NotFoundError, self).__init__(name)


class ConnectionError(RequestError):
    """Failed to connect to ArangoDB."""


class VersionGetError(RequestError):
    """Failed to retrieve the version."""


class InvalidArgumentError(Exception):
    """The given argument(s) are invalid."""


#######################
# Database Exceptions #
#######################


class DatabaseNotFoundError(NotFoundError):
    """Failed to find the database."""


class DatabaseListError(RequestError):
    """Failed to get the list of databases."""


class DatabasePropertyError(RequestError):
    """Failed to get the database property."""


class DatabaseGetError(RequestError):
    """Failed to get the database."""


class DatabaseCreateError(RequestError):
    """Failed to create the database."""


class DatabaseDeleteError(RequestError):
    """Failed to delete the database."""


###################
# User Exceptions #
###################


class UserGetAllError(RequestError):
    """Failed to get the list of users."""


class UserGetError(RequestError):
    """Failed to get the user."""


class UserCreateError(RequestError):
    """Failed to create the user."""


class UserUpdateError(RequestError):
    """Failed to update the user."""


class UserReplaceError(RequestError):
    """Failed to replace the user."""


class UserDeleteError(RequestError):
    """Failed to delete the user."""


#########################
# Collection Exceptions #
#########################


class CollectionCorruptedError(Exception):
    """The collection is corrupted (i.e. its status is ``unknown``)."""


class CollectionNotFoundError(NotFoundError):
    """Failed to find the collection."""


class CollectionListError(RequestError):
    """Failed to get the list of collections."""


class CollectionGetError(RequestError):
    """Failed to get the collection."""


class CollectionChecksumError(RequestError):
    """Failed to get the collection checksum."""


class CollectionCreateError(RequestError):
    """Failed to create the collection."""


class CollectionDeleteError(RequestError):
    """Failed to delete the collection"""


class CollectionUpdateError(RequestError):
    """Failed to update the collection."""


class CollectionRenameError(RequestError):
    """Failed to rename the collection."""


class CollectionTruncateError(RequestError):
    """Failed to truncate the collection."""


class CollectionLoadError(RequestError):
    """Failed to load the collection into memory."""


class CollectionUnloadError(RequestError):
    """Failed to unload the collection from memory."""


class CollectionRotateJournalError(RequestError):
    """Failed to rotate the journal of the collection."""


########################################
# Documents Import & Export Exceptions #
########################################


class DocumentsImportError(RequestError):
    """Failed to bulk import documents/edges."""


class DocumentsExportError(RequestError):
    """Failed to bulk export documents/edges."""


#######################
# Document Exceptions #
#######################


class DocumentInvalidError(Exception):
    """The document is invalid (malformed)."""


class DocumentRevisionError(RequestError):
    """The expected and actual document revisions do not match."""


class DocumentGetError(RequestError):
    """Failed to get the document."""


class DocumentCreateError(RequestError):
    """Failed to create the document."""


class DocumentReplaceError(RequestError):
    """Failed to replace the document."""


class DocumentUpdateError(RequestError):
    """Failed to update the document."""


class DocumentDeleteError(RequestError):
    """Failed to delete the document."""


###################
# Edge Exceptions #
###################


class EdgeInvalidError(Exception):
    """The edge is invalid (malformed)."""


class EdgeRevisionError(RequestError):
    """The expected and actual edge revisions do not match."""


class EdgeGetError(RequestError):
    """Failed to get the edge."""


class EdgeCreateError(RequestError):
    """Failed to create the edge."""


class EdgeReplaceError(RequestError):
    """Failed to replace the edge."""


class EdgeUpdateError(RequestError):
    """Failed to update the edge."""


class EdgeDeleteError(RequestError):
    """Failed to delete the edge."""


#####################
# Vertex Exceptions #
#####################


class VertexInvalidError(RequestError):
    """The vertex is invalid (malformed)."""


class VertexRevisionError(RequestError):
    """The expected and actual vertex revisions do not match."""


class VertexGetError(RequestError):
    """Failed to get the vertex."""


class VertexCreateError(RequestError):
    """Failed to create the vertex."""


class VertexUpdateError(RequestError):
    """Failed to update the vertex."""


class VertexReplaceError(RequestError):
    """Failed to replace the vertex."""


class VertexDeleteError(RequestError):
    """Failed to delete the vertex."""


####################
# Index Exceptions #
####################


class IndexListError(RequestError):
    """Failed to get the list of indexes."""


class IndexCreateError(RequestError):
    """Failed to create the index."""


class IndexDeleteError(RequestError):
    """Failed to delete the index."""


########################
# AQL Query Exceptions #
########################


class AQLQueryExplainError(RequestError):
    """Failed to explain the AQL query."""


class AQLQueryValidateError(RequestError):
    """Failed to validate the AQL query."""


class AQLQueryExecuteError(RequestError):
    """Failed to execute the AQL query."""


#####################
# Cursor Exceptions #
#####################

class CursorGetNextError(RequestError):
    """Failed to get the next cursor result."""


class CursorDeleteError(RequestError):
    """Failed to delete the cursor."""


###########################
# AQL Function Exceptions #
###########################


class AQLFunctionListError(RequestError):
    """Failed to get the list of AQL functions."""


class AQLFunctionCreateError(RequestError):
    """Failed to create the AQL function."""


class AQLFunctionDeleteError(RequestError):
    """Failed to delete the AQL function."""


###########################
# Simple Query Exceptions #
###########################


class SimpleQueryGetByExampleError(RequestError):
    """Failed to execute the ``by-example`` simple query."""


class SimpleQueryFirstExampleError(RequestError):
    """Failed to execute the ``first-example`` simple query."""


class SimpleQueryReplaceByExampleError(RequestError):
    """Failed to execute the ``replace-by-example`` simple query."""


class SimpleQueryUpdateByExampleError(RequestError):
    """Failed to execute the ``update-by-example`` simple query."""


class SimpleQueryDeleteByExampleError(RequestError):
    """Failed to execute the ``Delete-by-example`` simple query."""


class SimpleQueryFirstError(RequestError):
    """Failed to execute the ``first`` simple query."""


class SimpleQueryLastError(RequestError):
    """Failed to execute the ``last`` simple query."""


class SimpleQueryAllError(RequestError):
    """Failed to execute the `all`` simple query."""


class SimpleQueryAnyError(RequestError):
    """Failed to execute the ``any`` simple query."""


class SimpleQueryRangeError(RequestError):
    """Failed to execute the ``range`` simple query."""


class SimpleQueryNearError(RequestError):
    """Failed to execute the ``near`` simple query."""


class SimpleQueryWithinError(RequestError):
    """Failed to execute the ``within`` simple query."""


class SimpleQueryFullTextError(RequestError):
    """Failed to execute the ``fulltext`` simple query."""


class SimpleQueryLookupByKeysError(RequestError):
    """Failed to execute the ``lookup-by-keys`` simple query."""


class SimpleQueryDeleteByKeysError(RequestError):
    """Failed to execute the ``Delete-by-keys`` simple query."""


class SimpleQueryError(RequestError):
    """Failed to execute a simple query."""


##########################
# Transaction Exceptions #
##########################


class TransactionExecuteError(RequestError):
    """Failed to execute a transaction."""


####################
# Batch Exceptions #
####################


class BatchInvalidError(Exception):
    """The batch request is invalid (malformed)."""


class BatchExecuteError(RequestError):
    """Failed to execute a batch request."""


####################
# Graph Exceptions #
####################


class GraphNotFoundError(NotFoundError):
    """Failed to find the graph."""


class GraphListError(RequestError):
    """Failed to get the list of graphs."""


class GraphGetError(RequestError):
    """Failed to get the graph."""


class GraphCreateError(RequestError):
    """Failed to create the graph."""


class GraphDeleteError(RequestError):
    """Failed to delete the graph."""


class GraphPropertyError(RequestError):
    """Failed to get the graph property."""


class GraphTraversalError(RequestError):
    """Failed to execute the graph traversal."""


################################
# Vertex Collection Exceptions #
################################


class VertexCollectionListError(RequestError):
    """Failed to get the list of vertex collections."""


class VertexCollectionCreateError(RequestError):
    """Failed to create the vertex collection."""


class VertexCollectionDeleteError(RequestError):
    """Failed to delete the vertex collection."""


#########################################
# Edge Collection/Definition Exceptions #
#########################################


class EdgeDefinitionListError(RequestError):
    """Failed to get the list of edge definitions."""


class EdgeDefinitionCreateError(RequestError):
    """Failed to create the edge definition."""


class EdgeDefinitionReplaceError(RequestError):
    """Failed to replace the edge definition."""


class EdgeDefinitionDeleteError(RequestError):
    """Failed to delete the edge definition."""


##########################################
# Administration & Monitoring Exceptions #
##########################################


class LogGetError(RequestError):
    """Failed to get the global log."""


class RountingInfoReloadError(RequestError):
    """Failed to reload the routing information."""


class StatisticsGetError(RequestError):
    """Failed to get the server statistics."""


class StatisticsDescriptionGetError(RequestError):
    """Failed to get the statistics description."""


class ServerRoleGetError(RequestError):
    """Failed to get the role of the server in a cluster."""


