from arango_internals.exceptions import ArangoError


class UserError(ArangoError):
    """Base class for errors in User queries"""


class UserListError(UserError):
    """Failed to retrieve the users."""


class UserGetError(UserError):
    """Failed to retrieve the user."""


class UserCreateError(UserError):
    """Failed to create the user."""


class UserUpdateError(UserError):
    """Failed to update the user."""


class UserReplaceError(UserError):
    """Failed to replace the user."""


class UserDeleteError(UserError):
    """Failed to delete the user."""


class UserAccessError(UserError):
    """Failed to retrieve the names of databases user can access."""


class UserGrantAccessError(UserError):
    """Failed to grant user access to a database."""


class UserRevokeAccessError(UserError):
    """Failed to revoke user access to a database."""
