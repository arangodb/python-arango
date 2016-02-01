from __future__ import absolute_import, unicode_literals

import logging

from arango.http_clients import DefaultHTTPClient
from arango.utils import sanitize

logger = logging.getLogger('arango')


class Connection(object):
    """ArangoDB database connection.

    :param protocol: the internet transfer protocol (default: ``"http"``)
    :type protocol: str
    :param host: ArangoDB host (default: ``"localhost"``)
    :type host: str
    :param port: ArangoDB port (default: ``8529``)
    :type port: int | str
    :param database: the name of the target database (default: ``"_system"``)
    :type database: str
    :param username: ArangoDB username (default: ``"root"``)
    :type username: str
    :param password: ArangoDB password (default: ``""``)
    :type password: str
    :param http_client: the HTTP client
    :type http_client: arango.clients.base.BaseHTTPClient
    :param enable_logging: log all API requests with a logger named "arango"
    :type enable_logging: bool
    """

    def __init__(self,
                 protocol='http',
                 host='localhost',
                 port=8529,
                 database='_system',
                 username='root',
                 password='',
                 http_client=None,
                 enable_logging=True):

        self._protocol = protocol.strip('/')
        self._host = host.strip('/')
        self._port = port
        self._database = database or '_system'
        self._url_prefix = '{protocol}://{host}:{port}/_db/{db}'.format(
            protocol=self._protocol,
            host=self._host,
            port=self._port,
            db=self._database
        )
        self._username = username
        self._password = password
        self._http = http_client or DefaultHTTPClient()
        self._logging = enable_logging
        self._type = 'standard'

    def __repr__(self):
        return '<ArangoDB connection to database "{}">'.format(self._database)

    @property
    def protocol(self):
        """Return the internet transfer protocol.

        :returns: the internet transfer protocol
        :rtype: str
        """
        return self._protocol

    @property
    def host(self):
        """Return the ArangoDB host.

        :returns: the ArangoDB host
        :rtype: str
        """
        return self._host

    @property
    def port(self):
        """Return the ArangoDB port.

        :returns: the ArangoDB port
        :rtype: int
        """
        return self._port

    @property
    def username(self):
        """Return the ArangoDB username.

        :returns: the ArangoDB username
        :rtype: str
        """
        return self._username

    @property
    def password(self):
        """Return the ArangoDB user password.

        :returns: the ArangoDB user password
        :rtype: str
        """
        return self._password

    @property
    def database(self):
        """Return the name of the connected database.

        :returns: the name of the connected database
        :rtype: str
        """
        return self._database

    @property
    def http_client(self):
        """Return the HTTP client in use.

        :returns: the HTTP client in use
        :rtype: arango.http_clients.base.BaseHTTPClient
        """
        return self._http

    @property
    def has_logging(self):
        """Return ``True`` if logging is enabled, ``False`` otherwise.

        :returns: whether logging is enabled or not
        :rtype: bool
        """
        return self._logging

    @property
    def type(self):
        """Return the connection type.

        :return: the connection type
        :rtype: str
        """
        return self._type

    def handle_request(self, request, handler):
        return handler(getattr(self, request.method)(**request.kwargs))

    def head(self, endpoint, params=None, headers=None, **_):
        """Execute a **HEAD** API method.

        :param endpoint: the API endpoint
        :type endpoint: str
        :param params: the request parameters
        :type params: dict
        :param headers: the request headers
        :type headers: dict
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        res = self._http.head(
            url=self._url_prefix + endpoint,
            params=params,
            headers=headers,
            auth=(self._username, self._password)
        )
        if self._logging:
            logger.debug('HEAD {} {}'.format(endpoint, res.status_code))
        return res

    def get(self, endpoint, params=None, headers=None, **_):
        """Execute a **GET** API method.

        :param endpoint: the API endpoint
        :type endpoint: str
        :param params: the request parameters
        :type params: dict
        :param headers: the request headers
        :type headers: dict
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        res = self._http.get(
            url=self._url_prefix + endpoint,
            params=params,
            headers=headers,
            auth=(self._username, self._password)
        )
        if self._logging:
            logger.debug('GET {} {}'.format(endpoint, res.status_code))
        return res

    def put(self, endpoint, data=None, params=None, headers=None, **_):
        """Execute a **PUT** API method.

        :param endpoint: the API endpoint
        :type endpoint: str
        :param data: the request payload
        :type data: str | dict
        :param params: the request parameters
        :type params: dict
        :param headers: the request headers
        :type headers: dict
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        res = self._http.put(
            url=self._url_prefix + endpoint,
            data=sanitize(data),
            params=params,
            headers=headers,
            auth=(self._username, self._password)
        )
        if self._logging:
            logger.debug('PUT {} {}'.format(endpoint, res.status_code))
        return res

    def post(self, endpoint, data=None, params=None, headers=None, **_):
        """Execute a **POST** API method.

        :param endpoint: the API endpoint
        :type endpoint: str
        :param data: the request payload
        :type data: str | dict
        :param params: the request parameters
        :type params: dict
        :param headers: the request headers
        :type headers: dict
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        res = self._http.post(
            url=self._url_prefix + endpoint,
            data=sanitize(data),
            params=params,
            headers=headers,
            auth=(self._username, self._password)
        )
        if self._logging:
            logger.debug('POST {} {}'.format(endpoint, res.status_code))
        return res

    def patch(self, endpoint, data=None, params=None, headers=None, **_):
        """Execute a **PATCH** API method.

        :param endpoint: the API endpoint
        :type endpoint: str
        :param data: the request payload
        :type data: str | dict
        :param params: the request parameters
        :type params: dict
        :param headers: the request headers
        :type headers: dict
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        res = self._http.patch(
            url=self._url_prefix + endpoint,
            data=sanitize(data),
            params=params,
            headers=headers,
            auth=(self._username, self._password)
        )
        if self._logging:
            logger.debug('PATCH {} {}'.format(endpoint, res.status_code))
        return res

    def delete(self, endpoint, data=None, params=None, headers=None, **_):
        """Execute a **DELETE** API method.

        :param endpoint: the API endpoint
        :type endpoint: str
        :param data: the request payload
        :type data: str | dict
        :param params: the request parameters
        :type params: dict
        :param headers: the request headers
        :type headers: dict
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        res = self._http.delete(
            url=self._url_prefix + endpoint,
            data=sanitize(data),
            params=params,
            headers=headers,
            auth=(self._username, self._password)
        )
        if self._logging:
            logger.debug('DELETE {} {}'.format(endpoint, res.status_code))
        return res
