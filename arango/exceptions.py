from typing import Optional

from arango.request import Request
from arango.response import Response


class ArangoError(Exception):
    """Base class for all exceptions in python-arango."""


class ArangoClientError(ArangoError):
    """Base class for errors originating from python-arango client.

    :param msg: Error message.
    :type msg: str

    :cvar source: Source of the error (always set to "client").
    :vartype source: str
    :ivar message: Error message.
    :vartype message: str
    """

    source = "client"

    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.message = msg
        self.error_message = None
        self.error_code = None
        self.url = None
        self.response = None
        self.request = None
        self.http_method = None
        self.http_code = None
        self.http_headers = None


class ArangoServerError(ArangoError):
    """Base class for errors originating from ArangoDB server.

    :param resp: HTTP response.
    :type resp: arango.response.Response
    :param msg: Error message override.
    :type msg: str

    :cvar source: Source of the error (always set to "server").
    :vartype source: str
    :ivar message: Exception message.
    :vartype message: str
    :ivar url: API URL.
    :vartype url: str
    :ivar response: HTTP response object.
    :vartype response: arango.response.Response
    :ivar request: HTTP request object.
    :vartype request: arango.request.Request
    :ivar http_method: HTTP method in lowercase (e.g. "post").
    :vartype http_method: str
    :ivar http_code: HTTP status code.
    :vartype http_code: int
    :ivar http_headers: Response headers.
    :vartype http_headers: dict
    :ivar error_code: Error code from ArangoDB server.
    :vartype error_code: int
    :ivar error_message: Raw error message from ArangoDB server.
    :vartype error_message: str
    """

    source = "server"

    def __init__(
        self, resp: Response, request: Request, msg: Optional[str] = None
    ) -> None:
        msg = msg or resp.error_message or resp.status_text
        self.error_message = resp.error_message
        self.error_code = resp.error_code
        if self.error_code is not None:
            msg = f"[HTTP {resp.status_code}][ERR {self.error_code}] {msg}"
        else:
            msg = f"[HTTP {resp.status_code}] {msg}"
            self.error_code = resp.status_code
        super().__init__(msg)
        self.message = msg
        self.url = resp.url
        self.response = resp
        self.request = request
        self.http_method = resp.method
        self.http_code = resp.status_code
        self.http_headers = resp.headers


##################
# AQL Exceptions #
##################


class AQLQueryListError(ArangoServerError):
    """Failed to retrieve running AQL queries."""


class AQLQueryExplainError(ArangoServerError):
    """Failed to parse and explain query."""


class AQLQueryValidateError(ArangoServerError):
    """Failed to parse and validate query."""


class AQLQueryExecuteError(ArangoServerError):
    """Failed to execute query."""


class AQLQueryKillError(ArangoServerError):
    """Failed to kill the query."""


class AQLQueryClearError(ArangoServerError):
    """Failed to clear slow AQL queries."""


class AQLQueryTrackingGetError(ArangoServerError):
    """Failed to retrieve AQL tracking properties."""


class AQLQueryTrackingSetError(ArangoServerError):
    """Failed to configure AQL tracking properties."""


class AQLCachePropertiesError(ArangoServerError):
    """Failed to retrieve query cache properties."""


class AQLCacheConfigureError(ArangoServerError):
    """Failed to configure query cache properties."""


class AQLCacheEntriesError(ArangoServerError):
    """Failed to retrieve AQL cache entries."""


class AQLCacheClearError(ArangoServerError):
    """Failed to clear the query cache."""


class AQLFunctionListError(ArangoServerError):
    """Failed to retrieve AQL user functions."""


class AQLFunctionCreateError(ArangoServerError):
    """Failed to create AQL user function."""


class AQLFunctionDeleteError(ArangoServerError):
    """Failed to delete AQL user function."""


class AQLQueryRulesGetError(ArangoServerError):
    """Failed to retrieve AQL query rules."""


##############################
# Async Execution Exceptions #
##############################


class AsyncExecuteError(ArangoServerError):
    """Failed to execute async API request."""


class AsyncJobListError(ArangoServerError):
    """Failed to retrieve async jobs."""


class AsyncJobCancelError(ArangoServerError):
    """Failed to cancel async job."""


class AsyncJobStatusError(ArangoServerError):
    """Failed to retrieve async job status."""


class AsyncJobResultError(ArangoServerError):
    """Failed to retrieve async job result."""


class AsyncJobClearError(ArangoServerError):
    """Failed to clear async job results."""


##############################
# Backup Exceptions #
##############################


class BackupCreateError(ArangoServerError):
    """Failed to create a backup."""


