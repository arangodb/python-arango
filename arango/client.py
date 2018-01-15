from arango.databases import SystemDatabase
from arango.http_clients import DefaultHTTPClient
from arango.connections import BaseConnection


class ArangoClient(SystemDatabase):
    """ArangoDB Client.

        :param protocol: The internet transfer protocol (default: ``"http"``).
        :type protocol: str | unicode
        :param host: ArangoDB server host (default: ``"localhost"``).
        :type host: str | unicode
        :param port: ArangoDB server port (default: ``8529``).
        :type port: int or str
        :param username: ArangoDB default username (default: ``"root"``).
        :type username: str | unicode
        :param password: ArangoDB default password (default: ``""``).
        :param verify: Check the connection during initialization. Root
            privileges are required to use this flag.
        :type verify: bool
        :param http_client: Custom HTTP client to override the default one
            with. Please refer to the API documentation for more details.
        :type http_client: arango.http_clients.base.BaseHTTPClient
        :param enable_logging: Log all API requests as debug messages.
        :type enable_logging: bool
        :param check_cert: Verify SSL certificate when making HTTP requests.
            This flag is ignored if a custom **http_client** is specified.
        :type check_cert: bool
        :param use_session: Use session when making HTTP requests. This flag is
            ignored if a custom **http_client** is specified.
        :type use_session: bool
        :param logger: Custom logger to record the API requests with. The
            logger's ``debug`` method is called.
        :type logger: logging.Logger
        """

    def __init__(self,
                 protocol='http',
                 host='127.0.0.1',
                 port=8529,
                 username='root',
                 password='',
                 verify=False,
                 http_client=None,
                 enable_logging=True,
                 check_cert=True,
                 use_session=True,
                 logger=None,
                 async_ready=False):

        if http_client is None:
            http_client = DefaultHTTPClient(
                use_session=use_session,
                check_cert=check_cert
            )

        conn = BaseConnection(
            protocol=protocol,
            host=host,
            port=port,
            database='_system',
            username=username,
            password=password,
            http_client=http_client,
            enable_logging=enable_logging,
            logger=logger,
            async_ready=async_ready
        )

        super(ArangoClient, self).__init__(conn)

        if verify:
            self.verify()

    def __repr__(self):
        return '<ArangoDB client for "{}">'.format(self.connection.host)
