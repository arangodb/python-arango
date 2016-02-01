from __future__ import absolute_import, unicode_literals

from six import string_types as string

from arango.response import Response


class ArangoError(Exception):
    """Base class for all ArangoDB exceptions.

    :param data: the response object or string
    :type data: arango.response.Response | str
    """

    def __init__(self, data, message=None):
        if isinstance(data, Response):
            # Get the ArangoDB error message if provided
            if message is not None:
                error_message = message
            elif data.error_message is not None:
                error_message = data.error_message
            elif data.status_text is not None:
                error_message = data.status_text
            else:
                error_message = "request failed"

            # Get the ArangoDB error number if provided
            self.error_code = data.error_code

            # Build the error message for the exception
            if self.error_code is None:
                error_message = '[HTTP {}] {}'.format(
                    data.status_code,
                    error_message
                )
            else:
                error_message = '[HTTP {}][ERR {}] {}'.format(
                    data.status_code,
                    self.error_code,
                    error_message
                )
            # Generate the error message for the exception
            super(ArangoError, self).__init__(error_message)
            self.message = error_message
            self.http_method = data.method
            self.url = data.url
            self.http_code = data.status_code
            self.http_headers = data.headers
        elif isinstance(data, string):
            super(ArangoError, self).__init__(data)
            self.message = data
            self.error_code = None
            self.url = None
            self.http_method = None
            self.http_code = None
            self.http_headers = None


#####################
# Server Exceptions #
#####################


class ServerConnectionError(ArangoError):
    """Failed to connect to the ArangoDB instance."""


class ServerGetEndpointsError(ArangoError):
    """Failed to retrieve the ArangoDB server endpoints."""


class ServerGetVersionError(ArangoError):
    """Failed to retrieve the ArangoDB server version."""


class ServerGetDetailsError(ArangoError):
    """Failed to retrieve the ArangoDB server details."""


class ServerGetTimeError(ArangoError):
    """Failed to return the current ArangoDB system time."""


class ServerEchoError(ArangoError):
    """Failed to return the last request."""


class ServerSleepError(ArangoError):
    """Failed to suspend the ArangoDB server."""


class ServerShutdownError(ArangoError):
    """Failed to initiate a clean shutdown sequence."""


class ServerRunTestsError(ArangoError):
    """Failed to execute the specified tests on the server."""


class ServerExecuteError(ArangoError):
    """Failed to execute a the given Javascript program on the server."""


class ServerGetRequiredVersionError(ArangoError):
    """Failed to retrieve the required database version."""


class ServerReadLogError(ArangoError):
    """Failed to retrieve the global log."""


class ServerReloadRoutingError(ArangoError):
    """Failed to reload the routing information."""


class ServerGetStatisticsError(ArangoError):
    """Failed to retrieve the server statistics."""


class ServerGetRoleError(ArangoError):
    """Failed to retrieve the role of the server in a cluster."""


##############################
# Write-Ahead Log Exceptions #
##############################


class WALFlushError(ArangoError):
    """Failed to flush the write-ahead log."""


class WALGetPropertiesError(ArangoError):
    """Failed to retrieve the write-ahead log."""


class WALConfigureError(ArangoError):
    """Failed to configure the write-ahead log."""


###################
# Task Exceptions #
###################


class TasksListError(ArangoError):
    """Failed to list the active server tasks."""


class TaskGetError(ArangoError):
    """Failed to retrieve the active server task."""


class TaskCreateError(ArangoError):
    """Failed to create a server task."""


class TaskDeleteError(ArangoError):
    """Failed to delete a server task."""


#######################
# Database Exceptions #
#######################


class DatabasesListError(ArangoError):
    """Failed to retrieve the list of databases."""


class DatabaseGetPropertiesError(ArangoError):
    """Failed to retrieve the database options."""


class DatabaseCreateError(ArangoError):
    """Failed to create the database."""


class DatabaseDeleteError(ArangoError):
    """Failed to delete the database."""


###################
# User Exceptions #
###################


class UsersListError(ArangoError):
    """Failed to retrieve the users."""


class UserGetError(ArangoError):
    """Failed to retrieve the user."""


class UserCreateError(ArangoError):
    """Failed to create the user."""


class UserUpdateError(ArangoError):
    """Failed to update the user."""


class UserReplaceError(ArangoError):
    """Failed to replace the user."""


class UserDeleteError(ArangoError):
    """Failed to delete the user."""


class UserGrantAccessError(ArangoError):
    """Failed to grant user access to a database."""


class UserRevokeAccessError(ArangoError):
    """Failed to revoke user access to a database."""


#########################
# Collection Exceptions #
#########################


class CollectionsListError(ArangoError):
    """Failed to retrieve the list of collections."""


class CollectionGetCountError(ArangoError):
    """Failed to retrieve the count of the documents in the collections."""


class CollectionContainsError(ArangoError):
    """Failed to check whether a collection contains a document."""


class CollectionGetPropertiesError(ArangoError):
    """Failed to retrieve the collection properties."""


class CollectionConfigureError(ArangoError):
    """Failed to configure the collection properties."""


class CollectionGetStatisticsError(ArangoError):
    """Failed to retrieve the collection statistics."""


class CollectionGetRevisionError(ArangoError):
    """Failed to retrieve the collection revision."""


