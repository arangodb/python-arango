from arango.exceptions import ArangoError


class DatabaseError(ArangoError):
    """Base class for errors in Database queries"""


class DatabaseListError(DatabaseError):
    """Failed to retrieve the list of databases."""


class DatabasePropertiesError(DatabaseError):
    """Failed to retrieve the database options."""


class DatabaseCreateError(DatabaseError):
    """Failed to create the database."""


class DatabaseDeleteError(DatabaseError):
    """Failed to delete the database."""
