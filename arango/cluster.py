from __future__ import absolute_import, unicode_literals

from arango.aql import AQL
from arango.collections import Collection
from arango.connection import Connection
from arango.exceptions import ClusterTestError
from arango.graph import Graph
from arango.utils import HTTP_OK


class ClusterTest(Connection):
    """ArangoDB cluster round-trip test for sharding.

    :param connection: ArangoDB database connection
    :type connection: arango.connection.Connection
    :param shard_id: the ID of the shard to which the request is sent
    :type shard_id: str | unicode
    :param transaction_id: the transaction ID for the request
    :type transaction_id: str | unicode
    :param timeout: the timeout in seconds for the cluster operation, where
        an error is returned if the response does not arrive within the given
        limit (default: 24 hrs)
    :type timeout: int
    :param sync: if set to ``True``, the test uses synchronous mode, otherwise
        asynchronous mode is used (this is mainly for debugging purposes)
    :param sync: bool
    """

    def __init__(self,
                 connection,
                 shard_id,
                 transaction_id=None,
                 timeout=None,
                 sync=None):
        super(ClusterTest, self).__init__(
            protocol=connection.protocol,
            host=connection.host,
            port=connection.port,
            username=connection.username,
            password=connection.password,
            http_client=connection.http_client,
            database=connection.database,
            enable_logging=connection.has_logging
        )
        self._shard_id = shard_id
        self._trans_id = transaction_id
        self._timeout = timeout
        self._sync = sync
        self._aql = AQL(self)
        self._type = 'cluster'

    def __repr__(self):
        return '<ArangoDB cluster round-trip test>'

    def handle_request(self, request, handler):
        """Handle the incoming request and response handler.

        :param request: the API request to be placed in the server-side queue
        :type request: arango.request.Request
        :param handler: the response handler
        :type handler: callable
        :returns: the test results
        :rtype: dict
        :raises arango.exceptions.ClusterTestError: if the cluster round-trip
            test cannot be executed
        """
        request.headers['X-Shard-ID'] = str(self._shard_id)
        if self._trans_id is not None:
            request.headers['X-Client-Transaction-ID'] = str(self._trans_id)
        if self._timeout is not None:
            request.headers['X-Timeout'] = str(self._timeout)
        if self._sync is True:
            request.headers['X-Synchronous-Mode'] = 'true'

        request.endpoint = '/_admin/cluster-test' + request.endpoint + '11'
        res = getattr(self, request.method)(**request.kwargs)
        if res.status_code not in HTTP_OK:
            raise ClusterTestError(res)
        return res.body  # pragma: no cover

    @property
    def aql(self):
        """Return the AQL object tailored for asynchronous execution.

        API requests via the returned query object are placed in a server-side
        in-memory task queue and executed asynchronously in a fire-and-forget
        style.

        :returns: ArangoDB query object
        :rtype: arango.query.AQL
        """
        return self._aql

    def collection(self, name):
        """Return a collection object tailored for asynchronous execution.

        API requests via the returned collection object are placed in a
        server-side in-memory task queue and executed asynchronously in
        a fire-and-forget style.

        :param name: the name of the collection
        :type name: str | unicode
        :returns: the collection object
        :rtype: arango.collections.Collection
        """
        return Collection(self, name)

    def graph(self, name):
        """Return a graph object tailored for asynchronous execution.

        API requests via the returned graph object are placed in a server-side
        in-memory task queue and executed asynchronously in a fire-and-forget
        style.

        :param name: the name of the graph
        :type name: str | unicode
        :returns: the graph object
        :rtype: arango.graph.Graph
        """
        return Graph(self, name)
