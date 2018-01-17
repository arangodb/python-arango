from __future__ import absolute_import, unicode_literals

from arango.connections.base import BaseConnection
from arango.exceptions import ArangoError


class ClusterTest(BaseConnection):
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
            enable_logging=connection.logging_enabled
        )

        self._url_prefix = \
            '{protocol}://{host}:{port}/_admin/cluster-test/_db/{db}'.format(
                protocol=self._protocol,
                host=self._host,
                port=self._port,
                db=self._database
            )

        self._shard_id = shard_id
        self._trans_id = transaction_id
        self._timeout = timeout
        self._sync = sync
        self._type = 'cluster'
        self._parent = connection

    def __repr__(self):
        return '<ArangoDB cluster round-trip test>'

    def handle_request(self, request, handler, job_class=None):
        """Handle the incoming request and response handler.

        :param request: the API request to be placed in the server-side queue
        :type request: arango.request.Request
        :param handler: the response handler
        :type handler: callable
        :param job_class: the class of the :class:arango.jobs.BaseJob to
        output or None to use the default job for this connection
        :type job_class: class | None
        :returns: the test results
        :rtype: dict
        :raises arango.exceptions.ClusterTestError: if the cluster round-trip
            test cannot be executed
        """
        if job_class is not None:
            raise ArangoError('')

        request.headers['X-Shard-ID'] = str(self._shard_id)
        if self._trans_id is not None:
            request.headers['X-Client-Transaction-ID'] = str(self._trans_id)
        if self._timeout is not None:
            request.headers['X-Timeout'] = str(self._timeout)
        if self._sync is True:
            request.headers['X-Synchronous-Mode'] = 'true'

        return BaseConnection.handle_request(self, request, handler, job_class)
