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


class ArangoVersionError(ArangoRequestError):
    """Failed to retrieve the version."""


#############
# Databases #
#############


class ArangoDatabaseNotFoundError(ArangoNotFoundError):
    """Failed to locate database."""


class ArangoDatabaseListError(ArangoRequestError):
    """Failed to retrieve the database list."""


class ArangoDatabasePropertyError(ArangoRequestError):
    """Failed to retrieve the database property."""


class ArangoDatabaseAddError(ArangoRequestError):
    """Failed to add the database."""


class ArangoDatabaseRemoveError(ArangoRequestError):
    """Failed to remove the database."""

###############
# Collections #
###############

class ArangoCollectionCorruptedError(Exception):
    """The collection is corrupted (unknown status)."""


class ArangoCollectionNotFoundError(ArangoNotFoundError):
    """Failed to locate the collection."""


class ArangoCollectionListError(ArangoRequestError):
    """Failed to retrieve the collection list."""


class ArangoCollectionPropertyError(ArangoRequestError):
    """Failed to retrieve the collection property."""


class ArangoCollectionGetChecksumError(ArangoRequestError):
    """Failed to retrieve the collection checksum."""


class ArangoCollectionAddError(ArangoRequestError):
    """Failed to add the collection."""


class ArangoCollectionRemoveError(ArangoRequestError):
    """Failed to remove the collection"""


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


class ArangoDocumentRevisionError(ArangoRequestError):
    """There was a mismatch between expected and actual revision."""


class ArangoCollectionBulkImportError(ArangoRequestError):
    """Failed to bulk import documents/edges"""

#############
# Documents #
#############

class ArangoDocumentInvalidError(Exception):
    """The document is invalid."""


class ArangoDocumentGetError(ArangoRequestError):
    """Failed to get the ArangoDB document(s)."""


class ArangoDocumentAddError(ArangoRequestError):
    """Failed to add the ArangoDB document(s)."""


class ArangoDocumentReplaceError(ArangoRequestError):
    """Failed to replace the ArangoDB document(s)."""


class ArangoDocumentUpdateError(ArangoRequestError):
    """Failed to update the ArangoDB document(s)."""


class ArangoDocumentRemoveError(ArangoRequestError):
    """Failed to remove the ArangoDB document(s)."""


#########
# Edges #
#########

class ArangoEdgeInvalidError(Exception):
    """The edge is invalid."""


class ArangoEdgeGetError(ArangoRequestError):
    """Failed to get the ArangoDB edge(s)."""


class ArangoEdgeAddError(ArangoRequestError):
    """Failed to add the ArangoDB edge(s)."""


class ArangoEdgeReplaceError(ArangoRequestError):
    """Failed to replace the ArangoDB edge(s)."""


class ArangoEdgeUpdateError(ArangoRequestError):
    """Failed to update the ArangoDB edge(s)."""


class ArangoEdgeRemoveError(ArangoRequestError):
    """Failed to remove the ArangoDB edge(s)."""


############
# Vertices #
############


class ArangoVertexInvalidError(ArangoRequestError):
    """The vertex is invalid."""


class ArangoVertexGetError(ArangoRequestError):
    """Failed to get the vertex."""


class ArangoVertexAddError(ArangoRequestError):
    """Failed to add the vertex."""


class ArangoVertexUpdateError(ArangoRequestError):
    """Failed to modify the vertex."""


class ArangoVertexReplaceError(ArangoRequestError):
    """Failed to replace the vertex."""


class ArangoVertexRemoveError(ArangoRequestError):
    """Failed to remove the vertex."""


###########
# Indexes #
###########

class ArangoIndexListError(ArangoRequestError):
    """Failed to list all the collections."""


class ArangoIndexAddError(ArangoRequestError):
    """Failed to add the index."""


class ArangoIndexRemoveError(ArangoRequestError):
    """Failed to remove the index."""

###########
# Queries #
###########

class ArangoQueryExplainError(ArangoRequestError):
    """Failed to explain the query."""


class ArangoQueryValidateError(ArangoRequestError):
    """Failed to validate the query."""


