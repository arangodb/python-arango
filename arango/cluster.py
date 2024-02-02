__all__ = ["Cluster"]

from typing import List, Optional

from arango.api import ApiGroup
from arango.exceptions import (
    ClusterEndpointsError,
    ClusterHealthError,
    ClusterMaintenanceModeError,
    ClusterRebalanceError,
    ClusterServerCountError,
    ClusterServerEngineError,
    ClusterServerIDError,
    ClusterServerModeError,
    ClusterServerRoleError,
    ClusterServerStatisticsError,
    ClusterServerVersionError,
)
from arango.formatter import format_body
from arango.request import Request
from arango.response import Response
from arango.result import Result
from arango.typings import Json


class Cluster(ApiGroup):  # pragma: no cover
    def server_id(self) -> Result[str]:
        """Return the server ID.

        :return: Server ID.
        :rtype: str
        :raise arango.exceptions.ClusterServerIDError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_admin/server/id")

        def response_handler(resp: Response) -> str:
            if resp.is_success:
                return str(resp.body["id"])
            raise ClusterServerIDError(resp, request)

        return self._execute(request, response_handler)

    def server_role(self) -> Result[str]:
        """Return the server role.

        :return: Server role. Possible values are "SINGLE" (server which is
            not in a cluster), "COORDINATOR" (cluster coordinator), "PRIMARY",
            "SECONDARY", "AGENT" (Agency server in a cluster) or "UNDEFINED".
        :rtype: str
        :raise arango.exceptions.ClusterServerRoleError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_admin/server/role")

        def response_handler(resp: Response) -> str:
            if resp.is_success:
                return str(resp.body["role"])
            raise ClusterServerRoleError(resp, request)

        return self._execute(request, response_handler)

    def server_mode(self) -> Result[str]:
        """Return the server mode.

        In a read-only server, all write operations will fail
        with an error code of 1004 (ERROR_READ_ONLY). Creating or dropping
        databases and collections will also fail with error code 11 (ERROR_FORBIDDEN).

        :return: Server mode. Possible values are "default" or "readonly".
        :rtype: str
        :raise arango.exceptions.ClusterServerModeError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_admin/server/mode")

        def response_handler(resp: Response) -> str:
            if resp.is_success:
                return str(resp.body["mode"])

            raise ClusterServerModeError(resp, request)

        return self._execute(request, response_handler)

    def server_version(self, server_id: str) -> Result[Json]:
        """Return the version of the given server.

        :param server_id: Server ID.
        :type server_id: str
        :return: Version of the given server.
        :rtype: dict
        :raise arango.exceptions.ClusterServerVersionError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint="/_admin/cluster/nodeVersion",
            params={"ServerID": server_id},
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_body(resp.body)
            raise ClusterServerVersionError(resp, request)

        return self._execute(request, response_handler)

    def server_engine(self, server_id: str) -> Result[Json]:
        """Return the engine details for the given server.

        :param server_id: Server ID.
        :type server_id: str
        :return: Engine details of the given server.
        :rtype: dict
        :raise arango.exceptions.ClusterServerEngineError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint="/_admin/cluster/nodeEngine",
            params={"ServerID": server_id},
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_body(resp.body)
            raise ClusterServerEngineError(resp, request)

        return self._execute(request, response_handler)

    def server_count(self) -> Result[int]:
        """Return the number of servers in the cluster.

        :return: Number of servers in the cluster.
        :rtype: int
        :raise arango.exceptions.ClusterServerCountError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_admin/cluster/numberOfServers")

        def response_handler(resp: Response) -> int:
            if resp.is_success:
                result: int = resp.body
                return result
            raise ClusterServerCountError(resp, request)

        return self._execute(request, response_handler)

    def server_statistics(self, server_id: str) -> Result[Json]:
        """Return the statistics for the given server.

        :param server_id: Server ID.
        :type server_id: str
        :return: Statistics for the given server.
        :rtype: dict
        :raise arango.exceptions.ClusterServerStatisticsError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint="/_admin/cluster/nodeStatistics",
            params={"ServerID": server_id},
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_body(resp.body)
            raise ClusterServerStatisticsError(resp, request)

        return self._execute(request, response_handler)

    def server_maintenance_mode(self, server_id: str) -> Result[Json]:
        """Return the maintenance status for the given server.

        :param server_id: Server ID.
        :type server_id: str
        :return: Maintenance status for the given server.
        :rtype: dict
        :raise arango.exceptions.ClusterMaintenanceModeError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint=f"/_admin/cluster/maintenance/{server_id}",
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                result: Json = resp.body.get("result", {})
                return result

            raise ClusterMaintenanceModeError(resp, request)

        return self._execute(request, response_handler)

    def toggle_server_maintenance_mode(
        self, server_id: str, mode: str, timeout: Optional[int] = None
    ) -> Result[Json]:
        """Enable or disable the maintenance mode for the given server.

        :param server_id: Server ID.
        :type server_id: str
        :param mode: Maintenance mode. Allowed values are "normal" and "maintenance".
        :type mode: str
        :param timeout: Timeout in seconds.
        :type timeout: Optional[int]
        :return: Result of the operation.
        :rtype: dict
        :raise arango.exceptions.ClusterMaintenanceModeError: If toggle fails.
        """
        request = Request(
            method="put",
            endpoint=f"/_admin/cluster/maintenance/{server_id}",
            data={"mode": mode, "timeout": timeout},
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_body(resp.body)

            raise ClusterMaintenanceModeError(resp, request)

        return self._execute(request, response_handler)

    def health(self) -> Result[Json]:
        """Return the cluster health.

        :return: Cluster health.
        :rtype: dict
        :raise arango.exceptions.ClusterHealthError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint="/_admin/cluster/health",
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_body(resp.body)
            raise ClusterHealthError(resp, request)

        return self._execute(request, response_handler)

    def toggle_maintenance_mode(self, mode: str) -> Result[Json]:
        """Enable or disable the cluster supervision (agency) maintenance mode.

        :param mode: Maintenance mode. Allowed values are "on" and "off".
        :type mode: str
        :return: Result of the operation.
        :rtype: dict
        :raise arango.exceptions.ClusterMaintenanceModeError: If toggle fails.
        """
        request = Request(
            method="put",
            endpoint="/_admin/cluster/maintenance",
            data=f'"{mode}"',
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_body(resp.body)
            raise ClusterMaintenanceModeError(resp, request)

        return self._execute(request, response_handler)

    def endpoints(self) -> Result[List[str]]:
        """Return coordinate endpoints. This method is for clusters only.

        :return: List of endpoints.
        :rtype: [str]
        :raise arango.exceptions.ServerEndpointsError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/cluster/endpoints")

        def response_handler(resp: Response) -> List[str]:
            if not resp.is_success:
                raise ClusterEndpointsError(resp, request)
            return [item["endpoint"] for item in resp.body["endpoints"]]

        return self._execute(request, response_handler)

    def calculate_imbalance(self) -> Result[Json]:
        """Compute the current cluster imbalance, including
        the amount of ongoing and pending move shard operations.

        :return: Cluster imbalance information.
        :rtype: dict
        :raise: arango.exceptions.ClusterRebalanceError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_admin/cluster/rebalance")

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise ClusterRebalanceError(resp, request)
            result: Json = resp.body["result"]
            return result

        return self._execute(request, response_handler)

    def rebalance(
        self,
        version: int = 1,
        max_moves: Optional[int] = None,
        leader_changes: Optional[bool] = None,
        move_leaders: Optional[bool] = None,
        move_followers: Optional[bool] = None,
        pi_factor: Optional[float] = None,
        exclude_system_collections: Optional[bool] = None,
        databases_excluded: Optional[List[str]] = None,
    ) -> Result[Json]:
        """Compute and execute a cluster rebalance plan.

        :param version: Must be set to 1.
        :type version: int
        :param max_moves: Maximum number of moves to be computed.
        :type max_moves: int | None
        :param leader_changes: Allow leader changes without moving data.
        :type leader_changes: bool | None
        :param move_leaders: Allow moving shard leaders.
        :type move_leaders: bool | None
        :param move_followers: Allow moving shard followers.
        :type move_followers: bool | None
        :param pi_factor: A weighting factor that should remain untouched.
        :type pi_factor: float | None
        :param exclude_system_collections: Ignore system collections in the
            rebalance plan.
        :type exclude_system_collections: bool | None
        :param databases_excluded: List of database names to be excluded
            from the analysis.
        :type databases_excluded: [str] | None
        :return: Cluster rebalance plan that has been executed.
        :rtype: dict
        :raise: arango.exceptions.ClusterRebalanceError: If retrieval fails.
        """
        data: Json = dict(version=version)
        if max_moves is not None:
            data["maximumNumberOfMoves"] = max_moves
        if leader_changes is not None:
            data["leaderChanges"] = leader_changes
        if move_leaders is not None:
            data["moveLeaders"] = move_leaders
        if move_followers is not None:
            data["moveFollowers"] = move_followers
        if pi_factor is not None:
            data["piFactor"] = pi_factor
        if exclude_system_collections is not None:
            data["excludeSystemCollections"] = exclude_system_collections
        if databases_excluded is not None:
            data["databasesExcluded"] = databases_excluded

        request = Request(method="put", endpoint="/_admin/cluster/rebalance", data=data)

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise ClusterRebalanceError(resp, request)
            result: Json = resp.body["result"]
            return result

        return self._execute(request, response_handler)

    def calculate_rebalance_plan(
        self,
        version: int = 1,
        max_moves: Optional[int] = None,
        leader_changes: Optional[bool] = None,
        move_leaders: Optional[bool] = None,
        move_followers: Optional[bool] = None,
        pi_factor: Optional[float] = None,
        exclude_system_collections: Optional[bool] = None,
        databases_excluded: Optional[List[str]] = None,
    ) -> Result[Json]:
        """Compute the cluster rebalance plan.

        :param version: Must be set to 1.
        :type version: int
        :param max_moves: Maximum number of moves to be computed.
        :type max_moves: int | None
        :param leader_changes: Allow leader changes without moving data.
        :type leader_changes: bool | None
        :param move_leaders: Allow moving shard leaders.
        :type move_leaders: bool | None
        :param move_followers: Allow moving shard followers.
        :type move_followers: bool | None
        :param pi_factor: A weighting factor that should remain untouched.
        :type pi_factor: float | None
        :param exclude_system_collections: Ignore system collections in the
            rebalance plan.
        :type exclude_system_collections: bool | None
        :param databases_excluded: List of database names to be excluded
            from the analysis.
        :type databases_excluded: [str] | None
        :return: Cluster rebalance plan.
        :rtype: dict
        :raise: arango.exceptions.ClusterRebalanceError: If retrieval fails.
        """
        data: Json = dict(version=version)
        if max_moves is not None:
            data["maximumNumberOfMoves"] = max_moves
        if leader_changes is not None:
            data["leaderChanges"] = leader_changes
        if move_leaders is not None:
            data["moveLeaders"] = move_leaders
        if move_followers is not None:
            data["moveFollowers"] = move_followers
        if pi_factor is not None:
            data["piFactor"] = pi_factor
        if exclude_system_collections is not None:
            data["excludeSystemCollections"] = exclude_system_collections
        if databases_excluded is not None:
            data["databasesExcluded"] = databases_excluded

        request = Request(
            method="post", endpoint="/_admin/cluster/rebalance", data=data
        )

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise ClusterRebalanceError(resp, request)
            result: Json = resp.body["result"]
            return result

        return self._execute(request, response_handler)

    def execute_rebalance_plan(
        self, moves: List[Json], version: int = 1
    ) -> Result[bool]:
        """Execute the given set of move shard operations.

        You can use :meth:`Cluster.calculate_rebalance_plan` to calculate
        these operations to improve the balance of shards, leader shards,
        and follower shards.

        :param moves: List of move shard operations.
        :type moves: [dict]
        :param version: Must be set to 1.
        :type version: int
        :return: True if the methods have been accepted and scheduled
            for execution.
        :rtype: bool
        :raise: arango.exceptions.ClusterRebalanceError: If request fails.
        """
        data: Json = dict(version=version, moves=moves)

        request = Request(
            method="post", endpoint="/_admin/cluster/rebalance/execute", data=data
        )

        def response_handler(resp: Response) -> bool:
            if not resp.is_success:
                raise ClusterRebalanceError(resp, request)
            result: bool = resp.body["code"] == 202
            return result

        return self._execute(request, response_handler)