class BackupDeleteError(ArangoServerError):
    """Failed to delete a backup."""


class BackupDownloadError(ArangoServerError):
    """Failed to download a backup from remote repository."""


class BackupGetError(ArangoServerError):
    """Failed to retrieve backup details."""


class BackupRestoreError(ArangoServerError):
    """Failed to restore from backup."""


class BackupUploadError(ArangoServerError):
    """Failed to upload a backup to remote repository."""


##############################
# Batch Execution Exceptions #
##############################


class BatchStateError(ArangoClientError):
    """The batch object was in a bad state."""


class BatchJobResultError(ArangoClientError):
    """Failed to retrieve batch job result."""


class BatchExecuteError(ArangoServerError):
    """Failed to execute batch API request."""


#########################################
# Overload Control Execution Exceptions #
#########################################


class OverloadControlExecutorError(ArangoServerError):
    """Failed to execute overload controlled API request."""


#########################
# Collection Exceptions #
#########################


class CollectionListError(ArangoServerError):
    """Failed to retrieve collections."""


class CollectionInformationError(ArangoServerError):
    """Failed to retrieve collection information."""


class CollectionPropertiesError(ArangoServerError):
    """Failed to retrieve collection properties."""


class CollectionConfigureError(ArangoServerError):
    """Failed to configure collection properties."""


class CollectionShardsError(ArangoServerError):
    """Failed to retrieve collection shards."""


class CollectionStatisticsError(ArangoServerError):
    """Failed to retrieve collection statistics."""


class CollectionRevisionError(ArangoServerError):
    """Failed to retrieve collection revision."""


class CollectionChecksumError(ArangoServerError):
    """Failed to retrieve collection checksum."""


class CollectionCompactError(ArangoServerError):
    """Failed to compact collection."""


class CollectionCreateError(ArangoServerError):
    """Failed to create collection."""


class CollectionDeleteError(ArangoServerError):
    """Failed to delete collection."""


class CollectionRenameError(ArangoServerError):
    """Failed to rename collection."""


class CollectionTruncateError(ArangoServerError):
    """Failed to truncate collection."""


class CollectionLoadError(ArangoServerError):
    """Failed to load collection."""


class CollectionUnloadError(ArangoServerError):
    """Failed to unload collection."""


class CollectionRecalculateCountError(ArangoServerError):
    """Failed to recalculate document count."""


class CollectionResponsibleShardError(ArangoServerError):
    """Failed to retrieve responsible shard."""


#####################
# Cursor Exceptions #
#####################


class CursorStateError(ArangoClientError):
    """The cursor object was in a bad state."""


class CursorCountError(ArangoClientError, TypeError):
    """The cursor count was not enabled."""


class CursorEmptyError(ArangoClientError):
    """The current batch in cursor was empty."""


class CursorNextError(ArangoServerError):
    """Failed to retrieve the next result batch from server."""


class CursorCloseError(ArangoServerError):
    """Failed to delete the cursor result from server."""


#######################
# Database Exceptions #
#######################


class DatabaseListError(ArangoServerError):
    """Failed to retrieve databases."""


class DatabasePropertiesError(ArangoServerError):
    """Failed to retrieve database properties."""


class DatabaseCreateError(ArangoServerError):
    """Failed to create database."""


class DatabaseDeleteError(ArangoServerError):
    """Failed to delete database."""


class DatabaseSupportInfoError(ArangoServerError):
    """Failed to retrieve support info for deployment."""


class DatabaseCompactError(ArangoServerError):
    """Failed to compact databases."""


#######################
# Document Exceptions #
#######################


class DocumentParseError(ArangoClientError):
    """Failed to parse document input."""


class DocumentCountError(ArangoServerError):
    """Failed to retrieve document count."""


class DocumentInError(ArangoServerError):
    """Failed to check whether document exists."""


class DocumentGetError(ArangoServerError):
    """Failed to retrieve document."""


class DocumentKeysError(ArangoServerError):
    """Failed to retrieve document keys."""


class DocumentIDsError(ArangoServerError):
    """Failed to retrieve document IDs."""


class DocumentInsertError(ArangoServerError):
    """Failed to insert document."""


class DocumentReplaceError(ArangoServerError):
    """Failed to replace document."""


class DocumentUpdateError(ArangoServerError):
    """Failed to update document."""


class DocumentDeleteError(ArangoServerError):
    """Failed to delete document."""


class DocumentRevisionError(ArangoServerError):
    """The expected and actual document revisions mismatched."""


###################
# Foxx Exceptions #
###################


class FoxxServiceListError(ArangoServerError):
    """Failed to retrieve Foxx services."""


