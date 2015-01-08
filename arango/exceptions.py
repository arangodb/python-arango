"""ArangoDB Exception."""


class ArangoRequestError(Exception):
    """Base ArangoDB request exception class."""

    def __init__(self, res):
        if res.obj is not None and "errorMessage" in res.obj:
            message = res.obj["errorMessage"]
        else:
            message = "no message"
        super(ArangoRequestError, self).__init__(
            "{message} ({status_code})".format(
                message=message,
                status_code=res.status_code
            )
        )
        self.status_code = res.status_code


class ArangoNotFoundError(KeyError):
    """Base ArangoDB "not found" exception class."""

    def __init__(self, name):
        super(ArangoNotFoundError, self).__init__(name)


##############
# Connection #
##############


class ArangoConnectionError(Exception):
    """Failed to connect to ArangoDB."""


class VersionGetError(ArangoRequestError):
    """Failed to retrieve the version."""


#############
# Databases #
#############


class DatabaseNotFoundError(ArangoNotFoundError):
    """Failed to locate database."""


class DatabaseListError(ArangoRequestError):
    """Failed to retrieve the database list."""


class DatabasePropertyError(ArangoRequestError):
    """Failed to retrieve the database property."""


class DatabaseAddError(ArangoRequestError):
    """Failed to add the database."""


class DatabaseRemoveError(ArangoRequestError):
    """Failed to remove the database."""

###############
# Collections #
###############

class CollectionCorruptedError(Exception):
    """The collection is corrupted (unknown status)."""


class CollectionNotFoundError(ArangoNotFoundError):
    """Failed to locate the collection."""


class CollectionListError(ArangoRequestError):
    """Failed to retrieve the collection list."""


class CollectionPropertyError(ArangoRequestError):
    """Failed to retrieve the collection property."""


class CollectionGetChecksumError(ArangoRequestError):
    """Failed to retrieve the collection checksum."""


class CollectionAddError(ArangoRequestError):
    """Failed to add the collection."""


class CollectionRemoveError(ArangoRequestError):
    """Failed to remove the collection"""


class CollectionModifyError(ArangoRequestError):
    """Failed to modify the collection."""


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


class CollectionBulkImportError(ArangoRequestError):
    """Failed to bulk import documents/edges"""

#############
# Documents #
#############

class DocumentInvalidError(Exception):
    """The document is invalid."""


class RevisionMismatchError(ArangoRequestError):
    """There was a mismatch between expected and actual revision."""


class DocumentGetError(ArangoRequestError):
    """Failed to get the ArangoDB document(s)."""


class DocumentAddError(ArangoRequestError):
    """Failed to add the ArangoDB document(s)."""


class DocumentReplaceError(ArangoRequestError):
    """Failed to replace the ArangoDB document(s)."""


class DocumentUpdateError(ArangoRequestError):
    """Failed to update the ArangoDB document(s)."""


class DocumentRemoveError(ArangoRequestError):
    """Failed to remove the ArangoDB document(s)."""


#########
# Edges #
#########

class EdgeInvalidError(Exception):
    """The edge is invalid."""


class EdgeGetError(ArangoRequestError):
    """Failed to get the ArangoDB edge(s)."""


class EdgeAddError(ArangoRequestError):
    """Failed to add the ArangoDB edge(s)."""


class EdgeReplaceError(ArangoRequestError):
    """Failed to replace the ArangoDB edge(s)."""


class EdgeUpdateError(ArangoRequestError):
    """Failed to update the ArangoDB edge(s)."""


class EdgeRemoveError(ArangoRequestError):
    """Failed to remove the ArangoDB edge(s)."""


############
# Vertices #
############


class VertexInvalidError(ArangoRequestError):
    """The vertex is invalid."""


class VertexGetError(ArangoRequestError):
    """Failed to get the vertex."""


class VertexAddError(ArangoRequestError):
    """Failed to add the vertex."""


class VertexUpdateError(ArangoRequestError):
    """Failed to modify the vertex."""


class VertexReplaceError(ArangoRequestError):
    """Failed to replace the vertex."""


class VertexRemoveError(ArangoRequestError):
    """Failed to remove the vertex."""


###########
# Indexes #
###########

class IndexListError(ArangoRequestError):
    """Failed to list all the collections."""


class IndexAddError(ArangoRequestError):
    """Failed to add the index."""


class IndexRemoveError(ArangoRequestError):
    """Failed to remove the index."""

###########
# Queries #
###########

class QueryExplainError(ArangoRequestError):
    """Failed to explain the query."""


class QueryValidateError(ArangoRequestError):
    """Failed to validate the query."""


class QueryExecuteError(ArangoRequestError):
    """Failed to execute the query."""


class CursorDeleteError(ArangoRequestError):
    """Failed to remove the query cursor."""


class AQLFunctionListError(ArangoRequestError):
    """Failed to get the list of AQL functions."""


class AQLFunctionAddError(ArangoRequestError):
    """Failed to add the AQL function."""


class AQLFunctionRemoveError(ArangoRequestError):
    """Failed to remove the AQL function."""

##################
# Simple Queries #
##################

class SimpleQueryGetByExampleError(ArangoRequestError):
    """Failed to execute the ``by-example`` simple query."""


class SimpleQueryFirstExampleError(ArangoRequestError):
    """Failed to execute the ``first-example`` simple query."""


class SimpleQueryReplaceByExampleError(ArangoRequestError):
    """Failed to execute the ``replace-by-example`` simple query."""


class SimpleQueryUpdateByExampleError(ArangoRequestError):
    """Failed to execute the ``update-by-example`` simple query."""


class SimpleQueryRemoveByExampleError(ArangoRequestError):
    """Failed to execute the ``remove-by-example`` simple query."""


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
    """Failed to execute a ``fulltext`` query."""


class SimpleQueryError(ArangoRequestError):
    """Failed to execute a simple query."""

################
# Transactions #
################

class TransactionExecuteError(ArangoRequestError):
    """Failed to execute a transaction."""

###########
# Batches #
###########

class BatchExecuteError(ArangoRequestError):
    """Failed to execute a batch request."""

##########
# Graphs #
##########

class GraphNotFoundError(ArangoNotFoundError):
    """Failed to find the grpah."""


class GraphListError(ArangoRequestError):
    """Failed to list the graphs."""


class GraphGetError(ArangoRequestError):
    """Failed to retrieve the graph."""


class GraphAddError(ArangoRequestError):
    """Failed to add the graph."""


class GraphRemoveError(ArangoRequestError):
    """Failed to drop the graph."""


class GraphPropertiesError(ArangoRequestError):
    """Failed to retrieve the properties of the graph."""


class GraphTraversalError(ArangoRequestError):
    """Failed to traverse the graph."""

######################
# Vertex Collections #
######################

class VertexCollectionListError(ArangoRequestError):
    """Failed to list the vertex collections."""


class VertexCollectionAddError(ArangoRequestError):
    """Failed to add a new vertex collection to the graph."""


class VertexCollectionRemoveError(ArangoRequestError):
    """Failed to remove a vertex collection from the graph."""

################################
# Edge Collections/Definitions #
################################

class EdgeDefinitionListError(ArangoRequestError):
    """Failed to list the edge collections."""


class EdgeDefinitionAddError(ArangoRequestError):
    """Failed to add a new edge definition to the graph."""


class EdgeDefinitionReplaceError(ArangoRequestError):
    """Failed to replace the edge definition in the graph."""


class EdgeDefinitionRemoveError(ArangoRequestError):
    """Failed to remove a edge definition from the graph."""
