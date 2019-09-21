from __future__ import absolute_import, unicode_literals

__all__ = ['Cluster']

from arango.api import APIWrapper
from arango.exceptions import (
    ClusterHealthError,
    ClusterMaintenanceModeError,
    ClusterServerIDError,
    ClusterServerRoleError,
    ClusterStatisticsError,
)
from arango.request import Request


class Cluster(APIWrapper):  # pragma: no cover

    def __init__(self, connection, executor):
        super(Cluster, self).__init__(connection, executor)

    def server_id(self):
        """Return the server ID.

        :return: Server ID.
        :rtype: str | unicode
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
            "SECONDARY", "AGENT" (Agency node in a cluster) or "UNDEFINED".
        :rtype: str | unicode
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

    def statistics(self, server_id):
        """Return the cluster statistics for the given server.

        :param server_id: Server ID.
        :type server_id: str | unicode
        :return: Cluster statistics for the given server.
        :rtype: dict
        :raise arango.exceptions.ClusterStatisticsError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_admin/clusterStatistics',
            params={'DBserver': server_id}
        )

        def response_handler(resp):
            if resp.is_success:
                return resp.body
            raise ClusterStatisticsError(resp, request)

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
        :type mode: str | unicode
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