class FoxxServiceGetError(ArangoServerError):
    """Failed to retrieve Foxx service metadata."""


class FoxxServiceCreateError(ArangoServerError):
    """Failed to create Foxx service."""


class FoxxServiceUpdateError(ArangoServerError):
    """Failed to update Foxx service."""


class FoxxServiceReplaceError(ArangoServerError):
    """Failed to replace Foxx service."""


class FoxxServiceDeleteError(ArangoServerError):
    """Failed to delete Foxx services."""


class FoxxConfigGetError(ArangoServerError):
    """Failed to retrieve Foxx service configuration."""


class FoxxConfigUpdateError(ArangoServerError):
    """Failed to update Foxx service configuration."""


class FoxxConfigReplaceError(ArangoServerError):
    """Failed to replace Foxx service configuration."""


class FoxxDependencyGetError(ArangoServerError):
    """Failed to retrieve Foxx service dependencies."""


class FoxxDependencyUpdateError(ArangoServerError):
    """Failed to update Foxx service dependencies."""


class FoxxDependencyReplaceError(ArangoServerError):
    """Failed to replace Foxx service dependencies."""


class FoxxScriptListError(ArangoServerError):
    """Failed to retrieve Foxx service scripts."""


class FoxxScriptRunError(ArangoServerError):
    """Failed to run Foxx service script."""


class FoxxTestRunError(ArangoServerError):
    """Failed to run Foxx service tests."""


class FoxxDevModeEnableError(ArangoServerError):
    """Failed to enable development mode for Foxx service."""


class FoxxDevModeDisableError(ArangoServerError):
    """Failed to disable development mode for Foxx service."""


class FoxxReadmeGetError(ArangoServerError):
    """Failed to retrieve Foxx service readme."""


class FoxxSwaggerGetError(ArangoServerError):
    """Failed to retrieve Foxx service swagger."""


class FoxxDownloadError(ArangoServerError):
    """Failed to download Foxx service bundle."""


class FoxxCommitError(ArangoServerError):
    """Failed to commit local Foxx service state."""


####################
# Graph Exceptions #
####################


class GraphListError(ArangoServerError):
    """Failed to retrieve graphs."""


class GraphCreateError(ArangoServerError):
    """Failed to create the graph."""


class GraphDeleteError(ArangoServerError):
    """Failed to delete the graph."""


class GraphPropertiesError(ArangoServerError):
    """Failed to retrieve graph properties."""


class GraphTraverseError(ArangoServerError):
    """Failed to execute graph traversal."""


class VertexCollectionListError(ArangoServerError):
    """Failed to retrieve vertex collections."""


class VertexCollectionCreateError(ArangoServerError):
    """Failed to create vertex collection."""


class VertexCollectionDeleteError(ArangoServerError):
    """Failed to delete vertex collection."""


class EdgeDefinitionListError(ArangoServerError):
    """Failed to retrieve edge definitions."""


class EdgeDefinitionCreateError(ArangoServerError):
    """Failed to create edge definition."""


class EdgeDefinitionReplaceError(ArangoServerError):
    """Failed to replace edge definition."""


class EdgeDefinitionDeleteError(ArangoServerError):
    """Failed to delete edge definition."""


class EdgeListError(ArangoServerError):
    """Failed to retrieve edges coming in and out of a vertex."""


####################
# Index Exceptions #
####################


class IndexListError(ArangoServerError):
    """Failed to retrieve collection indexes."""


class IndexCreateError(ArangoServerError):
    """Failed to create collection index."""


class IndexGetError(ArangoServerError):
    """Failed to retrieve collection index."""


class IndexMissingError(ArangoClientError):
    """Failed to find collection index."""


class IndexDeleteError(ArangoServerError):
    """Failed to delete collection index."""


class IndexLoadError(ArangoServerError):
    """Failed to load indexes into memory."""


#####################
# Pregel Exceptions #
#####################


class PregelJobCreateError(ArangoServerError):
    """Failed to create Pregel job."""


class PregelJobGetError(ArangoServerError):
    """Failed to retrieve Pregel job details."""


class PregelJobDeleteError(ArangoServerError):
    """Failed to delete Pregel job."""


#####################
# Server Exceptions #
#####################


class ServerConnectionError(ArangoServerError):
    """Failed to connect to ArangoDB server."""


class ServerEngineError(ArangoServerError):
    """Failed to retrieve database engine."""


class ServerVersionError(ArangoServerError):
    """Failed to retrieve server version."""


class ServerDetailsError(ArangoServerError):
    """Failed to retrieve server details."""


class ServerLicenseGetError(ArangoServerError):
    """Failed to retrieve server license."""


