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


class ArangoDatabaseCreateError(ArangoRequestError):
    """Failed to create the database."""


class ArangoDatabaseDeleteError(ArangoRequestError):
    """Failed to delete the database."""

###############
# Collections #
###############


class ArangoCollectionNotFoundError(ArangoNotFoundError):
    """Failed to locate the collection."""


class ArangoCollectionListError(ArangoRequestError):
    """Failed to retrieve the collection list."""


class ArangoCollectionPropertyError(ArangoRequestError):
    """Failed to retrieve the collection property."""


class ArangoCollectionGetChecksumError(ArangoRequestError):
    """Failed to retrieve the collection checksum."""


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


class ArangoRevisionMismatchError(ArangoRequestError):
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


class ArangoDocumentCreateError(ArangoRequestError):
    """Failed to create the ArangoDB document(s)."""


class ArangoDocumentReplaceError(ArangoRequestError):
    """Failed to replace the ArangoDB document(s)."""


class ArangoDocumentPatchError(ArangoRequestError):
    """Failed to patch the ArangoDB document(s)."""


class ArangoDocumentDeleteError(ArangoRequestError):
    """Failed to delete the ArangoDB document(s)."""


#########
# Edges #
#########

class ArangoEdgeInvalidError(Exception):
    """The edge is invalid."""


class ArangoEdgeGetError(ArangoRequestError):
    """Failed to get the ArangoDB edge(s)."""


class ArangoEdgeCreateError(ArangoRequestError):
    """Failed to create the ArangoDB edge(s)."""


class ArangoEdgeReplaceError(ArangoRequestError):
    """Failed to replace the ArangoDB edge(s)."""


class ArangoEdgePatchError(ArangoRequestError):
    """Failed to patch the ArangoDB edge(s)."""


class ArangoEdgeDeleteError(ArangoRequestError):
    """Failed to delete the ArangoDB edge(s)."""

###########
# Indexes #
###########

class ArangoIndexListError(ArangoRequestError):
    """Failed to list all the collections."""


class ArangoIndexCreateError(ArangoRequestError):
    """Failed to create the index."""


class ArangoIndexDeleteError(ArangoRequestError):
    """Failed to delete the index."""

###############
# AQL Queries #
###############

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

################
# Transactions #
################

class ArangoTransactionError(ArangoRequestError):
    """Failed to execute a transaction."""

##########
# Graphs #
##########

class ArangoGraphNotFoundError(ArangoNotFoundError):
    """Failed to find the grpah."""


class ArangoGraphListError(ArangoRequestError):
    """Failed to list the graphs."""


class ArangoGraphGetError(ArangoRequestError):
    """Failed to retrieve the graph."""


class ArangoGraphCreateError(ArangoRequestError):
    """Failed to create the graph."""


class ArangoGraphDeleteError(ArangoRequestError):
    """Failed to drop the graph."""


class ArangoGraphPropertiesError(ArangoRequestError):
    """Failed to retrieve the properties of the graph."""

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

class ArangoEdgeCollectionListError(ArangoRequestError):
    """Failed to list the edge collections."""


class ArangoEdgeDefinitionAddError(ArangoRequestError):
    """Failed to add a new edge definition to the graph."""


class ArangoEdgeDefinitionReplaceError(ArangoRequestError):
    """Failed to replace the edge definition in the graph."""


class ArangoEdgeDefinitionRemoveError(ArangoRequestError):
    """Failed to remove a edge definition from the graph."""

############
# Vertices #
############


class ArangoVertexInvalidError(ArangoRequestError):
    """The vertex is invalid."""


class ArangoVertexGetError(ArangoRequestError):
    """Failed to get the vertex."""


class ArangoVertexCreateError(ArangoRequestError):
    """Failed to create the vertex."""


class ArangoVertexPatchError(ArangoRequestError):
    """Failed to modify the vertex."""


class ArangoVertexReplaceError(ArangoRequestError):
    """Failed to replace the vertex."""


class ArangoVertexDeleteError(ArangoRequestError):
    """Failed to delete the vertex."""


#########
# Edges #
#########


class ArangoEdgeGetError(ArangoRequestError):
    """Failed to get the edge."""


class ArangoEdgeCreateError(ArangoRequestError):
    """Failed to create the edge."""


class ArangoEdgeModifyError(ArangoRequestError):
    """Failed to modify the edge."""


class ArangoEdgeReplaceError(ArangoRequestError):
    """Failed to modify the edge."""


class ArangoEdgeDeleteError(ArangoRequestError):
    """Failed to delete the edge."""