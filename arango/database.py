__all__ = [
    "StandardDatabase",
    "AsyncDatabase",
    "BatchDatabase",
    "OverloadControlDatabase",
    "TransactionDatabase",
]

from datetime import datetime
from numbers import Number
from typing import Any, Dict, List, Optional, Sequence, Union
from warnings import warn

from arango.api import ApiGroup
from arango.aql import AQL
from arango.backup import Backup
from arango.cluster import Cluster
from arango.collection import StandardCollection
from arango.connection import Connection
from arango.exceptions import (
    AnalyzerCreateError,
    AnalyzerDeleteError,
    AnalyzerGetError,
    AnalyzerListError,
    AsyncJobClearError,
    AsyncJobListError,
    CollectionCreateError,
    CollectionDeleteError,
    CollectionListError,
    DatabaseCompactError,
    DatabaseCreateError,
    DatabaseDeleteError,
    DatabaseListError,
    DatabasePropertiesError,
    DatabaseSupportInfoError,
    GraphCreateError,
    GraphDeleteError,
    GraphListError,
    JWTSecretListError,
    JWTSecretReloadError,
    PermissionGetError,
    PermissionListError,
    PermissionResetError,
    PermissionUpdateError,
    ServerAvailableOptionsGetError,
    ServerCurrentOptionsGetError,
    ServerDetailsError,
    ServerEchoError,
    ServerEncryptionError,
    ServerEngineError,
    ServerExecuteError,
    ServerLicenseGetError,
    ServerLicenseSetError,
    ServerLogLevelError,
    ServerLogLevelSetError,
    ServerLogSettingError,
    ServerLogSettingSetError,
    ServerMetricsError,
    ServerModeError,
    ServerModeSetError,
    ServerReadLogError,
    ServerReloadRoutingError,
    ServerRequiredDBVersionError,
    ServerRoleError,
    ServerRunTestsError,
    ServerShutdownError,
    ServerShutdownProgressError,
    ServerStatisticsError,
    ServerStatusError,
    ServerTimeError,
    ServerTLSError,
    ServerTLSReloadError,
    ServerVersionError,
    TaskCreateError,
    TaskDeleteError,
    TaskGetError,
    TaskListError,
    TransactionExecuteError,
    TransactionListError,
    UserCreateError,
    UserDeleteError,
    UserGetError,
    UserListError,
    UserReplaceError,
    UserUpdateError,
    ViewCreateError,
    ViewDeleteError,
    ViewGetError,
    ViewListError,
    ViewRenameError,
    ViewReplaceError,
    ViewUpdateError,
)
from arango.executor import (
    AsyncApiExecutor,
    BatchApiExecutor,
    DefaultApiExecutor,
    OverloadControlApiExecutor,
    TransactionApiExecutor,
)
from arango.formatter import (
    format_body,
    format_database,
    format_server_status,
    format_tls,
    format_view,
)
from arango.foxx import Foxx
from arango.graph import Graph
from arango.job import BatchJob
from arango.pregel import Pregel
from arango.replication import Replication
from arango.request import Request
from arango.response import Response
from arango.result import Result
from arango.typings import Json, Jsons, Params
from arango.utils import get_col_name
from arango.wal import WAL


