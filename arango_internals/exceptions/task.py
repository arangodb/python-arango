from arango_internals.exceptions import ArangoError


class TaskError(ArangoError):
    """Base class for errors in Task queries"""


class TaskListError(TaskError):
    """Failed to list the active server tasks."""


class TaskGetError(TaskError):
    """Failed to retrieve the active server task."""


class TaskCreateError(TaskError):
    """Failed to create a server task."""


class TaskDeleteError(TaskError):
    """Failed to delete a server task."""
