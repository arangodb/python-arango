from arango.exceptions import ArangoError


class ServerError(ArangoError):
    """Base class for Server errors"""


class ServerConnectionError(ServerError):
    """Failed to connect to the ArangoDB instance."""


class ServerEndpointsError(ServerError):
    """Failed to retrieve the ArangoDB server endpoints."""


class ServerVersionError(ServerError):
    """Failed to retrieve the ArangoDB server version."""


class ServerDetailsError(ServerError):
    """Failed to retrieve the ArangoDB server details."""


class ServerTimeError(ServerError):
    """Failed to return the current ArangoDB system time."""


class ServerEchoError(ServerError):
    """Failed to return the last request."""


class ServerSleepError(ServerError):
    """Failed to suspend the ArangoDB server."""


class ServerShutdownError(ServerError):
    """Failed to initiate a clean shutdown sequence."""


class ServerRunTestsError(ServerError):
    """Failed to execute the specified tests on the server."""


class ServerExecuteError(ServerError):
    """Failed to execute a the given Javascript program on the server."""


class ServerRequiredDBVersionError(ServerError):
    """Failed to retrieve the required database version."""


class ServerReadLogError(ServerError):
    """Failed to retrieve the global log."""


class ServerLogLevelError(ServerError):
    """Failed to return the log level."""


class ServerLogLevelSetError(ServerError):
    """Failed to set the log level."""


class ServerReloadRoutingError(ServerError):
    """Failed to reload the routing information."""


class ServerStatisticsError(ServerError):
    """Failed to retrieve the server statistics."""


class ServerRoleError(ServerError):
    """Failed to retrieve the role of the server in a cluster."""