class Database(ApiGroup):
    """Base class for Database API wrappers."""

    def __getitem__(self, name: str) -> StandardCollection:
        """Return the collection API wrapper.

        :param name: Collection name.
        :type name: str
        :return: Collection API wrapper.
        :rtype: arango.collection.StandardCollection
        """
        return self.collection(name)

    def _get_col_by_doc(self, document: Union[str, Json]) -> StandardCollection:
        """Return the collection of the given document.

        :param document: Document ID or body with "_id" field.
        :type document: str | dict
        :return: Collection API wrapper.
        :rtype: arango.collection.StandardCollection
        :raise arango.exceptions.DocumentParseError: On malformed document.
        """
        return self.collection(get_col_name(document))

    @property
    def name(self) -> str:
        """Return database name.

        :return: Database name.
        :rtype: str
        """
        return self.db_name

    @property
    def aql(self) -> AQL:
        """Return AQL (ArangoDB Query Language) API wrapper.

        :return: AQL API wrapper.
        :rtype: arango.aql.AQL
        """
        return AQL(self._conn, self._executor)

    @property
    def wal(self) -> WAL:
        """Return WAL (Write-Ahead Log) API wrapper.

        :return: WAL API wrapper.
        :rtype: arango.wal.WAL
        """
        return WAL(self._conn, self._executor)

    @property
    def foxx(self) -> Foxx:
        """Return Foxx API wrapper.

        :return: Foxx API wrapper.
        :rtype: arango.foxx.Foxx
        """
        return Foxx(self._conn, self._executor)

    @property
    def pregel(self) -> Pregel:
        """Return Pregel API wrapper.

        :return: Pregel API wrapper.
        :rtype: arango.pregel.Pregel
        """
        return Pregel(self._conn, self._executor)

    @property
    def replication(self) -> Replication:
        """Return Replication API wrapper.

        :return: Replication API wrapper.
        :rtype: arango.replication.Replication
        """
        return Replication(self._conn, self._executor)

    @property
    def cluster(self) -> Cluster:  # pragma: no cover
        """Return Cluster API wrapper.

        :return: Cluster API wrapper.
        :rtype: arango.cluster.Cluster
        """
        return Cluster(self._conn, self._executor)

    @property
    def backup(self) -> Backup:
        """Return Backup API wrapper.

        :return: Backup API wrapper.
        :rtype: arango.backup.Backup
        """
        return Backup(self._conn, self._executor)

    def properties(self) -> Result[Json]:
        """Return database properties.

        :return: Database properties.
        :rtype: dict
        :raise arango.exceptions.DatabasePropertiesError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint="/_api/database/current",
        )

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise DatabasePropertiesError(resp, request)
            return format_database(resp.body["result"])

        return self._execute(request, response_handler)

    def execute(self, command: str) -> Result[Any]:
        """Execute raw Javascript command on the server.

        Executes the JavaScript code in the body on the server as
        the body of a function with no arguments. If you have a
        return statement then the return value you produce will be returned
        as 'application/json'.

        NOTE: this method endpoint will only be usable if the server
        was started with the option `--javascript.allow-admin-execute true`.
        The default value of this option is false, which disables the execution
        of user-defined code and disables this API endpoint entirely.
        This is also the recommended setting for production.

        :param command: Javascript command to execute.
        :type command: str
        :return: Return value of **command**, if any.
        :rtype: Any
        :raise arango.exceptions.ServerExecuteError: If execution fails.
        """
        request = Request(method="post", endpoint="/_admin/execute", data=command)

        def response_handler(resp: Response) -> Any:
            if not resp.is_success:
                raise ServerExecuteError(resp, request)

            return resp.body

        return self._execute(request, response_handler)

    def execute_transaction(
        self,
        command: str,
        params: Optional[Json] = None,
        read: Optional[Sequence[str]] = None,
        write: Optional[Sequence[str]] = None,
        sync: Optional[bool] = None,
        timeout: Optional[Number] = None,
        max_size: Optional[int] = None,
        allow_implicit: Optional[bool] = None,
        intermediate_commit_count: Optional[int] = None,
        intermediate_commit_size: Optional[int] = None,
        allow_dirty_read: bool = False,
    ) -> Result[Any]:
        """Execute raw Javascript command in transaction.

        :param command: Javascript command to execute.
        :type command: str
        :param read: Names of collections read during transaction. If parameter
            **allow_implicit** is set to True, any undeclared read collections
            are loaded lazily.
        :type read: [str] | None
        :param write: Names of collections written to during transaction.
            Transaction fails on undeclared write collections.
        :type write: [str] | None
        :param params: Optional parameters passed into the Javascript command.
        :type params: dict | None
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param timeout: Timeout for waiting on collection locks. If set to 0,
            ArangoDB server waits indefinitely. If not set, system default
            value is used.
        :type timeout: int | None
        :param max_size: Max transaction size limit in bytes.
        :type max_size: int | None
        :param allow_implicit: If set to True, undeclared read collections are
            loaded lazily. If set to False, transaction fails on any undeclared
            collections.
        :type allow_implicit: bool | None
        :param intermediate_commit_count: Max number of operations after which
            an intermediate commit is performed automatically.
        :type intermediate_commit_count: int | None
        :param intermediate_commit_size: Max size of operations in bytes after
            which an intermediate commit is performed automatically.
        :type intermediate_commit_size: int | None
        :param allow_dirty_read: Allow reads from followers in a cluster.
        :type allow_dirty_read: bool | None
        :return: Return value of **command**.
        :rtype: Any
        :raise arango.exceptions.TransactionExecuteError: If execution fails.
        """
        collections: Json = {"allowImplicit": allow_implicit}
        if read is not None:
            collections["read"] = read
        if write is not None:
            collections["write"] = write

        data: Json = {"action": command}
        if collections:
            data["collections"] = collections
        if params is not None:
            data["params"] = params
        if timeout is not None:
            data["lockTimeout"] = timeout
        if sync is not None:
            data["waitForSync"] = sync
        if max_size is not None:
            data["maxTransactionSize"] = max_size
        if intermediate_commit_count is not None:
            data["intermediateCommitCount"] = intermediate_commit_count
        if intermediate_commit_size is not None:
            data["intermediateCommitSize"] = intermediate_commit_size

        request = Request(
            method="post",
            endpoint="/_api/transaction",
            data=data,
            headers={"x-arango-allow-dirty-read": "true"} if allow_dirty_read else None,
        )

        def response_handler(resp: Response) -> Any:
            if not resp.is_success:
                raise TransactionExecuteError(resp, request)

            return resp.body.get("result")

        return self._execute(request, response_handler)

    def list_transactions(self) -> Result[Jsons]:
        """Return the list of running stream transactions.

        :return: The list of transactions, with each transaction
          containing an "id" and a "state" field.
        :rtype: List[Dict[str, Any]]
        :raise arango.exceptions.TransactionListError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/transaction")

        def response_handler(resp: Response) -> Jsons:
            if not resp.is_success:
                raise TransactionListError(resp, request)

            result: Jsons = resp.body["transactions"]
            return result

        return self._execute(request, response_handler)

    def version(self, details: bool = False) -> Result[Any]:
        """Return ArangoDB server version.
        :param details: Return more detailed version output
        :type details: bool | None
        :return: Server version.
        :rtype: str
        :raise arango.exceptions.ServerVersionError: If retrieval fails.
        """
        request = Request(
            method="get", endpoint="/_api/version", params={"details": details}
        )

        def response_handler(resp: Response) -> Any:
            if not resp.is_success:
                raise ServerVersionError(resp, request)
            if not details:
                return str(resp.body["version"])
            else:
                return resp.body

        return self._execute(request, response_handler)

    def details(self) -> Result[Json]:
        """Return ArangoDB server details.

        :return: Server details.
        :rtype: dict
        :raise arango.exceptions.ServerDetailsError: If retrieval fails.
        """
        request = Request(
            method="get", endpoint="/_api/version", params={"details": True}
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                result: Json = resp.body["details"]
                return result
            raise ServerDetailsError(resp, request)

        return self._execute(request, response_handler)

    def license(self) -> Result[Json]:
        """View the license information and status of an
        Enterprise Edition instance. Can be called on
        single servers, Coordinators, and DB-Servers.

        :return: Server license.
        :rtype: dict
        :raise arango.exceptions.ServerLicenseGetError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_admin/license")

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                result: Json = resp.body
                return result
            raise ServerLicenseGetError(resp, request)

        return self._execute(request, response_handler)

    def set_license(self, license: str, force: bool = False) -> Result[Json]:
        """Set a new license for an Enterprise Edition
        instance. Can be called on single servers, Coordinators,
        and DB-Servers.

        :param license: The Base64-encoded license string.
        :type license: str
        :param force: If set to True, the new license will be set even if
            it expires sooner than the current license.
        :type force: bool
        :return: Server license.
        :rtype: dict
        :raise arango.exceptions.ServerLicenseError: If retrieval fails.
        """
        request = Request(
            method="put",
            endpoint="/_admin/license",
            params={"force": force},
            data=license,
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                result: Json = resp.body
                return result
            raise ServerLicenseSetError(resp, request)

        return self._execute(request, response_handler)

    def status(self) -> Result[Json]:
        """Return ArangoDB server status.

        :return: Server status.
        :rtype: dict
        :raise arango.exceptions.ServerStatusError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint="/_admin/status",
        )

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise ServerStatusError(resp, request)
            return format_server_status(resp.body)

        return self._execute(request, response_handler)

    def compact(
        self,
        change_level: Optional[bool] = None,
        compact_bottom_most_level: Optional[bool] = None,
    ) -> Result[Json]:
        """Compact all databases.

        NOTE: This command can cause a full rewrite of all data in all databases,
        which may take very long for large databases. It should thus only be used with
        care and only when additional I/O load can be tolerated for a prolonged time.

        This method can be used to reclaim disk space after substantial data deletions
        have taken place, by compacting the entire database system data.

        This method requires superuser access.

        :param change_level: Whether or not compacted data should be moved to
            the minimum possible level. Default value is False.
        :type change_level: bool | None
        :param compact_bottom_most_level: Whether or not to compact the
            bottom-most level of data. Default value is False.
        :type compact_bottom_most_level: bool | None
        :return: Collection compact.
        :rtype: dict
        :raise arango.exceptions.CollectionCompactError: If retrieval fails.
        """
        data = {}
        if change_level is not None:
            data["changeLevel"] = change_level
        if compact_bottom_most_level is not None:
            data["compactBottomMostLevel"] = compact_bottom_most_level

        request = Request(method="put", endpoint="/_admin/compact", data=data)

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_body(resp.body)
            raise DatabaseCompactError(resp, request)

        return self._execute(request, response_handler)

    def required_db_version(self) -> Result[str]:
        """Return required version of target database.

        :return: Required version of target database.
        :rtype: str
        :raise arango.exceptions.ServerRequiredDBVersionError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_admin/database/target-version")

        def response_handler(resp: Response) -> str:
            if resp.is_success:
                return str(resp.body["version"])
            raise ServerRequiredDBVersionError(resp, request)

        return self._execute(request, response_handler)

    def engine(self) -> Result[Json]:
        """Return the database engine details.

        :return: Database engine details.
        :rtype: dict
        :raise arango.exceptions.ServerEngineError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/engine")

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_body(resp.body)
            raise ServerEngineError(resp, request)

        return self._execute(request, response_handler)

    def statistics(self, description: bool = False) -> Result[Json]:
        """Return server statistics.

        :return: Server statistics.
        :rtype: dict
        :raise arango.exceptions.ServerStatisticsError: If retrieval fails.
        """
        if description:
            endpoint = "/_admin/statistics-description"
        else:
            endpoint = "/_admin/statistics"

        request = Request(method="get", endpoint=endpoint)

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_body(resp.body)
            raise ServerStatisticsError(resp, request)

        return self._execute(request, response_handler)

    def role(self) -> Result[str]:
        """Return server role.

        :return: Server role. Possible values are "SINGLE" (server which is not
            in a cluster), "COORDINATOR" (cluster coordinator), "PRIMARY",
            "SECONDARY", "AGENT" (Agency node in a cluster) or "UNDEFINED".
        :rtype: str
        :raise arango.exceptions.ServerRoleError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_admin/server/role")

        def response_handler(resp: Response) -> str:
            if resp.is_success:
                return str(resp.body["role"])
            raise ServerRoleError(resp, request)

        return self._execute(request, response_handler)

    def mode(self) -> Result[str]:
        """Return the server mode (default or read-only)

        In a read-only server, all write operations will fail
        with an error code of 1004 (ERROR_READ_ONLY). Creating or dropping
        databases and collections will also fail with error code 11 (ERROR_FORBIDDEN).

        :return: Server mode. Possible values are "default" or "readonly".
        :rtype: str
        :raise arango.exceptions.ServerModeError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_admin/server/mode")

        def response_handler(resp: Response) -> str:
            if resp.is_success:
                return str(resp.body["mode"])

            raise ServerModeError(resp, request)

        return self._execute(request, response_handler)

    def set_mode(self, mode: str) -> Result[Json]:
        """Set the server mode to read-only or default.

        Update mode information about a server. The JSON response will
        contain a field mode with the value readonly or default.
        In a read-only server all write operations will fail with an error
        code of 1004 (ERROR_READ_ONLY). Creating or dropping of databases
        and collections will also fail with error code 11 (ERROR_FORBIDDEN).

        This is a protected API. It requires authentication and administrative
        server rights.

        :param mode: Server mode. Possible values are "default" or "readonly".
        :type mode: str
        :return: Server mode.
        :rtype: str
        :raise arango.exceptions.ServerModeSetError: If set fails.
        """
        request = Request(
            method="put", endpoint="/_admin/server/mode", data={"mode": mode}
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_body(resp.body)
            raise ServerModeSetError(resp, request)

        return self._execute(request, response_handler)

    def time(self) -> Result[datetime]:
        """Return server system time.

        :return: Server system time.
        :rtype: datetime.datetime
        :raise arango.exceptions.ServerTimeError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_admin/time")

        def response_handler(resp: Response) -> datetime:
            if not resp.is_success:
                raise ServerTimeError(resp, request)
            return datetime.fromtimestamp(resp.body["time"])

        return self._execute(request, response_handler)

    def echo(self, body: Optional[Any] = None) -> Result[Json]:
        """Return details of the last request (e.g. headers, payload),
        or echo the given request body.

        :param body: The body of the request. Can be of any type
            and is simply forwarded. If not set, the details of the last
            request are returned.
        :type body: dict | list | str | int | float | None
        :return: Details of the last request.
        :rtype: dict
        :raise arango.exceptions.ServerEchoError: If retrieval fails.
        """
        request = (
            Request(method="get", endpoint="/_admin/echo")
            if body is None
            else Request(method="post", endpoint="/_admin/echo", data=body)
        )

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise ServerEchoError(resp, request)
            result: Json = resp.body
            return result

        return self._execute(request, response_handler)

    def shutdown(self, soft: bool = False) -> Result[bool]:  # pragma: no cover
        """Initiate server shutdown sequence.

        :param soft: If set to true, this initiates a soft shutdown. This is only
            available on Coordinators. When issued, the Coordinator tracks a number
            of ongoing operations, waits until all have finished, and then shuts
            itself down normally. It will still accept new operations.
        :type soft: bool
        :return: True if the server was shutdown successfully.
        :rtype: bool
        :raise arango.exceptions.ServerShutdownError: If shutdown fails.
        """
        request = Request(
            method="delete", endpoint="/_admin/shutdown", params={"soft": soft}
        )

        def response_handler(resp: Response) -> bool:
            if not resp.is_success:
                raise ServerShutdownError(resp, request)
            return True

        return self._execute(request, response_handler)

    def shutdown_progress(self) -> Result[Json]:  # pragma: no cover
        """Query the soft shutdown progress. This call reports progress about a
            soft Coordinator shutdown (DELETE /_admin/shutdown?soft=true). This API
            is only available on Coordinators.

        :return: Information about the shutdown progress.
        :rtype: dict
        :raise arango.exceptions.ServerShutdownError: If shutdown fails.
        """
        request = Request(method="get", endpoint="/_admin/shutdown")

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise ServerShutdownProgressError(resp, request)

            result: Json = resp.body
            return result

        return self._execute(request, response_handler)

    def run_tests(self, tests: Sequence[str]) -> Result[Json]:  # pragma: no cover
        """Run available unittests on the server.

        :param tests: List of files containing the test suites.
        :type tests: [str]
        :return: Test results.
        :rtype: dict
        :raise arango.exceptions.ServerRunTestsError: If execution fails.
        """
        request = Request(method="post", endpoint="/_admin/test", data={"tests": tests})

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise ServerRunTestsError(resp, request)
            result: Json = resp.body
            return result

        return self._execute(request, response_handler)

    def read_log(
        self,
        upto: Optional[Union[int, str]] = None,
        level: Optional[Union[int, str]] = None,
        start: Optional[int] = None,
        size: Optional[int] = None,
        offset: Optional[int] = None,
        search: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> Result[Json]:
        """Read the global log from server. This method is deprecated
            in ArangoDB 3.8 and will be removed in a future version
            of the driver. Use :func:`arango.database.Database.read_log_entries`
            instead.

        :param upto: Return the log entries up to the given level (mutually
            exclusive with parameter **level**). Allowed values are "fatal",
            "error", "warning", "info" (default) and "debug".
        :type upto: int | str
        :param level: Return the log entries of only the given level (mutually
            exclusive with **upto**). Allowed values are "fatal", "error",
            "warning", "info" (default) and "debug".
        :type level: int | str
        :param start: Return the log entries whose ID is greater or equal to
            the given value.
        :type start: int
        :param size: Restrict the size of the result to the given value. This
            can be used for pagination.
        :type size: int
        :param offset: Number of entries to skip (e.g. for pagination).
        :type offset: int
        :param search: Return only the log entries containing the given text.
        :type search: str
        :param sort: Sort the log entries according to the given fashion, which
            can be "sort" or "desc".
        :type sort: str
        :return: Server log entries.
        :rtype: dict
        :raise arango.exceptions.ServerReadLogError: If read fails.
        """
        m = "read_log() is deprecated in ArangoDB 3.8 and will be removed in a future version of the driver. Use read_log_entries() instead."  # noqa: E501
        warn(m, DeprecationWarning, stacklevel=2)

        params = dict()
        if upto is not None:
            params["upto"] = upto
        if level is not None:
            params["level"] = level
        if start is not None:
            params["start"] = start
        if size is not None:
            params["size"] = size
        if offset is not None:
            params["offset"] = offset
        if search is not None:
            params["search"] = search
        if sort is not None:
            params["sort"] = sort

        request = Request(method="get", endpoint="/_admin/log", params=params)

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise ServerReadLogError(resp, request)

            result: Json = resp.body
            if "totalAmount" in result:
                resp.body["total_amount"] = resp.body.pop("totalAmount")
            return result

        return self._execute(request, response_handler)

    def read_log_entries(
        self,
        upto: Optional[Union[int, str]] = None,
        level: Optional[Union[int, str]] = None,
        start: Optional[int] = None,
        size: Optional[int] = None,
        offset: Optional[int] = None,
        search: Optional[str] = None,
        sort: Optional[str] = None,
        server_id: Optional[str] = None,
    ) -> Result[Json]:
        """Read the global log from server.

        :param upto: Return the log entries up to the given level (mutually
            exclusive with parameter **level**). Allowed values are "fatal",
            "error", "warning", "info" (default) and "debug".
        :type upto: int | str
        :param level: Return the log entries of only the given level (mutually
            exclusive with **upto**). Allowed values are "fatal", "error",
            "warning", "info" (default) and "debug".
        :type level: int | str
        :param start: Return the log entries whose ID is greater or equal to
            the given value.
        :type start: int
        :param size: Restrict the size of the result to the given value. This
            can be used for pagination.
        :type size: int
        :param offset: Number of entries to skip (e.g. for pagination).
        :type offset: int
        :param search: Return only the log entries containing the given text.
        :type search: str
        :param sort: Sort the log entries according to the given fashion, which
            can be "sort" or "desc".
        :type sort: str
        :param server_id: Returns all log entries of the specified server.
            All other query parameters remain valid. If no serverId is given,
            the asked server will reply. This parameter is only meaningful
            on Coordinators.
        :type server_id: str
        :return: Server log entries.
        :rtype: dict
        :raise arango.exceptions.ServerReadLogError: If read fails.
        """
        params = dict()
        if upto is not None:
            params["upto"] = upto
        if level is not None:
            params["level"] = level
        if start is not None:
            params["start"] = start
        if size is not None:
            params["size"] = size
        if offset is not None:
            params["offset"] = offset
        if search is not None:
            params["search"] = search
        if sort is not None:
            params["sort"] = sort
        if server_id is not None:
            params["serverId"] = server_id

        request = Request(method="get", endpoint="/_admin/log/entries", params=params)

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise ServerReadLogError(resp, request)

            result: Json = resp.body
            return result

        return self._execute(request, response_handler)

    def log_settings(self) -> Result[Json]:
        """Return the structured log settings.

        :return: Current log settings. False values are not returned.
        :rtype: dict
        """
        request = Request(method="get", endpoint="/_admin/log/structured")

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise ServerLogSettingError(resp, request)
            result: Json = resp.body
            return result

        return self._execute(request, response_handler)

    def set_log_settings(self, **kwargs: Dict[str, Any]) -> Result[Json]:
        """Set the structured log settings.

        This method takes arbitrary keyword arguments where the keys are the
        structured log parameters and the values are true or false, for either
        enabling or disabling the parameters.

        .. code-block:: python

            arango.set_log_settings(
                database=True,
                url=True,
                username=False,
            )

        :param kwargs: Structured log parameters.
        :type kwargs: Dict[str, Any]
        :return: New log settings. False values are not returned.
        :rtype: dict
        """
        request = Request(method="put", endpoint="/_admin/log/structured", data=kwargs)

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise ServerLogSettingSetError(resp, request)
            result: Json = resp.body
            return result

        return self._execute(request, response_handler)

    def log_levels(self, server_id: Optional[str] = None) -> Result[Json]:
        """Return current logging levels.

        :param server_id: Forward log level to a specific server. This makes it
            easier to adjust the log levels in clusters because DB-Servers require
            JWT authentication whereas Coordinators also support authentication
            using usernames and passwords.
        :type server_id: str
        :return: Current logging levels.
        :rtype: dict
        """
        params: Params = {}
        if server_id is not None:
            params["serverId"] = server_id

        request = Request(method="get", endpoint="/_admin/log/level", params=params)

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise ServerLogLevelError(resp, request)
            result: Json = resp.body
            return result

        return self._execute(request, response_handler)

    def set_log_levels(
        self, server_id: Optional[str] = None, **kwargs: Dict[str, Any]
    ) -> Result[Json]:
        """Set the logging levels.

        This method takes arbitrary keyword arguments where the keys are the
        logger names and the values are the logging levels. For example:

        .. code-block:: python

            arango.set_log_levels(
                agency='DEBUG',
                collector='INFO',
                threads='WARNING'
            )

        Keys that are not valid logger names are ignored.

        :param server_id: Forward log level to a specific server. This makes it
            easier to adjust the log levels in clusters because DB-Servers require
            JWT authentication whereas Coordinators also support authentication
            using usernames and passwords.
        :type server_id: str | None
        :param kwargs: Logging levels.
        :type kwargs: Dict[str, Any]
        :return: New logging levels.
        :rtype: dict
        """
        params: Params = {}
        if server_id is not None:
            params["serverId"] = server_id

        request = Request(
            method="put", endpoint="/_admin/log/level", params=params, data=kwargs
        )

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise ServerLogLevelSetError(resp, request)
            result: Json = resp.body
            return result

        return self._execute(request, response_handler)

    def reload_routing(self) -> Result[bool]:
        """Reload the routing information.

        :return: True if routing was reloaded successfully.
        :rtype: bool
        :raise arango.exceptions.ServerReloadRoutingError: If reload fails.
        """
        request = Request(method="post", endpoint="/_admin/routing/reload")

        def response_handler(resp: Response) -> bool:
            if not resp.is_success:
                raise ServerReloadRoutingError(resp, request)
            return True

        return self._execute(request, response_handler)

    def metrics(self) -> Result[str]:
        """Return server metrics in Prometheus format.

        :return: Server metrics in Prometheus format.
        :rtype: str
        """
        request = Request(method="get", endpoint="/_admin/metrics/v2")

        def response_handler(resp: Response) -> str:
            if resp.is_success:
                return resp.raw_body
            raise ServerMetricsError(resp, request)

        return self._execute(request, response_handler)

    def jwt_secrets(self) -> Result[Json]:  # pragma: no cover
        """Return information on currently loaded JWT secrets.

        :return: Information on currently loaded JWT secrets.
        :rtype: dict
        """
        request = Request(method="get", endpoint="/_admin/server/jwt")

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise JWTSecretListError(resp, request)
            result: Json = resp.body["result"]
            return result

        return self._execute(request, response_handler)

    def reload_jwt_secrets(self) -> Result[Json]:  # pragma: no cover
        """Hot-reload JWT secrets.

        Calling this without payload reloads JWT secrets from disk. Only files
        specified via arangod startup option ``--server.jwt-secret-keyfile`` or
        ``--server.jwt-secret-folder`` are used. It is not possible to change
        the location where files are loaded from without restarting the server.

        :return: Information on reloaded JWT secrets.
        :rtype: dict
        """
        request = Request(method="post", endpoint="/_admin/server/jwt")

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise JWTSecretReloadError(resp, request)
            result: Json = resp.body["result"]
            return result

        return self._execute(request, response_handler)

    def tls(self) -> Result[Json]:
        """Return TLS data (server key, client-auth CA).

        :return: TLS data.
        :rtype: dict
        """
        request = Request(method="get", endpoint="/_admin/server/tls")

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise ServerTLSError(resp, request)
            return format_tls(resp.body["result"])

        return self._execute(request, response_handler)

    def reload_tls(self) -> Result[Json]:
        """Reload TLS data (server key, client-auth CA).

        :return: New TLS data.
        :rtype: dict
        """
        request = Request(method="post", endpoint="/_admin/server/tls")

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise ServerTLSReloadError(resp, request)
            return format_tls(resp.body["result"])

        return self._execute(request, response_handler)

    def encryption(self) -> Result[Json]:
        """Rotate the user-supplied keys for encryption.

        This method is available only for enterprise edition of ArangoDB.

        :return: New TLS data.
        :rtype: dict
        :raise arango.exceptions.ServerEncryptionError: If retrieval fails.
        """
        request = Request(method="post", endpoint="/_admin/server/encryption")

        def response_handler(resp: Response) -> Json:
            if resp.is_success:  # pragma: no cover
                result: Json = resp.body["result"]
                return result
            raise ServerEncryptionError(resp, request)

        return self._execute(request, response_handler)

    def options(self) -> Result[Json]:
        """Return the currently-set server options (ArangoDB 3.12+)

        As this API may reveal sensitive data about the deployment, it can only
        be accessed from inside the _system database. In addition, there is a
        policy control startup option --server.options-api that determines if and
        to whom the API is made available. This option can have the following
        values:
        - disabled: API is disabled.
        - jwt: API can only be accessed via superuser JWT.
        - admin: API can be accessed by admin users in the _system database only.
        - public: everyone with access to _system database can access the API.

        :return: Server options.
        :rtype: dict
        """
        request = Request(method="get", endpoint="/_admin/options")

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                result: Json = resp.body
                return result
            raise ServerCurrentOptionsGetError(resp, request)

        return self._execute(request, response_handler)

    def options_available(self) -> Result[Json]:
        """Return a description of all available server options (ArangoDB 3.12+)

        As this API may reveal sensitive data about the deployment, it can only
        be accessed from inside the _system database. In addition, there is a
        policy control startup option --server.options-api that determines if and
        to whom the API is made available. This option can have the following
        values:
        - disabled: API is disabled.
        - jwt: API can only be accessed via superuser JWT.
        - admin: API can be accessed by admin users in the _system database only.
        - public: everyone with access to _system database can access the options API.

        :return: Server options.
        :rtype: dict
        """
        request = Request(method="get", endpoint="/_admin/options-description")

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                result: Json = resp.body
                return result
            raise ServerAvailableOptionsGetError(resp, request)

        return self._execute(request, response_handler)

    #######################
    # Database Management #
    #######################

    def databases(self) -> Result[List[str]]:
        """Return the names of all databases.

        :return: Database names.
        :rtype: [str]
        :raise arango.exceptions.DatabaseListError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/database")

        def response_handler(resp: Response) -> List[str]:
            if not resp.is_success:
                raise DatabaseListError(resp, request)
            result: List[str] = resp.body["result"]
            return result

        return self._execute(request, response_handler)

    def databases_accessible_to_user(self) -> Result[List[str]]:
        """Return the names of all databases accessible by the user.

        :return: Database names accesible by the current user.
        :rtype: List[str]
        :raise arango.exceptions.DatabaseListError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/database/user")

        def response_handler(resp: Response) -> List[str]:
            if not resp.is_success:
                raise DatabaseListError(resp, request)
            result: List[str] = resp.body["result"]
            return result

        return self._execute(request, response_handler)

    def has_database(self, name: str) -> Result[bool]:
        """Check if a database exists.

        :param name: Database name.
        :type name: str
        :return: True if database exists, False otherwise.
        :rtype: bool
        """
        request = Request(method="get", endpoint="/_api/database")

        def response_handler(resp: Response) -> bool:
            if not resp.is_success:
                raise DatabaseListError(resp, request)
            return name in resp.body["result"]

        return self._execute(request, response_handler)

    def create_database(
        self,
        name: str,
        users: Optional[Sequence[Json]] = None,
        replication_factor: Union[int, str, None] = None,
        write_concern: Optional[int] = None,
        sharding: Optional[str] = None,
    ) -> Result[bool]:
        """Create a new database.

        :param name: Database name.
        :type name: str
        :param users: List of users with access to the new database, where each
            user is a dictionary with fields "username", "password", "active"
            and "extra" (see below for example). If not set, only the admin and
            current user are granted access.
        :type users: [dict]
        :param replication_factor: Default replication factor for collections
            created in this database. Special values include "satellite" which
            replicates the collection to every DBServer, and 1 which disables
            replication. Used for clusters only.
        :type replication_factor: int | str
        :param write_concern: Default write concern for collections created in
            this database. Determines how many copies of each shard are
            required to be in sync on different DBServers. If there are less
            than these many copies in the cluster a shard will refuse to write.
            Writes to shards with enough up-to-date copies will succeed at the
            same time, however. Value of this parameter can not be larger than
            the value of **replication_factor**. Used for clusters only.
        :type write_concern: int
        :param sharding: Sharding method used for new collections in this
            database. Allowed values are: "", "flexible" and "single". The
            first two are equivalent. Used for clusters only.
        :type sharding: str
        :return: True if database was created successfully.
        :rtype: bool
        :raise arango.exceptions.DatabaseCreateError: If create fails.

        Here is an example entry for parameter **users**:

        .. code-block:: python

            {
                'username': 'john',
                'password': 'password',
                'active': True,
                'extra': {'Department': 'IT'}
            }
        """
        data: Json = {"name": name}

        options: Json = {}
        if replication_factor is not None:
            options["replicationFactor"] = replication_factor
        if write_concern is not None:
            options["writeConcern"] = write_concern
        if sharding is not None:
            options["sharding"] = sharding
        if options:
            data["options"] = options

        if users is not None:
            data["users"] = [
                {
                    "username": user["username"],
                    "passwd": user["password"],
                    "active": user.get("active", True),
                    "extra": user.get("extra", {}),
                }
                for user in users
            ]

        request = Request(method="post", endpoint="/_api/database", data=data)

        def response_handler(resp: Response) -> bool:
            if not resp.is_success:
                raise DatabaseCreateError(resp, request)
            return True

        return self._execute(request, response_handler)

    def delete_database(self, name: str, ignore_missing: bool = False) -> Result[bool]:
        """Delete the database.

        :param name: Database name.
        :type name: str
        :param ignore_missing: Do not raise an exception on missing database.
        :type ignore_missing: bool
        :return: True if database was deleted successfully, False if database
            was not found and **ignore_missing** was set to True.
        :rtype: bool
        :raise arango.exceptions.DatabaseDeleteError: If delete fails.
        """
        request = Request(method="delete", endpoint=f"/_api/database/{name}")

        def response_handler(resp: Response) -> bool:
            if resp.error_code == 1228 and ignore_missing:
                return False
            if not resp.is_success:
                raise DatabaseDeleteError(resp, request)
            return True

        return self._execute(request, response_handler)

    #########################
    # Collection Management #
    #########################

    def collection(self, name: str) -> StandardCollection:
        """Return the standard collection API wrapper.

        :param name: Collection name.
        :type name: str
        :return: Standard collection API wrapper.
        :rtype: arango.collection.StandardCollection
        """
        return StandardCollection(self._conn, self._executor, name)

    def has_collection(self, name: str) -> Result[bool]:
        """Check if collection exists in the database.

        :param name: Collection name.
        :type name: str
        :return: True if collection exists, False otherwise.
        :rtype: bool
        """
        request = Request(method="get", endpoint="/_api/collection")

        def response_handler(resp: Response) -> bool:
            if not resp.is_success:
                raise CollectionListError(resp, request)
            return any(col["name"] == name for col in resp.body["result"])

        return self._execute(request, response_handler)

    def collections(self) -> Result[Jsons]:
        """Return the collections in the database.

        :return: Collections in the database and their details.
        :rtype: [dict]
        :raise arango.exceptions.CollectionListError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/collection")

        def response_handler(resp: Response) -> Jsons:
            if not resp.is_success:
                raise CollectionListError(resp, request)
            return [
                {
                    "id": col["id"],
                    "name": col["name"],
                    "system": col["isSystem"],
                    "type": StandardCollection.types[col["type"]],
                    "status": StandardCollection.statuses[col["status"]],
                }
                for col in resp.body["result"]
            ]

        return self._execute(request, response_handler)

    def create_collection(
        self,
        name: str,
        sync: bool = False,
        system: bool = False,
        edge: bool = False,
        user_keys: bool = True,
        key_increment: Optional[int] = None,
        key_offset: Optional[int] = None,
        key_generator: str = "traditional",
        shard_fields: Optional[Sequence[str]] = None,
        shard_count: Optional[int] = None,
        replication_factor: Optional[int] = None,
        shard_like: Optional[str] = None,
        sync_replication: Optional[bool] = None,
        enforce_replication_factor: Optional[bool] = None,
        sharding_strategy: Optional[str] = None,
        smart_join_attribute: Optional[str] = None,
        write_concern: Optional[int] = None,
        schema: Optional[Json] = None,
        computedValues: Optional[Jsons] = None,
    ) -> Result[StandardCollection]:
        """Create a new collection.

        :param name: Collection name.
        :type name: str
        :param sync: If set to True, document operations via the collection
            will block until synchronized to disk by default.
        :type sync: bool | None
        :param system: If set to True, a system collection is created. The
            collection name must have leading underscore "_" character.
        :type system: bool
        :param edge: If set to True, an edge collection is created.
        :type edge: bool
        :param key_generator: Used for generating document keys. Allowed values
            are "traditional" or "autoincrement".
        :type key_generator: str
        :param user_keys: If set to True, users are allowed to supply document
            keys. If set to False, the key generator is solely responsible for
            supplying the key values.
        :type user_keys: bool
        :param key_increment: Key increment value. Applies only when value of
            **key_generator** is set to "autoincrement".
        :type key_increment: int
        :param key_offset: Key offset value. Applies only when value of
            **key_generator** is set to "autoincrement".
        :type key_offset: int
        :param shard_fields: Field(s) used to determine the target shard.
        :type shard_fields: [str]
        :param shard_count: Number of shards to create.
        :type shard_count: int
        :param replication_factor: Number of copies of each shard on different
            servers in a cluster. Allowed values are 1 (only one copy is kept
            and no synchronous replication), and n (n-1 replicas are kept and
            any two copies are replicated across servers synchronously, meaning
            every write to the master is copied to all slaves before operation
            is reported successful).
        :type replication_factor: int
        :param shard_like: Name of prototype collection whose sharding
            specifics are imitated. Prototype collections cannot be dropped
            before imitating collections. Applies to enterprise version of
            ArangoDB only.
        :type shard_like: str
        :param sync_replication: If set to True, server reports success only
            when collection is created in all replicas. You can set this to
            False for faster server response, and if full replication is not a
            concern.
        :type sync_replication: bool
        :param enforce_replication_factor: Check if there are enough replicas
            available at creation time, or halt the operation.
        :type enforce_replication_factor: bool
        :param sharding_strategy: Sharding strategy. Available for ArangoDB
            version  and up only. Possible values are "community-compat",
            "enterprise-compat", "enterprise-smart-edge-compat", "hash" and
            "enterprise-hash-smart-edge". Refer to ArangoDB documentation for
            more details on each value.
        :type sharding_strategy: str
        :param smart_join_attribute: Attribute of the collection which must
            contain the shard key value of the smart join collection. The shard
            key for the documents must contain the value of this attribute,
            followed by a colon ":" and the primary key of the document.
            Requires parameter **shard_like** to be set to the name of another
            collection, and parameter **shard_fields** to be set to a single
            shard key attribute, with another colon ":" at the end. Available
            only for enterprise version of ArangoDB.
        :type smart_join_attribute: str
        :param write_concern: Write concern for the collection. Determines how
            many copies of each shard are required to be in sync on different
            DBServers. If there are less than these many copies in the cluster
            a shard will refuse to write. Writes to shards with enough
            up-to-date copies will succeed at the same time. The value of this
            parameter cannot be larger than that of **replication_factor**.
            Default value is 1. Used for clusters only.
        :type write_concern: int
        :param schema: Optional dict specifying the collection level schema
            for documents. See ArangoDB documentation for more information on
            document schema validation.
        :type schema: dict
        :param computedValues: Array of computed values for the new collection
            enabling default values to new documents or the maintenance of
            auxiliary attributes for search queries. Available in ArangoDB
            version 3.10 or greater. See ArangoDB documentation for more
            information on computed values.
        :type computedValues: list
        :return: Standard collection API wrapper.
        :rtype: arango.collection.StandardCollection
        :raise arango.exceptions.CollectionCreateError: If create fails.
        """
        key_options: Json = {"type": key_generator, "allowUserKeys": user_keys}
        if key_generator == "autoincrement":
            if key_increment is not None:
                key_options["increment"] = key_increment
            if key_offset is not None:
                key_options["offset"] = key_offset

        data: Json = {
            "name": name,
            "waitForSync": sync,
            "isSystem": system,
            "keyOptions": key_options,
            "type": 3 if edge else 2,
        }
        if shard_count is not None:
            data["numberOfShards"] = shard_count
        if shard_fields is not None:
            data["shardKeys"] = shard_fields
        if replication_factor is not None:
            data["replicationFactor"] = replication_factor
        if shard_like is not None:
            data["distributeShardsLike"] = shard_like
        if sharding_strategy is not None:
            data["shardingStrategy"] = sharding_strategy
        if smart_join_attribute is not None:
            data["smartJoinAttribute"] = smart_join_attribute
        if write_concern is not None:
            data["writeConcern"] = write_concern
        if schema is not None:
            data["schema"] = schema
        if computedValues is not None:
            data["computedValues"] = computedValues

        params: Params = {}
        if sync_replication is not None:
            params["waitForSyncReplication"] = sync_replication
        if enforce_replication_factor is not None:
            params["enforceReplicationFactor"] = enforce_replication_factor

        request = Request(
            method="post", endpoint="/_api/collection", params=params, data=data
        )

        def response_handler(resp: Response) -> StandardCollection:
            if resp.is_success:
                return self.collection(name)
            raise CollectionCreateError(resp, request)

        return self._execute(request, response_handler)

    def delete_collection(
        self, name: str, ignore_missing: bool = False, system: Optional[bool] = None
    ) -> Result[bool]:
        """Delete the collection.

        :param name: Collection name.
        :type name: str
        :param ignore_missing: Do not raise an exception on missing collection.
        :type ignore_missing: bool
        :param system: Whether the collection is a system collection.
        :type system: bool
        :return: True if collection was deleted successfully, False if
            collection was not found and **ignore_missing** was set to True.
        :rtype: bool
        :raise arango.exceptions.CollectionDeleteError: If delete fails.
        """
        params: Params = {}
        if system is not None:
            params["isSystem"] = system

        request = Request(
            method="delete", endpoint=f"/_api/collection/{name}", params=params
        )

        def response_handler(resp: Response) -> bool:
            if resp.error_code == 1203 and ignore_missing:
                return False
            if not resp.is_success:
                raise CollectionDeleteError(resp, request)
            return True

        return self._execute(request, response_handler)

    ####################
    # Graph Management #
    ####################

    def graph(self, name: str) -> Graph:
        """Return the graph API wrapper.

        :param name: Graph name.
        :type name: str
        :return: Graph API wrapper.
        :rtype: arango.graph.Graph
        """
        return Graph(self._conn, self._executor, name)

    def has_graph(self, name: str) -> Result[bool]:
        """Check if a graph exists in the database.

        :param name: Graph name.
        :type name: str
        :return: True if graph exists, False otherwise.
        :rtype: bool
        """
        request = Request(method="get", endpoint="/_api/gharial")

        def response_handler(resp: Response) -> bool:
            if not resp.is_success:
                raise GraphListError(resp, request)
            return any(name == graph["_key"] for graph in resp.body["graphs"])

        return self._execute(request, response_handler)

    def graphs(self) -> Result[Jsons]:
        """List all graphs in the database.

        :return: Graphs in the database.
        :rtype: [dict]
        :raise arango.exceptions.GraphListError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/gharial")

        def response_handler(resp: Response) -> Jsons:
            if not resp.is_success:
                raise GraphListError(resp, request)
            return [
                {
                    "id": body["_id"],
                    "name": body["_key"],
                    "revision": body["_rev"],
                    "orphan_collections": body["orphanCollections"],
                    "edge_definitions": [
                        {
                            "edge_collection": definition["collection"],
                            "from_vertex_collections": definition["from"],
                            "to_vertex_collections": definition["to"],
                        }
                        for definition in body["edgeDefinitions"]
                    ],
                    "shard_count": body.get("numberOfShards"),
                    "replication_factor": body.get("replicationFactor"),
                }
                for body in resp.body["graphs"]
            ]

        return self._execute(request, response_handler)

    def create_graph(
        self,
        name: str,
        edge_definitions: Optional[Sequence[Json]] = None,
        orphan_collections: Optional[Sequence[str]] = None,
        smart: Optional[bool] = None,
        disjoint: Optional[bool] = None,
        smart_field: Optional[str] = None,
        shard_count: Optional[int] = None,
        replication_factor: Optional[int] = None,
        write_concern: Optional[int] = None,
    ) -> Result[Graph]:
        """Create a new graph.

        :param name: Graph name.
        :type name: str
        :param edge_definitions: List of edge definitions, where each edge
            definition entry is a dictionary with fields "edge_collection",
            "from_vertex_collections" and "to_vertex_collections" (see below
            for example).
        :type edge_definitions: [dict] | None
        :param orphan_collections: Names of additional vertex collections that
            are not in edge definitions.
        :type orphan_collections: [str] | None
        :param smart: If set to True, sharding is enabled (see parameter
            **smart_field** below). Applies only to enterprise version of
            ArangoDB.
        :type smart: bool | None
        :param disjoint: If set to True, create a disjoint SmartGraph instead
            of a regular SmartGraph. Applies only to enterprise version of
            ArangoDB.
        :type disjoint: bool | None
        :param smart_field: Document field used to shard the vertices of the
            graph. To use this, parameter **smart** must be set to True and
            every vertex in the graph must have the smart field. Applies only
            to enterprise version of ArangoDB.
        :type smart_field: str | None
        :param shard_count: Number of shards used for every collection in the
            graph. To use this, parameter **smart** must be set to True and
            every vertex in the graph must have the smart field. This number
            cannot be modified later once set. Applies only to enterprise
            version of ArangoDB.
        :type shard_count: int | None
        :param replication_factor: Number of copies of each shard on different
            servers in a cluster. Allowed values are 1 (only one copy is kept
            and no synchronous replication), and n (n-1 replicas are kept and
            any two copies are replicated across servers synchronously, meaning
            every write to the master is copied to all slaves before operation
            is reported successful).
        :type replication_factor: int
        :param write_concern: Write concern for the collection. Determines how
            many copies of each shard are required to be in sync on different
            DBServers. If there are less than these many copies in the cluster
            a shard will refuse to write. Writes to shards with enough
            up-to-date copies will succeed at the same time. The value of this
            parameter cannot be larger than that of **replication_factor**.
            Default value is 1. Used for clusters only.
        :type write_concern: int
        :return: Graph API wrapper.
        :rtype: arango.graph.Graph
        :raise arango.exceptions.GraphCreateError: If create fails.

        Here is an example entry for parameter **edge_definitions**:

        .. code-block:: python

            [
                {
                    'edge_collection': 'teach',
                    'from_vertex_collections': ['teachers'],
                    'to_vertex_collections': ['lectures']
                }
            ]
        """
        data: Json = {"name": name, "options": dict()}
        if edge_definitions is not None:
            data["edgeDefinitions"] = [
                {
                    "collection": definition["edge_collection"],
                    "from": definition["from_vertex_collections"],
                    "to": definition["to_vertex_collections"],
                }
                for definition in edge_definitions
            ]
        if orphan_collections is not None:
            data["orphanCollections"] = orphan_collections
        if smart is not None:  # pragma: no cover
            data["isSmart"] = smart
        if disjoint is not None:  # pragma: no cover
            data["isDisjoint"] = disjoint
        if smart_field is not None:  # pragma: no cover
            data["options"]["smartGraphAttribute"] = smart_field
        if shard_count is not None:  # pragma: no cover
            data["options"]["numberOfShards"] = shard_count
        if replication_factor is not None:  # pragma: no cover
            data["options"]["replicationFactor"] = replication_factor
        if write_concern is not None:  # pragma: no cover
            data["options"]["writeConcern"] = write_concern

        request = Request(method="post", endpoint="/_api/gharial", data=data)

        def response_handler(resp: Response) -> Graph:
            if resp.is_success:
                return Graph(self._conn, self._executor, name)
            raise GraphCreateError(resp, request)

        return self._execute(request, response_handler)

    def delete_graph(
        self,
        name: str,
        ignore_missing: bool = False,
        drop_collections: Optional[bool] = None,
    ) -> Result[bool]:
        """Drop the graph of the given name from the database.

        :param name: Graph name.
        :type name: str
        :param ignore_missing: Do not raise an exception on missing graph.
        :type ignore_missing: bool
        :param drop_collections: Drop the collections of the graph also. This
            is only if they are not in use by other graphs.
        :type drop_collections: bool | None
        :return: True if graph was deleted successfully, False if graph was not
            found and **ignore_missing** was set to True.
        :rtype: bool
        :raise arango.exceptions.GraphDeleteError: If delete fails.
        """
        params: Params = {}
        if drop_collections is not None:
            params["dropCollections"] = drop_collections

        request = Request(
            method="delete", endpoint=f"/_api/gharial/{name}", params=params
        )

        def response_handler(resp: Response) -> bool:
            if resp.error_code == 1924 and ignore_missing:
                return False
            if not resp.is_success:
                raise GraphDeleteError(resp, request)
            return True

        return self._execute(request, response_handler)

    #######################
    # Document Management #
    #######################

    def has_document(
        self, document: Json, rev: Optional[str] = None, check_rev: bool = True
    ) -> Result[bool]:
        """Check if a document exists.

        :param document: Document ID or body with "_id" field.
        :type document: str | dict
        :param rev: Expected document revision. Overrides value of "_rev" field
            in **document** if present.
        :type rev: str | None
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :return: True if document exists, False otherwise.
        :rtype: bool
        :raise arango.exceptions.DocumentInError: If check fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_doc(document).has(
            document=document, rev=rev, check_rev=check_rev
        )

    def document(
        self, document: Json, rev: Optional[str] = None, check_rev: bool = True
    ) -> Result[Optional[Json]]:
        """Return a document.

        :param document: Document ID or body with "_id" field.
        :type document: str | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **document** if present.
        :type rev: str | None
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :return: Document, or None if not found.
        :rtype: dict | None
        :raise arango.exceptions.DocumentGetError: If retrieval fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_doc(document).get(
            document=document, rev=rev, check_rev=check_rev
        )

    def insert_document(
        self,
        collection: str,
        document: Json,
        return_new: bool = False,
        sync: Optional[bool] = None,
        silent: bool = False,
        overwrite: bool = False,
        return_old: bool = False,
        overwrite_mode: Optional[str] = None,
        keep_none: Optional[bool] = None,
        merge: Optional[bool] = None,
    ) -> Result[Union[bool, Json]]:
        """Insert a new document.

        :param collection: Collection name.
        :type collection: str
        :param document: Document to insert. If it contains the "_key" or "_id"
            field, the value is used as the key of the new document (otherwise
            it is auto-generated). Any "_rev" field is ignored.
        :type document: dict
        :param return_new: Include body of the new document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_new: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :param overwrite: If set to True, operation does not fail on duplicate
            key and the existing document is replaced.
        :type overwrite: bool
        :param return_old: Include body of the old document if replaced.
            Applies only when value of **overwrite** is set to True.
        :type return_old: bool
        :param overwrite_mode: Overwrite behavior used when the document key
            exists already. Allowed values are "replace" (replace-insert) or
            "update" (update-insert). Implicitly sets the value of parameter
            **overwrite**.
        :type overwrite_mode: str | None
        :param keep_none: If set to True, fields with value None are retained
            in the document. Otherwise, they are removed completely. Applies
            only when **overwrite_mode** is set to "update" (update-insert).
        :type keep_none: bool | None
        :param merge: If set to True (default), sub-dictionaries are merged
            instead of the new one overwriting the old one. Applies only when
            **overwrite_mode** is set to "update" (update-insert).
        :type merge: bool | None
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentInsertError: If insert fails.
        """
        return self.collection(collection).insert(
            document=document,
            return_new=return_new,
            sync=sync,
            silent=silent,
            overwrite=overwrite,
            return_old=return_old,
            overwrite_mode=overwrite_mode,
            keep_none=keep_none,
            merge=merge,
        )

    def update_document(
        self,
        document: Json,
        check_rev: bool = True,
        merge: bool = True,
        keep_none: bool = True,
        return_new: bool = False,
        return_old: bool = False,
        sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Update a document.

        :param document: Partial or full document with the updated values. It
            must contain the "_id" field.
        :type document: dict
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :param merge: If set to True, sub-dictionaries are merged instead of
            the new one overwriting the old one.
        :type merge: bool | None
        :param keep_none: If set to True, fields with value None are retained
            in the document. Otherwise, they are removed completely.
        :type keep_none: bool | None
        :param return_new: Include body of the new document in the result.
        :type return_new: bool
        :param return_old: Include body of the old document in the result.
        :type return_old: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentUpdateError: If update fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_doc(document).update(
            document=document,
            check_rev=check_rev,
            merge=merge,
            keep_none=keep_none,
            return_new=return_new,
            return_old=return_old,
            sync=sync,
            silent=silent,
        )

    def replace_document(
        self,
        document: Json,
        check_rev: bool = True,
        return_new: bool = False,
        return_old: bool = False,
        sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Replace a document.

        :param document: New document to replace the old one with. It must
            contain the "_id" field. Edge document must also have "_from" and
            "_to" fields.
        :type document: dict
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :param return_new: Include body of the new document in the result.
        :type return_new: bool
        :param return_old: Include body of the old document in the result.
        :type return_old: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentReplaceError: If replace fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_doc(document).replace(
            document=document,
            check_rev=check_rev,
            return_new=return_new,
            return_old=return_old,
            sync=sync,
            silent=silent,
        )

    def delete_document(
        self,
        document: Union[str, Json],
        rev: Optional[str] = None,
        check_rev: bool = True,
        ignore_missing: bool = False,
        return_old: bool = False,
        sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Delete a document.

        :param document: Document ID, key or body. Document body must contain
            the "_id" field.
        :type document: str | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **document** if present.
        :type rev: str | None
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :param ignore_missing: Do not raise an exception on missing document.
            This parameter has no effect in transactions where an exception is
            always raised on failures.
        :type ignore_missing: bool
        :param return_old: Include body of the old document in the result.
        :type return_old: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: Document metadata (e.g. document key, revision), or True if
            parameter **silent** was set to True, or False if document was not
            found and **ignore_missing** was set to True (does not apply in
            transactions).
        :rtype: bool | dict
        :raise arango.exceptions.DocumentDeleteError: If delete fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        return self._get_col_by_doc(document).delete(
            document=document,
            rev=rev,
            check_rev=check_rev,
            ignore_missing=ignore_missing,
            return_old=return_old,
            sync=sync,
            silent=silent,
        )

    ###################
    # Task Management #
    ###################

    def tasks(self) -> Result[Jsons]:
        """Return all currently active server tasks.

        :return: Currently active server tasks.
        :rtype: [dict]
        :raise arango.exceptions.TaskListError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/tasks")

        def response_handler(resp: Response) -> Jsons:
            if not resp.is_success:
                raise TaskListError(resp, request)
            result: Jsons = resp.body
            return result

        return self._execute(request, response_handler)

    def task(self, task_id: str) -> Result[Json]:
        """Return the details of an active server task.

        :param task_id: Server task ID.
        :type task_id: str
        :return: Server task details.
        :rtype: dict
        :raise arango.exceptions.TaskGetError: If retrieval fails.
        """
        request = Request(method="get", endpoint=f"/_api/tasks/{task_id}")

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_body(resp.body)
            raise TaskGetError(resp, request)

        return self._execute(request, response_handler)

    def create_task(
        self,
        name: str,
        command: str,
        params: Optional[Json] = None,
        period: Optional[int] = None,
        offset: Optional[int] = None,
        task_id: Optional[str] = None,
    ) -> Result[Json]:
        """Create a new server task.

        :param name: Name of the server task.
        :type name: str
        :param command: Javascript command to execute.
        :type command: str
        :param params: Optional parameters passed into the Javascript command.
        :type params: dict | None
        :param period: Number of seconds to wait between executions. If set
            to 0, the new task will be "timed", meaning it will execute only
            once and be deleted afterwards.
        :type period: int | None
        :param offset: Initial delay before execution in seconds.
        :type offset: int | None
        :param task_id: Pre-defined ID for the new server task.
        :type task_id: str | None
        :return: Details of the new task.
        :rtype: dict
        :raise arango.exceptions.TaskCreateError: If create fails.
        """
        data: Json = {"name": name, "command": command}
        if params is not None:
            data["params"] = params
        if task_id is not None:
            data["id"] = task_id
        if period is not None:
            data["period"] = period
        if offset is not None:
            data["offset"] = offset

        if task_id is None:
            task_id = ""

        request = Request(method="post", endpoint=f"/_api/tasks/{task_id}", data=data)

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_body(resp.body)
            raise TaskCreateError(resp, request)

        return self._execute(request, response_handler)

    def delete_task(self, task_id: str, ignore_missing: bool = False) -> Result[bool]:
        """Delete a server task.

        :param task_id: Server task ID.
        :type task_id: str
        :param ignore_missing: Do not raise an exception on missing task.
        :type ignore_missing: bool
        :return: True if task was successfully deleted, False if task was not
            found and **ignore_missing** was set to True.
        :rtype: bool
        :raise arango.exceptions.TaskDeleteError: If delete fails.
        """
        request = Request(method="delete", endpoint=f"/_api/tasks/{task_id}")

        def response_handler(resp: Response) -> bool:
            if resp.error_code == 1852 and ignore_missing:
                return False
            if not resp.is_success:
                raise TaskDeleteError(resp, request)
            return True

        return self._execute(request, response_handler)

    ###################
    # User Management #
    ###################

    def has_user(self, username: str) -> Result[bool]:
        """Check if user exists.

        :param username: Username.
        :type username: str
        :return: True if user exists, False otherwise.
        :rtype: bool
        """
        request = Request(method="get", endpoint="/_api/user")

        def response_handler(resp: Response) -> bool:
            if not resp.is_success:
                raise UserListError(resp, request)
            return any(user["user"] == username for user in resp.body["result"])

        return self._execute(request, response_handler)

    def users(self) -> Result[Jsons]:
        """Return all user details.

        :return: List of user details.
        :rtype: [dict]
        :raise arango.exceptions.UserListError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/user")

        def response_handler(resp: Response) -> Jsons:
            if not resp.is_success:
                raise UserListError(resp, request)
            return [
                {
                    "username": record["user"],
                    "active": record["active"],
                    "extra": record["extra"],
                }
                for record in resp.body["result"]
            ]

        return self._execute(request, response_handler)

    def user(self, username: str) -> Result[Json]:
        """Return user details.

        :param username: Username.
        :type username: str
        :return: User details.
        :rtype: dict
        :raise arango.exceptions.UserGetError: If retrieval fails.
        """
        request = Request(method="get", endpoint=f"/_api/user/{username}")

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise UserGetError(resp, request)
            return {
                "username": resp.body["user"],
                "active": resp.body["active"],
                "extra": resp.body["extra"],
            }

        return self._execute(request, response_handler)

    def create_user(
        self,
        username: str,
        password: Optional[str] = None,
        active: Optional[bool] = None,
        extra: Optional[Json] = None,
    ) -> Result[Json]:
        """Create a new user.

        :param username: Username.
        :type username: str
        :param password: Password.
        :type password: str | None
        :param active: True if user is active, False otherwise.
        :type active: bool | None
        :param extra: Additional data for the user.
        :type extra: dict | None
        :return: New user details.
        :rtype: dict
        :raise arango.exceptions.UserCreateError: If create fails.
        """
        data: Json = {"user": username, "passwd": password, "active": active}
        if extra is not None:
            data["extra"] = extra

        request = Request(method="post", endpoint="/_api/user", data=data)

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise UserCreateError(resp, request)
            return {
                "username": resp.body["user"],
                "active": resp.body["active"],
                "extra": resp.body["extra"],
            }

        return self._execute(request, response_handler)

    def update_user(
        self,
        username: str,
        password: Optional[str] = None,
        active: Optional[bool] = None,
        extra: Optional[Json] = None,
    ) -> Result[Json]:
        """Update a user.

        :param username: Username.
        :type username: str
        :param password: New password.
        :type password: str | None
        :param active: Whether the user is active.
        :type active: bool | None
        :param extra: Additional data for the user.
        :type extra: dict | None
        :return: New user details.
        :rtype: dict
        :raise arango.exceptions.UserUpdateError: If update fails.
        """
        data: Json = {}
        if password is not None:
            data["passwd"] = password
        if active is not None:
            data["active"] = active
        if extra is not None:
            data["extra"] = extra

        request = Request(
            method="patch",
            endpoint=f"/_api/user/{username}",
            data=data,
        )

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise UserUpdateError(resp, request)
            return {
                "username": resp.body["user"],
                "active": resp.body["active"],
                "extra": resp.body["extra"],
            }

        return self._execute(request, response_handler)

    def replace_user(
        self,
        username: str,
        password: str,
        active: Optional[bool] = None,
        extra: Optional[Json] = None,
    ) -> Result[Json]:
        """Replace a user.

        :param username: Username.
        :type username: str
        :param password: New password.
        :type password: str
        :param active: Whether the user is active.
        :type active: bool | None
        :param extra: Additional data for the user.
        :type extra: dict | None
        :return: New user details.
        :rtype: dict
        :raise arango.exceptions.UserReplaceError: If replace fails.
        """
        data: Json = {"user": username, "passwd": password}
        if active is not None:
            data["active"] = active
        if extra is not None:
            data["extra"] = extra

        request = Request(method="put", endpoint=f"/_api/user/{username}", data=data)

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return {
                    "username": resp.body["user"],
                    "active": resp.body["active"],
                    "extra": resp.body["extra"],
                }
            raise UserReplaceError(resp, request)

        return self._execute(request, response_handler)

    def delete_user(self, username: str, ignore_missing: bool = False) -> Result[bool]:
        """Delete a user.

        :param username: Username.
        :type username: str
        :param ignore_missing: Do not raise an exception on missing user.
        :type ignore_missing: bool
        :return: True if user was deleted successfully, False if user was not
            found and **ignore_missing** was set to True.
        :rtype: bool
        :raise arango.exceptions.UserDeleteError: If delete fails.
        """
        request = Request(method="delete", endpoint=f"/_api/user/{username}")

        def response_handler(resp: Response) -> bool:
            if resp.is_success:
                return True
            elif resp.status_code == 404 and ignore_missing:
                return False
            raise UserDeleteError(resp, request)

        return self._execute(request, response_handler)

    #########################
    # Permission Management #
    #########################

    def permissions(self, username: str) -> Result[Json]:
        """Return user permissions for all databases and collections.

        :param username: Username.
        :type username: str
        :return: User permissions for all databases and collections.
        :rtype: dict
        :raise arango.exceptions.PermissionListError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint=f"/_api/user/{username}/database",
            params={"full": True},
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                result: Json = resp.body["result"]
                return result
            raise PermissionListError(resp, request)

        return self._execute(request, response_handler)

    def permission(
        self, username: str, database: str, collection: Optional[str] = None
    ) -> Result[str]:
        """Return user permission for a specific database or collection.

        :param username: Username.
        :type username: str
        :param database: Database name.
        :type database: str
        :param collection: Collection name.
        :type collection: str | None
        :return: Permission for given database or collection.
        :rtype: str
        :raise arango.exceptions.PermissionGetError: If retrieval fails.
        """
        endpoint = f"/_api/user/{username}/database/{database}"
        if collection is not None:
            endpoint += "/" + collection
        request = Request(method="get", endpoint=endpoint)

        def response_handler(resp: Response) -> str:
            if resp.is_success:
                return str(resp.body["result"])
            raise PermissionGetError(resp, request)

        return self._execute(request, response_handler)

    def update_permission(
        self,
        username: str,
        permission: str,
        database: str,
        collection: Optional[str] = None,
    ) -> Result[bool]:
        """Update user permission for a specific database or collection.

        :param username: Username.
        :type username: str
        :param permission: Allowed values are "rw" (read and write), "ro"
            (read only) or "none" (no access).
        :type permission: str
        :param database: Database name.
        :type database: str
        :param collection: Collection name.
        :type collection: str | None
        :return: True if access was granted successfully.
        :rtype: bool
        :raise arango.exceptions.PermissionUpdateError: If update fails.
        """
        endpoint = f"/_api/user/{username}/database/{database}"
        if collection is not None:
            endpoint += "/" + collection

        request = Request(method="put", endpoint=endpoint, data={"grant": permission})

        def response_handler(resp: Response) -> bool:
            if resp.is_success:
                return True
            raise PermissionUpdateError(resp, request)

        return self._execute(request, response_handler)

    def reset_permission(
        self, username: str, database: str, collection: Optional[str] = None
    ) -> Result[bool]:
        """Reset user permission for a specific database or collection.

        :param username: Username.
        :type username: str
        :param database: Database name.
        :type database: str
        :param collection: Collection name.
        :type collection: str
        :return: True if permission was reset successfully.
        :rtype: bool
        :raise arango.exceptions.PermissionRestError: If reset fails.
        """
        endpoint = f"/_api/user/{username}/database/{database}"
        if collection is not None:
            endpoint += "/" + collection

        request = Request(method="delete", endpoint=endpoint)

        def response_handler(resp: Response) -> bool:
            if resp.is_success:
                return True
            raise PermissionResetError(resp, request)

        return self._execute(request, response_handler)

    ########################
    # Async Job Management #
    ########################

    def async_jobs(self, status: str, count: Optional[int] = None) -> Result[List[str]]:
        """Return IDs of async jobs with given status.

        :param status: Job status (e.g. "pending", "done").
        :type status: str
        :param count: Max number of job IDs to return.
        :type count: int
        :return: List of job IDs.
        :rtype: [str]
        :raise arango.exceptions.AsyncJobListError: If retrieval fails.
        """
        params: Params = {}
        if count is not None:
            params["count"] = count

        request = Request(method="get", endpoint=f"/_api/job/{status}", params=params)

        def response_handler(resp: Response) -> List[str]:
            if resp.is_success:
                result: List[str] = resp.body
                return result
            raise AsyncJobListError(resp, request)

        return self._execute(request, response_handler)

    def clear_async_jobs(self, threshold: Optional[int] = None) -> Result[bool]:
        """Clear async job results from the server.

        Async jobs that are still queued or running are not stopped.

        :param threshold: If specified, only the job results created prior to
            the threshold (a unix timestamp) are deleted. Otherwise, all job
            results are deleted.
        :type threshold: int | None
        :return: True if job results were cleared successfully.
        :rtype: bool
        :raise arango.exceptions.AsyncJobClearError: If operation fails.
        """
        if threshold is None:
            request = Request(method="delete", endpoint="/_api/job/all")
        else:
            request = Request(
                method="delete",
                endpoint="/_api/job/expired",
                params={"stamp": threshold},
            )

        def response_handler(resp: Response) -> bool:
            if resp.is_success:
                return True
            raise AsyncJobClearError(resp, request)

        return self._execute(request, response_handler)

    ###################
    # View Management #
    ###################

    def views(self) -> Result[Jsons]:
        """Return list of views and their summaries.

        :return: List of views.
        :rtype: [dict]
        :raise arango.exceptions.ViewListError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/view")

        def response_handler(resp: Response) -> Jsons:
            if resp.is_success:
                return [format_view(view) for view in resp.body["result"]]
            raise ViewListError(resp, request)

        return self._execute(request, response_handler)

    def view(self, name: str) -> Result[Json]:
        """Return the properties of a View.

        :return: The View properties.
        :rtype: dict
        :raise arango.exceptions.ViewGetError: If retrieval fails.
        """
        request = Request(method="get", endpoint=f"/_api/view/{name}/properties")

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_view(resp.body)
            raise ViewGetError(resp, request)

        return self._execute(request, response_handler)

    def view_info(self, name: str) -> Result[Json]:
        """Return the id, name and type of a View.

        :return: Some View information.
        :rtype: dict
        :raise arango.exceptions.ViewGetError: If retrieval fails.
        """
        request = Request(method="get", endpoint=f"/_api/view/{name}")

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_view(resp.body)
            raise ViewGetError(resp, request)

        return self._execute(request, response_handler)

    def create_view(
        self, name: str, view_type: str, properties: Optional[Json] = None
    ) -> Result[Json]:
        """Create a view.

        :param name: View name.
        :type name: str
        :param view_type: View type (e.g. "arangosearch" or "search-alias").
        :type view_type: str
        :param properties: View properties. For more information see
            https://www.arangodb.com/docs/stable/http/views-arangosearch.html
        :type properties: dict
        :return: View details.
        :rtype: dict
        :raise arango.exceptions.ViewCreateError: If create fails.
        """
        data: Json = {"name": name, "type": view_type}

        if properties is not None:
            data.update(properties)

        request = Request(method="post", endpoint="/_api/view", data=data)

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_view(resp.body)
            raise ViewCreateError(resp, request)

        return self._execute(request, response_handler)

    def update_view(self, name: str, properties: Json) -> Result[Json]:
        """Update a view.

        :param name: View name.
        :type name: str
        :param properties: View properties. For more information see
            https://www.arangodb.com/docs/stable/http/views-arangosearch.html
        :type properties: dict
        :return: View details.
        :rtype: dict
        :raise arango.exceptions.ViewUpdateError: If update fails.
        """
        request = Request(
            method="patch",
            endpoint=f"/_api/view/{name}/properties",
            data=properties,
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_view(resp.body)
            raise ViewUpdateError(resp, request)

        return self._execute(request, response_handler)

    def replace_view(self, name: str, properties: Json) -> Result[Json]:
        """Replace a view.

        :param name: View name.
        :type name: str
        :param properties: View properties. For more information see
            https://www.arangodb.com/docs/stable/http/views-arangosearch.html
        :type properties: dict
        :return: View details.
        :rtype: dict
        :raise arango.exceptions.ViewReplaceError: If replace fails.
        """
        request = Request(
            method="put",
            endpoint=f"/_api/view/{name}/properties",
            data=properties,
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_view(resp.body)
            raise ViewReplaceError(resp, request)

        return self._execute(request, response_handler)

    def delete_view(self, name: str, ignore_missing: bool = False) -> Result[bool]:
        """Delete a view.

        :param name: View name.
        :type name: str
        :param ignore_missing: Do not raise an exception on missing view.
        :type ignore_missing: bool
        :return: True if view was deleted successfully, False if view was not
            found and **ignore_missing** was set to True.
        :rtype: bool
        :raise arango.exceptions.ViewDeleteError: If delete fails.
        """
        request = Request(method="delete", endpoint=f"/_api/view/{name}")

        def response_handler(resp: Response) -> bool:
            if resp.error_code == 1203 and ignore_missing:
                return False
            if resp.is_success:
                return True
            raise ViewDeleteError(resp, request)

        return self._execute(request, response_handler)

    def rename_view(self, name: str, new_name: str) -> Result[bool]:
        """Rename a view.

        :param name: View name.
        :type name: str
        :param new_name: New view name.
        :type new_name: str
        :return: True if view was renamed successfully.
        :rtype: bool
        :raise arango.exceptions.ViewRenameError: If delete fails.
        """
        request = Request(
            method="put",
            endpoint=f"/_api/view/{name}/rename",
            data={"name": new_name},
        )

        def response_handler(resp: Response) -> bool:
            if resp.is_success:
                return True
            raise ViewRenameError(resp, request)

        return self._execute(request, response_handler)

    ################################
    # ArangoSearch View Management #
    ################################

    def create_arangosearch_view(
        self, name: str, properties: Optional[Json] = None
    ) -> Result[Json]:
        """Create an ArangoSearch view.

        :param name: View name.
        :type name: str
        :param properties: View properties. For more information see
            https://www.arangodb.com/docs/stable/http/views-arangosearch.html
        :type properties: dict | None
        :return: View details.
        :rtype: dict
        :raise arango.exceptions.ViewCreateError: If create fails.
        """
        data: Json = {"name": name, "type": "arangosearch"}

        if properties is not None:
            data.update(properties)

        request = Request(method="post", endpoint="/_api/view#ArangoSearch", data=data)

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_view(resp.body)
            raise ViewCreateError(resp, request)

        return self._execute(request, response_handler)

    def update_arangosearch_view(self, name: str, properties: Json) -> Result[Json]:
        """Update an ArangoSearch view.

        :param name: View name.
        :type name: str
        :param properties: View properties. For more information see
            https://www.arangodb.com/docs/stable/http/views-arangosearch.html
        :type properties: dict
        :return: View details.
        :rtype: dict
        :raise arango.exceptions.ViewUpdateError: If update fails.
        """
        request = Request(
            method="patch",
            endpoint=f"/_api/view/{name}/properties#ArangoSearch",
            data=properties,
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_view(resp.body)
            raise ViewUpdateError(resp, request)

        return self._execute(request, response_handler)

    def replace_arangosearch_view(self, name: str, properties: Json) -> Result[Json]:
        """Replace an ArangoSearch view.

        :param name: View name.
        :type name: str
        :param properties: View properties. For more information see
            https://www.arangodb.com/docs/stable/http/views-arangosearch.html
        :type properties: dict
        :return: View details.
        :rtype: dict
        :raise arango.exceptions.ViewReplaceError: If replace fails.
        """
        request = Request(
            method="put",
            endpoint=f"/_api/view/{name}/properties#ArangoSearch",
            data=properties,
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_view(resp.body)
            raise ViewReplaceError(resp, request)

        return self._execute(request, response_handler)

    #######################
    # Analyzer Management #
    #######################

    def analyzers(self) -> Result[Jsons]:
        """Return list of analyzers.

        :return: List of analyzers.
        :rtype: [dict]
        :raise arango.exceptions.AnalyzerListError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/analyzer")

        def response_handler(resp: Response) -> Jsons:
            if resp.is_success:
                result: Jsons = resp.body["result"]
                return result
            raise AnalyzerListError(resp, request)

        return self._execute(request, response_handler)

    def analyzer(self, name: str) -> Result[Json]:
        """Return analyzer details.

        :param name: Analyzer name.
        :type name: str
        :return: Analyzer details.
        :rtype: dict
        :raise arango.exceptions.AnalyzerGetError: If retrieval fails.
        """
        request = Request(method="get", endpoint=f"/_api/analyzer/{name}")

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_body(resp.body)
            raise AnalyzerGetError(resp, request)

        return self._execute(request, response_handler)

    def create_analyzer(
        self,
        name: str,
        analyzer_type: str,
        properties: Optional[Json] = None,
        features: Optional[Sequence[str]] = None,
    ) -> Result[Json]:
        """Create an analyzer.

        :param name: Analyzer name.
        :type name: str
        :param analyzer_type: Analyzer type.
        :type analyzer_type: str
        :param properties: Analyzer properties.
        :type properties: dict | None
        :param features: Analyzer features.
        :type features: list | None
        :return: Analyzer details.
        :rtype: dict
        :raise arango.exceptions.AnalyzerCreateError: If create fails.
        """
        data: Json = {"name": name, "type": analyzer_type}

        if properties is not None:
            data["properties"] = properties

        if features is not None:
            data["features"] = features

        request = Request(method="post", endpoint="/_api/analyzer", data=data)

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                result: Json = resp.body
                return result
            raise AnalyzerCreateError(resp, request)

        return self._execute(request, response_handler)

    def delete_analyzer(
        self, name: str, force: bool = False, ignore_missing: bool = False
    ) -> Result[bool]:
        """Delete an analyzer.

        :param name: Analyzer name.
        :type name: str
        :param force: Remove the analyzer configuration even if in use.
        :type force: bool
        :param ignore_missing: Do not raise an exception on missing analyzer.
        :type ignore_missing: bool
        :return: True if analyzer was deleted successfully, False if analyzer
            was not found and **ignore_missing** was set to True.
        :rtype: bool
        :raise arango.exceptions.AnalyzerDeleteError: If delete fails.
        """
        request = Request(
            method="delete",
            endpoint=f"/_api/analyzer/{name}",
            params={"force": force},
        )

        def response_handler(resp: Response) -> bool:
            if resp.error_code in {1202, 404} and ignore_missing:
                return False
            if resp.is_success:
                return True
            raise AnalyzerDeleteError(resp, request)

        return self._execute(request, response_handler)

    ###########
    # Support #
    ###########

    def support_info(self) -> Result[Json]:
        """Return information about the deployment.

        Retrieves deployment information for support purposes.
        The endpoint returns data about the ArangoDB version used,
        the host (operating system, server ID, CPU and storage capacity,
        current utilization, a few metrics) and the other servers in the
        deployment (in case of Active Failover or cluster deployments).

        NOTE: This method can only be accessed from inside the **_system** database.
        The is a policy control startup option `--server.support-info-api` that controls
        if and to whom the API is made available.

        :return: Deployment information.
        :rtype: dict
        :raise arango.exceptions.DatabaseSupportInfoError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_admin/support-info")

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                result: Json = resp.body
                return result

            raise DatabaseSupportInfoError(resp, request)

        return self._execute(request, response_handler)


class StandardDatabase(Database):
    """Standard database API wrapper."""

    def __init__(self, connection: Connection) -> None:
        super().__init__(connection=connection, executor=DefaultApiExecutor(connection))

    def __repr__(self) -> str:
        return f"<StandardDatabase {self.name}>"

    def begin_async_execution(self, return_result: bool = True) -> "AsyncDatabase":
        """Begin async execution.

        :param return_result: If set to True, API executions return instances
            of :class:`arango.job.AsyncJob`, which you can use to retrieve
            results from server once available. If set to False, API executions
            return None and no results are stored on server.
        :type return_result: bool
        :return: Database API wrapper object specifically for async execution.
        :rtype: arango.database.AsyncDatabase
        """
        return AsyncDatabase(self._conn, return_result)

    def begin_batch_execution(
        self,
        return_result: bool = True,
        max_workers: Optional[int] = 1,
    ) -> "BatchDatabase":
        """Begin batch execution.

        .. warning::

            The batch request API is deprecated since ArangoDB 3.8.0.
            This functionality should no longer be used.
            To send multiple documents at once to an ArangoDB instance,
            please use any of :class:`arango.collection.Collection` methods
            that accept a list of documents as input.
            See :func:`~arango.collection.Collection.insert_many`,
            :func:`~arango.collection.Collection.update_many`,
            :func:`~arango.collection.Collection.replace_many`,
            :func:`~arango.collection.Collection.delete_many`.

        :param return_result: If set to True, API executions return instances
            of :class:`arango.job.BatchJob` that are populated with results on
            commit. If set to False, API executions return None and no results
            are tracked client-side.
        :type return_result: bool
        :param max_workers: Maximum number of workers to use for submitting
            requests asynchronously. If None, the default value is the minimum
            between `os.cpu_count()` and the number of requests.
        :type max_workers: Optional[int]
        :return: Database API wrapper object specifically for batch execution.
        :rtype: arango.database.BatchDatabase
        """
        return BatchDatabase(self._conn, return_result, max_workers)

    def fetch_transaction(self, transaction_id: str) -> "TransactionDatabase":
        """Fetch an existing transaction.

        :param transaction_id: The ID of the existing transaction.
        :type transaction_id: str
        """
        return TransactionDatabase(connection=self._conn, transaction_id=transaction_id)

    def begin_transaction(
        self,
        read: Union[str, Sequence[str], None] = None,
        write: Union[str, Sequence[str], None] = None,
        exclusive: Union[str, Sequence[str], None] = None,
        sync: Optional[bool] = None,
        allow_implicit: Optional[bool] = None,
        lock_timeout: Optional[int] = None,
        max_size: Optional[int] = None,
    ) -> "TransactionDatabase":
        """Begin a transaction.

        :param read: Name(s) of collections read during transaction. Read-only
            collections are added lazily but should be declared if possible to
            avoid deadlocks.
        :type read: str | [str] | None
        :param write: Name(s) of collections written to during transaction with
            shared access.
        :type write: str | [str] | None
        :param exclusive: Name(s) of collections written to during transaction
            with exclusive access.
        :type exclusive: str | [str] | None
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param allow_implicit: Allow reading from undeclared collections.
        :type allow_implicit: bool | None
        :param lock_timeout: Timeout for waiting on collection locks. If not
            given, a default value is used. Setting it to 0 disables the
            timeout.
        :type lock_timeout: int | None
        :param max_size: Max transaction size in bytes.
        :type max_size: int | None
        :return: Database API wrapper object specifically for transactions.
        :rtype: arango.database.TransactionDatabase
        """
        return TransactionDatabase(
            connection=self._conn,
            read=read,
            write=write,
            exclusive=exclusive,
            sync=sync,
            allow_implicit=allow_implicit,
            lock_timeout=lock_timeout,
            max_size=max_size,
        )

    def begin_controlled_execution(
        self, max_queue_time_seconds: Optional[float] = None
    ) -> "OverloadControlDatabase":
        """Begin a controlled connection, with options to handle server-side overload.

        :param max_queue_time_seconds: Maximum time in seconds a request can be queued
            on the server-side. If set to 0 or None, the server ignores this setting.
        :type max_queue_time_seconds: Optional[float]
        :return: Database API wrapper object specifically for queue bounded execution.
        :rtype: arango.database.OverloadControlDatabase
        """
        return OverloadControlDatabase(self._conn, max_queue_time_seconds)


class AsyncDatabase(Database):
    """Database API wrapper tailored specifically for async execution.

    See :func:`arango.database.StandardDatabase.begin_async_execution`.

    :param connection: HTTP connection.
    :param return_result: If set to True, API executions return instances of
        :class:`arango.job.AsyncJob`, which you can use to retrieve results
        from server once available. If set to False, API executions return None
        and no results are stored on server.
    :type return_result: bool
    """

    def __init__(self, connection: Connection, return_result: bool) -> None:
        self._executor: AsyncApiExecutor
        super().__init__(
            connection=connection, executor=AsyncApiExecutor(connection, return_result)
        )

    def __repr__(self) -> str:
        return f"<AsyncDatabase {self.name}>"


class BatchDatabase(Database):
    """Database API wrapper tailored specifically for batch execution.

    .. note::

        This class is not intended to be instantiated directly.
        See
        :func:`arango.database.StandardDatabase.begin_batch_execution`.

    :param connection: HTTP connection.
    :param return_result: If set to True, API executions return instances of
        :class:`arango.job.BatchJob` that are populated with results on commit.
        If set to False, API executions return None and no results are tracked
        client-side.
    :type return_result: bool
    :param max_workers: Use a thread pool of at most `max_workers`.
    :type max_workers: Optional[int]
    """

    def __init__(
        self, connection: Connection, return_result: bool, max_workers: Optional[int]
    ) -> None:
        self._executor: BatchApiExecutor
        super().__init__(
            connection=connection,
            executor=BatchApiExecutor(connection, return_result, max_workers),
        )
        warn(
            "The batch request API is deprecated since ArangoDB version 3.8.0.",
            FutureWarning,
            stacklevel=3,
        )

    def __repr__(self) -> str:
        return f"<BatchDatabase {self.name}>"

    def __enter__(self) -> "BatchDatabase":
        return self

    def __exit__(self, exception: Exception, *_: Any) -> None:
        if exception is None:
            self._executor.commit()

    def queued_jobs(self) -> Optional[Sequence[BatchJob[Any]]]:
        """Return the queued batch jobs.

        :return: Queued batch jobs or None if **return_result** parameter was
            set to False during initialization.
        :rtype: [arango.job.BatchJob] | None
        """
        return self._executor.jobs

    def commit(self) -> Optional[Sequence[BatchJob[Any]]]:
        """Execute the queued requests in a single batch API request.

        If **return_result** parameter was set to True during initialization,
        :class:`arango.job.BatchJob` instances are populated with results.

        :return: Batch jobs, or None if **return_result** parameter was set to
            False during initialization.
        :rtype: [arango.job.BatchJob] | None
        :raise arango.exceptions.BatchStateError: If batch state is invalid
            (e.g. batch was already committed or the response size did not
            match expected).
        :raise arango.exceptions.BatchExecuteError: If commit fails.
        """
        return self._executor.commit()


class TransactionDatabase(Database):
    """Database API wrapper tailored specifically for transactions.

    See :func:`arango.database.StandardDatabase.begin_transaction`.

    :param connection: HTTP connection.
    :param read: Name(s) of collections read during transaction. Read-only
        collections are added lazily but should be declared if possible to
        avoid deadlocks.
    :type read: str | [str] | None
    :param write: Name(s) of collections written to during transaction with
        shared access.
    :type write: str | [str] | None
    :param exclusive: Name(s) of collections written to during transaction
        with exclusive access.
    :type exclusive: str | [str] | None
    :param sync: Block until operation is synchronized to disk.
    :type sync: bool | None
    :param allow_implicit: Allow reading from undeclared collections.
    :type allow_implicit: bool | None
    :param lock_timeout: Timeout for waiting on collection locks. If not given,
        a default value is used. Setting it to 0 disables the timeout.
    :type lock_timeout: int | None
    :param max_size: Max transaction size in bytes.
    :type max_size: int | None
    :param transaction_id: Initialize using an existing transaction instead of creating
        a new transaction.
    :type transaction_id: str | None
    """

    def __init__(
        self,
        connection: Connection,
        read: Union[str, Sequence[str], None] = None,
        write: Union[str, Sequence[str], None] = None,
        exclusive: Union[str, Sequence[str], None] = None,
        sync: Optional[bool] = None,
        allow_implicit: Optional[bool] = None,
        lock_timeout: Optional[int] = None,
        max_size: Optional[int] = None,
        transaction_id: Optional[str] = None,
    ) -> None:
        self._executor: TransactionApiExecutor
        super().__init__(
            connection=connection,
            executor=TransactionApiExecutor(
                connection=connection,
                read=read,
                write=write,
                exclusive=exclusive,
                sync=sync,
                allow_implicit=allow_implicit,
                lock_timeout=lock_timeout,
                max_size=max_size,
                transaction_id=transaction_id,
            ),
        )

    def __repr__(self) -> str:
        return f"<TransactionDatabase {self.name}>"

    @property
    def transaction_id(self) -> str:
        """Return the transaction ID.

        :return: Transaction ID.
        :rtype: str
        """
        return self._executor.id

    def transaction_status(self) -> str:
        """Return the transaction status.

        :return: Transaction status.
        :rtype: str
        :raise arango.exceptions.TransactionStatusError: If retrieval fails.
        """
        return self._executor.status()

    def commit_transaction(self) -> bool:
        """Commit the transaction.

        :return: True if commit was successful.
        :rtype: bool
        :raise arango.exceptions.TransactionCommitError: If commit fails.
        """
        return self._executor.commit()

    def abort_transaction(self) -> bool:
        """Abort the transaction.

        :return: True if the abort operation was successful.
        :rtype: bool
        :raise arango.exceptions.TransactionAbortError: If abort fails.
        """
        return self._executor.abort()


class OverloadControlDatabase(Database):
    """Database API wrapper tailored to gracefully handle server overload scenarios.

    See :func:`arango.database.StandardDatabase.begin_controlled_execution`.

    :param connection: HTTP connection.
    :param max_queue_time_seconds: Maximum server-side queuing time in seconds.
        If the server-side queuing time exceeds the client's specified limit,
        the request will be rejected.
    :type max_queue_time_seconds: Optional[float]
    """

    def __init__(
        self, connection: Connection, max_queue_time_seconds: Optional[float] = None
    ) -> None:
        self._executor: OverloadControlApiExecutor
        super().__init__(
            connection=connection,
            executor=OverloadControlApiExecutor(connection, max_queue_time_seconds),
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<OverloadControlDatabase {self.name}>"

    @property
    def last_queue_time(self) -> float:
        """Return the most recently recorded server-side queuing time in seconds.

        :return: Server-side queuing time in seconds.
        :rtype: float
        """
        return self._executor.queue_time_seconds

    @property
    def max_queue_time(self) -> Optional[float]:
        """Return the maximum server-side queuing time in seconds.

        :return: Maximum server-side queuing time in seconds.
        :rtype: Optional[float]
        """
        return self._executor.max_queue_time_seconds

    def adjust_max_queue_time(self, max_queue_time_seconds: Optional[float]) -> None:
        """Adjust the maximum server-side queuing time in seconds.

        :param max_queue_time_seconds: New maximum server-side queuing time
            in seconds. Setting it to None disables the limit.
        :type max_queue_time_seconds: Optional[float]
        """
        self._executor.max_queue_time_seconds = max_queue_time_seconds