class ServerLicenseSetError(ArangoServerError):
    """Failed to set server license."""


class ServerStatusError(ArangoServerError):
    """Failed to retrieve server status."""


class ServerTimeError(ArangoServerError):
    """Failed to retrieve server system time."""


class ServerEchoError(ArangoServerError):
    """Failed to retrieve details on last request."""


class ServerShutdownError(ArangoServerError):
    """Failed to initiate shutdown sequence."""


class ServerShutdownProgressError(ArangoServerError):
    """Failed to retrieve soft shutdown progress."""


class ServerRunTestsError(ArangoServerError):
    """Failed to execute server tests."""


class ServerRequiredDBVersionError(ArangoServerError):
    """Failed to retrieve server target version."""


class ServerReadLogError(ArangoServerError):
    """Failed to retrieve global log."""


class ServerLogLevelError(ArangoServerError):
    """Failed to retrieve server log levels."""


class ServerLogSettingError(ArangoServerError):
    """Failed to retrieve server log settings."""


class ServerLogLevelSetError(ArangoServerError):
    """Failed to set server log levels."""


class ServerLogSettingSetError(ArangoServerError):
    """Failed to set server log settings."""


class ServerReloadRoutingError(ArangoServerError):
    """Failed to reload routing details."""


class ServerStatisticsError(ArangoServerError):
    """Failed to retrieve server statistics."""


class ServerMetricsError(ArangoServerError):
    """Failed to retrieve server metrics."""


class ServerRoleError(ArangoServerError):
    """Failed to retrieve server role."""


class ServerModeError(ArangoServerError):
    """Failed to retrieve server mode."""


class ServerModeSetError(ArangoServerError):
    """Failed to set server mode."""


class ServerTLSError(ArangoServerError):
    """Failed to retrieve TLS data."""


class ServerTLSReloadError(ArangoServerError):
    """Failed to reload TLS."""


class ServerEncryptionError(ArangoServerError):
    """Failed to reload user-defined encryption keys."""


class ServerCurrentOptionsGetError(ArangoServerError):
    """Failed to retrieve currently-set server options."""


class ServerAvailableOptionsGetError(ArangoServerError):
    """Failed to retrieve available server options."""


class ServerExecuteError(ArangoServerError):
    """Failed to execute raw JavaScript command."""


#####################
# Task Exceptions   #
#####################


class TaskListError(ArangoServerError):
    """Failed to retrieve server tasks."""


class TaskGetError(ArangoServerError):
    """Failed to retrieve server task details."""


class TaskCreateError(ArangoServerError):
    """Failed to create server task."""


class TaskDeleteError(ArangoServerError):
    """Failed to delete server task."""


##########################
# Transaction Exceptions #
##########################


class TransactionExecuteError(ArangoServerError):
    """Failed to execute raw transaction."""


class TransactionInitError(ArangoServerError):
    """Failed to initialize transaction."""


class TransactionStatusError(ArangoServerError):
    """Failed to retrieve transaction status."""


class TransactionCommitError(ArangoServerError):
    """Failed to commit transaction."""


class TransactionAbortError(ArangoServerError):
    """Failed to abort transaction."""


class TransactionFetchError(ArangoServerError):
    """Failed to fetch existing transaction."""


class TransactionListError(ArangoServerError):
    """Failed to retrieve transactions."""


###################
# User Exceptions #
###################


class UserListError(ArangoServerError):
    """Failed to retrieve users."""


class UserGetError(ArangoServerError):
    """Failed to retrieve user details."""


class UserCreateError(ArangoServerError):
    """Failed to create user."""


class UserUpdateError(ArangoServerError):
    """Failed to update user."""


class UserReplaceError(ArangoServerError):
    """Failed to replace user."""


class UserDeleteError(ArangoServerError):
    """Failed to delete user."""


###################
# View Exceptions #
###################


class ViewListError(ArangoServerError):
    """Failed to retrieve views."""


class ViewGetError(ArangoServerError):
    """Failed to retrieve view details."""


class ViewCreateError(ArangoServerError):
    """Failed to create view."""


class ViewUpdateError(ArangoServerError):
    """Failed to update view."""


class ViewReplaceError(ArangoServerError):
    """Failed to replace view."""


class ViewDeleteError(ArangoServerError):
    """Failed to delete view."""


class ViewRenameError(ArangoServerError):
    """Failed to rename view."""


#######################
# Analyzer Exceptions #
#######################


class AnalyzerListError(ArangoServerError):
    """Failed to retrieve analyzers."""


class AnalyzerGetError(ArangoServerError):
    """Failed to retrieve analyzer details."""