class ArangoQueryExecuteError(ArangoRequestError):
    """Failed to execute the query."""


class ArangoCursorDeleteError(ArangoRequestError):
    """Failed to remove the query cursor."""


class ArangoAQLFunctionListError(ArangoRequestError):
    """Failed to get the list of AQL functions."""


class ArangoAQLFunctionAddError(ArangoRequestError):
    """Failed to add the AQL function."""


class ArangoAQLFunctionRemoveError(ArangoRequestError):
    """Failed to remove the AQL function."""

##################
# Simple Queries #
##################

class ArangoSimpleQueryGetByExampleError(ArangoRequestError):
    """Failed to execute the ``by-example`` simple query."""


class ArangoSimpleQueryFirstExampleError(ArangoRequestError):
    """Failed to execute the ``first-example`` simple query."""


class ArangoSimpleQueryReplaceByExampleError(ArangoRequestError):
    """Failed to execute the ``replace-by-example`` simple query."""


class ArangoSimpleQueryUpdateByExampleError(ArangoRequestError):
    """Failed to execute the ``update-by-example`` simple query."""


class ArangoSimpleQueryRemoveByExampleError(ArangoRequestError):
    """Failed to execute the ``remove-by-example`` simple query."""


class ArangoSimpleQueryFirstError(ArangoRequestError):
    """Failed to execute the ``first`` simple query."""


class ArangoSimpleQueryLastError(ArangoRequestError):
    """Failed to execute the ``last`` simple query."""


class ArangoSimpleQueryAllError(ArangoRequestError):
    """Failed to execute the `all`` simple query."""


class ArangoSimpleQueryAnyError(ArangoRequestError):
    """Failed to execute the ``any`` simple query."""


class ArangoSimpleQueryRangeError(ArangoRequestError):
    """Failed to execute the ``range`` simple query."""


class ArangoSimpleQueryNearError(ArangoRequestError):
    """Failed to execute the ``near`` simple query."""


class ArangoSimpleQueryWithinError(ArangoRequestError):
    """Failed to execute the ``within`` simple query."""


class ArangoSimpleQueryFullTextError(ArangoRequestError):
    """Failed to execute a ``fulltext`` query."""


class ArangoSimpleQueryError(ArangoRequestError):
    """Failed to execute a simple query."""

################
# Transactions #
################

class ArangoTransactionExecuteError(ArangoRequestError):
    """Failed to execute a transaction."""

###########
# Batches #
###########

class ArangoBatchExecuteError(ArangoRequestError):
    """Failed to execute a batch request."""

##########
# Graphs #
##########

class ArangoGraphNotFoundError(ArangoNotFoundError):
    """Failed to find the grpah."""


class ArangoGraphListError(ArangoRequestError):
    """Failed to list the graphs."""


class ArangoGraphGetError(ArangoRequestError):
    """Failed to retrieve the graph."""


class ArangoGraphAddError(ArangoRequestError):
    """Failed to add the graph."""


class ArangoGraphRemoveError(ArangoRequestError):
    """Failed to drop the graph."""


class ArangoGraphPropertiesError(ArangoRequestError):
    """Failed to retrieve the properties of the graph."""


class ArangoGraphTraversalError(ArangoRequestError):
    """Failed to traverse the graph."""

######################
# Vertex Collections #
######################

class ArangoVertexCollectionListError(ArangoRequestError):
    """Failed to list the vertex collections."""


class ArangoVertexCollectionAddError(ArangoRequestError):
    """Failed to add a new vertex collection to the graph."""


class ArangoVertexCollectionRemoveError(ArangoRequestError):
    """Failed to remove a vertex collection from the graph."""

################################
# Edge Collections/Definitions #
################################

class ArangoEdgeDefinitionListError(ArangoRequestError):
    """Failed to list the edge collections."""


class ArangoEdgeDefinitionAddError(ArangoRequestError):
    """Failed to add a new edge definition to the graph."""


class ArangoEdgeDefinitionReplaceError(ArangoRequestError):
    """Failed to replace the edge definition in the graph."""


class ArangoEdgeDefinitionRemoveError(ArangoRequestError):
    """Failed to remove a edge definition from the graph."""
