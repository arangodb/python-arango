from arango.http_clients import DefaultHTTPClient
from arango.connections import BaseConnection
from arango import Request
from arango.utils import HTTP_OK
from arango.database import Database
from arango.exceptions import (
    DatabaseCreateError,
    DatabaseDeleteError,
    ServerEndpointsError
)


class ArangoClient(Database):
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

    """System calls. Every call listed here requires root access."""

    def endpoints(self):
        """Return the list of the endpoints the server is listening on.

        Each endpoint is mapped to a list of databases. If the list is empty,
        it means all databases can be accessed via the endpoint. If the list
        contains more than one database, the first database receives all the
        requests by default, unless the name is explicitly specified.

        :returns: the list of endpoints
        :rtype: list
        :raises arango.exceptions.ServerEndpointsError: if the endpoints
            cannot be retrieved from the server
        """

        request = Request(
            method='get',
            endpoint='/_api/endpoint'
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise ServerEndpointsError(res)
            return res.body

        return self.handle_request(request, handler)

    def create_database(self, name, users=None, username=None, password=None):
        """Create a new database.

        :param name: the name of the new database
        :type name: str | unicode
        :param users: the list of users with access to the new database, where
            each user is a dictionary with keys ``"username"``, ``"password"``,
            ``"active"`` and ``"extra"``.
        :type users: [dict]
        :param username: the username for authentication (if set, overrides
            the username specified during the client initialization)
        :type username: str | unicode
        :param password: the password for authentication (if set, overrides
            the password specified during the client initialization
        :type password: str | unicode
        :returns: the database object
        :rtype: arango.database.Database
        :raises arango.exceptions.DatabaseCreateError: if the create fails

        .. note::
            Here is an example entry in **users**:

            .. code-block:: python

                {
                    'username': 'john',
                    'password': 'password',
                    'active': True,
                    'extra': {'Department': 'IT'}
                }

            If **users** is not set, only the root and the current user are
            granted access to the new database by default.
        """

        data = {
            'name': name,
        }

        if users is not None:
            data['users'] = [{
                'username': user['username'],
                'passwd': user['password'],
                'active': user.get('active', True),
                'extra': user.get('extra', {})
            } for user in users]

        request = Request(
            method='post',
            endpoint='/_api/database',
            data=data
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DatabaseCreateError(res)
            return self.db(name, username, password)

        return self.handle_request(request, handler)

    def delete_database(self, name, ignore_missing=False):
        """Delete the database of the specified name.

        :param name: the name of the database to delete
        :type name: str | unicode
        :param ignore_missing: ignore missing databases
        :type ignore_missing: bool
        :returns: whether the database was deleted successfully
        :rtype: bool
        :raises arango.exceptions.DatabaseDeleteError: if the delete fails

        .. note::
            Root privileges (i.e. access to the ``_system`` database) are
            required to use this method.
        """

        request = Request(
            method='delete',
            endpoint='/_api/database/{}'.format(name)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                if not (res.status_code == 404 and ignore_missing):
                    raise DatabaseDeleteError(res)
            return not res.body['error']

        return self.handle_request(request, handler)