class AnalyzerCreateError(ArangoServerError):
    """Failed to create analyzer."""


class AnalyzerDeleteError(ArangoServerError):
    """Failed to delete analyzer."""


#########################
# Permission Exceptions #
#########################


class PermissionListError(ArangoServerError):
    """Failed to list user permissions."""


class PermissionGetError(ArangoServerError):
    """Failed to retrieve user permission."""


class PermissionUpdateError(ArangoServerError):
    """Failed to update user permission."""


class PermissionResetError(ArangoServerError):
    """Failed to reset user permission."""


##################
# WAL Exceptions #
##################


class WALPropertiesError(ArangoServerError):
    """Failed to retrieve WAL properties."""


class WALConfigureError(ArangoServerError):
    """Failed to configure WAL properties."""


class WALTransactionListError(ArangoServerError):
    """Failed to retrieve running WAL transactions."""


class WALFlushError(ArangoServerError):
    """Failed to flush WAL."""


class WALTickRangesError(ArangoServerError):
    """Failed to return WAL tick ranges."""


class WALLastTickError(ArangoServerError):
    """Failed to return WAL tick ranges."""


class WALTailError(ArangoServerError):
    """Failed to return WAL tick ranges."""


##########################
# Replication Exceptions #
##########################


class ReplicationInventoryError(ArangoServerError):
    """Failed to retrieve inventory of collection and indexes."""


class ReplicationDumpBatchCreateError(ArangoServerError):
    """Failed to create dump batch."""


class ReplicationDumpBatchDeleteError(ArangoServerError):
    """Failed to delete a dump batch."""


class ReplicationDumpBatchExtendError(ArangoServerError):
    """Failed to extend a dump batch."""


class ReplicationDumpError(ArangoServerError):
    """Failed to retrieve collection content."""


class ReplicationSyncError(ArangoServerError):
    """Failed to synchronize data from remote."""


class ReplicationClusterInventoryError(ArangoServerError):
    """Failed to retrieve overview of collection and indexes in a cluster."""


class ReplicationLoggerStateError(ArangoServerError):
    """Failed to retrieve logger state."""


class ReplicationLoggerFirstTickError(ArangoServerError):
    """Failed to retrieve logger first tick."""


class ReplicationApplierConfigError(ArangoServerError):
    """Failed to retrieve replication applier configuration."""


class ReplicationApplierConfigSetError(ArangoServerError):
    """Failed to update replication applier configuration."""


class ReplicationApplierStartError(ArangoServerError):
    """Failed to start replication applier."""


class ReplicationApplierStopError(ArangoServerError):
    """Failed to stop replication applier."""


class ReplicationApplierStateError(ArangoServerError):
    """Failed to retrieve replication applier state."""


class ReplicationMakeSlaveError(ArangoServerError):
    """Failed to change role to slave."""


class ReplicationServerIDError(ArangoServerError):
    """Failed to retrieve server ID."""


######################
# Cluster Exceptions #
######################


class ClusterHealthError(ArangoServerError):
    """Failed to retrieve DBServer health."""


class ClusterServerIDError(ArangoServerError):
    """Failed to retrieve server ID."""


class ClusterServerRoleError(ArangoServerError):
    """Failed to retrieve server role in a cluster."""


class ClusterServerModeError(ArangoServerError):
    """Failed to retrieve server mode in a cluster."""


class ClusterServerStatisticsError(ArangoServerError):
    """Failed to retrieve DBServer statistics."""


class ClusterServerVersionError(ArangoServerError):
    """Failed to retrieve server node version."""


class ClusterServerEngineError(ArangoServerError):
    """Failed to retrieve server node engine."""


class ClusterMaintenanceModeError(ArangoServerError):
    """Failed to enable/disable cluster supervision maintenance mode."""


class ClusterEndpointsError(ArangoServerError):
    """Failed to retrieve cluster endpoints."""


class ClusterServerCountError(ArangoServerError):
    """Failed to retrieve cluster server count."""


class ClusterRebalanceError(ArangoServerError):
    """Failed to execute cluster re-balancing operation (load/set)."""


##################
# JWT Exceptions #
##################


class JWTAuthError(ArangoServerError):
    """Failed to get a new JWT token from ArangoDB."""


class JWTSecretListError(ArangoServerError):
    """Failed to retrieve information on currently loaded JWT secrets."""


class JWTSecretReloadError(ArangoServerError):
    """Failed to reload JWT secrets."""


class JWTRefreshError(ArangoClientError):
    """Failed to refresh JWT token."""


class JWTExpiredError(ArangoClientError):
    """JWT token has expired."""
