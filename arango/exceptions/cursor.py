from arango.exceptions import ArangoError


class CursorError(ArangoError):
    """Base class for errors in Cursor queries"""


class CursorNextError(CursorError):
    """Failed to retrieve the next cursor result."""


class CursorCloseError(CursorError):
    """Failed to delete the cursor from the server."""
