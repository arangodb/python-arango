from arango_internals.exceptions import ArangoError


class IndexError(ArangoError):
    """Base class for errors in Index queries"""


class IndexListError(IndexError):
    """Failed to retrieve the list of indexes in the collection."""


class IndexCreateError(IndexError):
    """Failed to create the index in the collection."""


class IndexDeleteError(IndexError):
    """Failed to delete the index from the collection."""
