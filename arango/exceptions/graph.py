from arango.exceptions import ArangoError


class GraphError(ArangoError):
    """Base class for errors in Graph queries"""


class GraphListError(GraphError):
    """Failed to retrieve the list of graphs."""


class GraphGetError(GraphError):
    """Failed to retrieve the graph."""


class GraphCreateError(GraphError):
    """Failed to create the graph."""


class GraphDeleteError(GraphError):
    """Failed to delete the graph."""


class GraphPropertiesError(GraphError):
    """Failed to retrieve the graph properties."""


class GraphTraverseError(GraphError):
    """Failed to execute the graph traversal."""


class OrphanCollectionListError(GraphError):
    """Failed to retrieve the list of orphaned vertex collections."""


class VertexCollectionListError(GraphError):
    """Failed to retrieve the list of vertex collections."""


class VertexCollectionCreateError(GraphError):
    """Failed to create the vertex collection."""


class VertexCollectionDeleteError(GraphError):
    """Failed to delete the vertex collection."""


class EdgeDefinitionListError(GraphError):
    """Failed to retrieve the list of edge definitions."""


class EdgeDefinitionCreateError(GraphError):
    """Failed to create the edge definition."""


class EdgeDefinitionReplaceError(GraphError):
    """Failed to replace the edge definition."""


class EdgeDefinitionDeleteError(GraphError):
    """Failed to delete the edge definition."""
