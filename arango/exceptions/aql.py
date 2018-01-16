from arango.exceptions import ArangoError


class AQLError(ArangoError):
    """Base class for errors in AQL queries"""


class AQLQueryExplainError(AQLError):
    """Failed to explain the AQL query."""


class AQLQueryValidateError(AQLError):
    """Failed to validate the AQL query."""


class AQLQueryExecuteError(AQLError):
    """Failed to execute the AQL query."""


class AQLCacheClearError(AQLError):
    """Failed to clear the AQL query cache."""


class AQLCachePropertiesError(AQLError):
    """Failed to retrieve the AQL query cache properties."""


class AQLCacheConfigureError(AQLError):
    """Failed to configure the AQL query cache properties."""


class AQLFunctionListError(AQLError):
    """Failed to retrieve the list of AQL user functions."""


class AQLFunctionCreateError(AQLError):
    """Failed to create the AQL user function."""


class AQLFunctionDeleteError(AQLError):
    """Failed to delete the AQL user function."""
