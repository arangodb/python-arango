from arango.exceptions import ArangoError


class PregelError(ArangoError):
    """Base class for errors in Pregel queries"""


class PregelJobCreateError(PregelError):
    """Failed to start/create a Pregel job."""


class PregelJobGetError(PregelError):
    """Failed to retrieve a Pregel job."""


class PregelJobDeleteError(PregelError):
    """Failed to cancel/delete a Pregel job."""
