from arango_internals.exceptions import ArangoError


class CursorError(ArangoError):
    """Base class for errors in BaseCursor queries"""


class CursorNextError(CursorError):
    """Failed to retrieve the next cursor result."""


class CursorCloseError(CursorError):
    """Failed to delete the cursor from the server."""
