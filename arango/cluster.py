from __future__ import absolute_import, unicode_literals

__all__ = ['Cluster']

from arango.api import APIWrapper
from arango.exceptions import (
    ClusterEndpointsError,
    ClusterHealthError,
    ClusterMaintenanceModeError,
    ClusterServerCountError,
    ClusterServerEngineError,
    ClusterServerIDError,
    ClusterServerRoleError,
    ClusterServerStatisticsError,
    ClusterServerVersionError,
)
from arango.request import Request


class Cluster(APIWrapper):  # pragma: no cover

    def __init__(self, connection, executor):
        super(Cluster, self).__init__(connection, executor)

    def server_id(self):
        """Return the server ID.

        :return: Server ID.
        :rtype: str
        :raise arango.exceptions.ClusterServerIDError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_admin/server/id'
        )

        def response_handler(resp):
            if resp.is_success:
                return resp.body['id']
            raise ClusterServerIDError(resp, request)

        return self._execute(request, response_handler)

    def server_role(self):
        """Return the server role.

        :return: Server role. Possible values are "SINGLE" (server which is
            not in a cluster), "COORDINATOR" (cluster coordinator), "PRIMARY",
            "SECONDARY", "AGENT" (Agency server in a cluster) or "UNDEFINED".
        :rtype: str
        :raise arango.exceptions.ClusterServerRoleError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_admin/server/role'
        )

        def response_handler(resp):
            if resp.is_success:
                return resp.body['role']
            raise ClusterServerRoleError(resp, request)

        return self._execute(request, response_handler)

    def server_version(self, server_id):
        """Return the version of the given server.

        :param server_id: Server ID.
        :type server_id: str
        :return: Version of the given server.
        :rtype: dict
        :raise arango.exceptions.ClusterServerVersionError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_admin/cluster/nodeVersion',
            params={'ServerID': server_id}
        )

        def response_handler(resp):
            if resp.is_success:
                return resp.body
            raise ClusterServerVersionError(resp, request)

        return self._execute(request, response_handler)

    def server_engine(self, server_id):
        """Return the engine details for the given server.

        :param server_id: Server ID.
        :type server_id: str
        :return: Engine details of the given server.
        :rtype: dict
        :raise arango.exceptions.ClusterServerEngineError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_admin/cluster/nodeEngine',
            params={'ServerID': server_id}
        )

        def response_handler(resp):
            if resp.is_success:
                return resp.body
            raise ClusterServerEngineError(resp, request)

        return self._execute(request, response_handler)

    def server_count(self):
        """Return the number of servers in the cluster.

        :return: Number of servers in the cluster.
        :rtype: int
        :raise arango.exceptions.ClusterServerCountError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_admin/cluster/numberOfServers'
        )

        def response_handler(resp):
            if resp.is_success:
                return resp.body
            raise ClusterServerCountError(resp, request)

        return self._execute(request, response_handler)

    def server_statistics(self, server_id):
        """Return the statistics for the given server.

        :param server_id: Server ID.
        :type server_id: str
        :return: Statistics for the given server.
        :rtype: dict
        :raise arango.exceptions.ClusterServerStatisticsError: If retrieval
            fails.
        """
        request = Request(
            method='get',
            endpoint='/_admin/cluster/nodeStatistics',
            params={'ServerID': server_id}
        )

        def response_handler(resp):
            if resp.is_success:
                return resp.body
            raise ClusterServerStatisticsError(resp, request)

        return self._execute(request, response_handler)

    def health(self):
        """Return the cluster health.

        :return: Cluster health.
        :rtype: dict
        :raise arango.exceptions.ClusterHealthError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_admin/cluster/health',
        )

        def response_handler(resp):
            if resp.is_success:
                resp.body.pop('error')
                resp.body.pop('code')
                return resp.body
            raise ClusterHealthError(resp, request)

        return self._execute(request, response_handler)

    def toggle_maintenance_mode(self, mode):
        """Enable or disable the cluster supervision (agency) maintenance mode.

        :param mode: Maintenance mode. Allowed values are "on" and "off".
        :type mode: str
        :return: Result of the operation.
        :rtype: dict
        :raise arango.exceptions.ClusterMaintenanceModeError: If toggle fails.
        """
        request = Request(
            method='put',
            endpoint='/_admin/cluster/maintenance',
            data='"{}"'.format(mode)
        )

        def response_handler(resp):
            if resp.is_success:
                return resp.body
            raise ClusterMaintenanceModeError(resp, request)

        return self._execute(request, response_handler)

    def endpoints(self):
        """Return coordinate endpoints. This method is for clusters only.

        :return: List of endpoints.
        :rtype: [str]
        :raise arango.exceptions.ServerEndpointsError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_api/cluster/endpoints'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise ClusterEndpointsError(resp, request)
            return [item['endpoint'] for item in resp.body['endpoints']]

        return self._execute(request, response_handler)