class CollectionGetChecksumError(ArangoError):
    """Failed to retrieve the collection checksum."""


class CollectionCreateError(ArangoError):
    """Failed to create the collection."""


class CollectionDeleteError(ArangoError):
    """Failed to delete the collection"""


class CollectionRenameError(ArangoError):
    """Failed to rename the collection."""


class CollectionTruncateError(ArangoError):
    """Failed to truncate the collection."""


class CollectionLoadError(ArangoError):
    """Failed to load the collection into memory."""


class CollectionUnloadError(ArangoError):
    """Failed to unload the collection from memory."""


class CollectionRotateJournalError(ArangoError):
    """Failed to rotate the journal of the collection."""


class CollectionBadStatusError(ArangoError):
    """Unknown status was returned from the collection."""


#######################
# Document Exceptions #
#######################


class DocumentGetError(ArangoError):
    """Failed to retrieve the document."""


class DocumentInsertError(ArangoError):
    """Failed to insert the document."""


class DocumentReplaceError(ArangoError):
    """Failed to replace the document."""


class DocumentUpdateError(ArangoError):
    """Failed to update the document."""


class DocumentDeleteError(ArangoError):
    """Failed to delete the document."""


class DocumentRevisionError(ArangoError):
    """The expected and actual document revisions do not match."""


####################
# Index Exceptions #
####################


class IndexesListError(ArangoError):
    """Failed to retrieve the list of indexes in the collection."""


class IndexCreateError(ArangoError):
    """Failed to create the index in the collection."""


class IndexDeleteError(ArangoError):
    """Failed to delete the index from the collection."""


####################
# AQL Exceptions #
####################


class AQLQueryExplainError(ArangoError):
    """Failed to explain the AQL query."""


class AQLQueryValidateError(ArangoError):
    """Failed to validate the AQL query."""


class AQLQueryExecuteError(ArangoError):
    """Failed to execute the AQL query."""


class AQLCacheClearError(ArangoError):
    """Failed to clear the AQL query cache."""


class AQLCacheGetPropertiesError(ArangoError):
    """Failed to retrieve the AQL query cache properties."""


class AQLCacheConfigureError(ArangoError):
    """Failed to configure the AQL query cache properties."""


class AQLFunctionsListError(ArangoError):
    """Failed to retrieve the list of AQL user functions."""


class AQLFunctionCreateError(ArangoError):
    """Failed to create the AQL user function."""


class AQLFunctionDeleteError(ArangoError):
    """Failed to delete the AQL user function."""


#####################
# Cursor Exceptions #
#####################


class CursorNextError(ArangoError):
    """Failed to retrieve the next cursor result."""


class CursorCloseError(ArangoError):
    """Failed to delete the cursor from the server."""


##########################
# Transaction Exceptions #
##########################


class TransactionError(ArangoError):
    """Failed to execute a transaction."""


class TransactionsListError(ArangoError):
    """Failed to retrieve the list of running transactions."""


####################
# Batch Exceptions #
####################


class BatchExecuteError(ArangoError):
    """Failed to execute the batch request."""


####################
# Async Exceptions #
####################


class AsyncExecuteError(ArangoError):
    """Failed to execute the asynchronous request."""


class AsyncJobInvalidError(ArangoError):
    """Failed to retrieve the asynchronous job ID."""


class AsyncJobNotDoneError(ArangoError):
    """The asynchronous job is still pending in the queue."""


class AsyncJobNotFoundError(ArangoError):
    """Failed to find the asynchronous job (already deleted/fetched)"""


class AsyncJobCancelError(ArangoError):
    """Failed to cancel the asynchronous job."""


class AsyncJobGetStatusError(ArangoError):
    """Failed to retrieve the asynchronous job result from the server."""


class AsyncJobGetResultError(ArangoError):
    """Failed to pop the asynchronous job result from the server."""


class AsyncJobClearError(ArangoError):
    """Failed to delete the asynchronous job result from the server."""


####################
# Graph Exceptions #
####################


class GraphsListError(ArangoError):
    """Failed to retrieve the list of graphs."""


class GraphGetError(ArangoError):
    """Failed to retrieve the graph."""


class GraphCreateError(ArangoError):
    """Failed to create the graph."""


class GraphDeleteError(ArangoError):
    """Failed to delete the graph."""


class GraphGetPropertiesError(ArangoError):
    """Failed to retrieve the graph properties."""


class GraphTraverseError(ArangoError):
    """Failed to execute the graph traversal."""


class OrphanCollectionsListError(ArangoError):
    """Failed to retrieve the list of orphaned vertex collections."""


class VertexCollectionsListError(ArangoError):
    """Failed to retrieve the list of vertex collections."""


class VertexCollectionCreateError(ArangoError):
    """Failed to create the vertex collection."""


class VertexCollectionDeleteError(ArangoError):
    """Failed to delete the vertex collection."""


class EdgeDefinitionsListError(ArangoError):
    """Failed to retrieve the list of edge definitions."""


class EdgeDefinitionCreateError(ArangoError):
    """Failed to create the edge definition."""


class EdgeDefinitionReplaceError(ArangoError):
    """Failed to replace the edge definition."""


class EdgeDefinitionDeleteError(ArangoError):
    """Failed to delete the edge definition."""
