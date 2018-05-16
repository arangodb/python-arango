from __future__ import absolute_import, unicode_literals

__all__ = ['ArangoClient']

from arango.connection import Connection
from arango.database import StandardDatabase
from arango.exceptions import ServerConnectionError
from arango.version import __version__


class ArangoClient(object):
    """ArangoDB client.

    :param protocol: Internet transfer protocol (default: "http").
    :type protocol: str | unicode
    :param host: ArangoDB host (default: "127.0.0.1").
    :type host: str | unicode
    :param port: ArangoDB port (default: 8529).
    :type port: int
    :param http_client: User-defined HTTP client.
    :type http_client: arango.http.HTTPClient
    """

    def __init__(self,
                 protocol='http',
                 host='127.0.0.1',
                 port=8529,
                 http_client=None):
        self._protocol = protocol.strip('/')
        self._host = host.strip('/')
        self._port = int(port)
        self._url = '{}://{}:{}'.format(protocol, host, port)
        self._http_client = http_client

    def __repr__(self):
        return '<ArangoClient {}>'.format(self._url)

    @property
    def version(self):
        """Return the client version.

        :return: Client version.
        :rtype: str | unicode
        """
        return __version__

    @property
    def protocol(self):
        """Return the internet transfer protocol (e.g. "http").

        :return: Internet transfer protocol.
        :rtype: str | unicode
        """
        return self._protocol

    @property
    def host(self):
        """Return the ArangoDB host.

        :return: ArangoDB host.
        :rtype: str | unicode
        """
        return self._host

    @property
    def port(self):
        """Return the ArangoDB port.

        :return: ArangoDB port.
        :rtype: int
        """
        return self._port

    @property
    def base_url(self):
        """Return the ArangoDB base URL.

        :return: ArangoDB base URL.
        :rtype: str | unicode
        """
        return self._url

    def db(self, name='_system', username='root', password='', verify=False):
        """Connect to a database and return the database API wrapper.

        :param name: Database name.
        :type name: str | unicode
        :param username: Username for basic authentication.
        :type username: str | unicode
        :param password: Password for basic authentication.
        :type password: str | unicode
        :param verify: Verify the connection by sending a test request.
        :type verify: bool
        :return: Standard database API wrapper.
        :rtype: arango.database.StandardDatabase
        :raise arango.exceptions.ServerConnectionError: If **verify** was set
            to True and the connection to ArangoDB fails.
        """
        connection = Connection(
            url=self._url,
            db=name,
            username=username,
            password=password,
            http_client=self._http_client
        )
        database = StandardDatabase(connection)

        if verify:  # Check the server connection by making a read API call
            try:
                database.ping()
            except ServerConnectionError as err:
                raise err
            except Exception as err:
                raise ServerConnectionError('bad connection: {}'.format(err))

        return database
