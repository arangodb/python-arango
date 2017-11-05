from __future__ import absolute_import, unicode_literals

import logging

from arango.http_clients import DefaultHTTPClient
from arango.utils import sanitize


class Connection(object):
    """ArangoDB database connection.

    :param protocol: the internet transfer protocol (default: ``"http"``)
    :type protocol: str | unicode
    :param host: ArangoDB host (default: ``"localhost"``)
    :type host: str | unicode
    :param port: ArangoDB port (default: ``8529``)
    :type port: int | str | unicode
    :param database: the name of the target database (default: ``"_system"``)
    :type database: str | unicode
    :param username: ArangoDB username (default: ``"root"``)
    :type username: str | unicode
    :param password: ArangoDB password (default: ``""``)
    :type password: str | unicode
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
                 enable_logging=True,
                 logger=None):

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
        self._enable_logging = enable_logging
        self._type = 'standard'
        self._logger = logger or logging.getLogger('arango')

    def __repr__(self):
        return '<ArangoDB connection to database "{}">'.format(self._database)

    @property
    def protocol(self):
        """Return the internet transfer protocol.

        :returns: the internet transfer protocol
        :rtype: str | unicode
        """
        return self._protocol

    @property
    def host(self):
        """Return the ArangoDB host.

        :returns: the ArangoDB host
        :rtype: str | unicode
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
        :rtype: str | unicode
        """
        return self._username

    @property
    def password(self):
        """Return the ArangoDB user password.

        :returns: the ArangoDB user password
        :rtype: str | unicode
        """
        return self._password

    @property
    def database(self):
        """Return the name of the connected database.

        :returns: the name of the connected database
        :rtype: str | unicode
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
    def logging_enabled(self):
        """Return ``True`` if logging is enabled, ``False`` otherwise.

        :returns: whether logging is enabled or not
        :rtype: bool
        """
        return self._enable_logging

    @property
    def type(self):
        """Return the connection type.

        :return: the connection type
        :rtype: str | unicode
        """
        return self._type

    def handle_request(self, request, handler):
        # from arango.async import AsyncExecution
        # from arango.exceptions import ArangoError
        # async = AsyncExecution(self, return_result=True)
        # response = async.handle_request(request, handler)
        # while response.status() != 'done':
        #     pass
        # result = response.result()
        # if isinstance(result, ArangoError):
        #     raise result
        # return result

        # from arango.batch import BatchExecution
        # from arango.exceptions import ArangoError
        #
        # batch = BatchExecution(self, return_result=True)
        # response = batch.handle_request(request, handler)
        # batch.commit()
        # result = response.result()
        # if isinstance(result, ArangoError):
        #     raise result
        # return result
        return handler(getattr(self, request.method)(**request.kwargs))

    def head(self, endpoint, params=None, headers=None, **_):
        """Execute a **HEAD** API method.

        :param endpoint: the API endpoint
        :type endpoint: str | unicode
        :param params: the request parameters
        :type params: dict
        :param headers: the request headers
        :type headers: dict
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        url = self._url_prefix + endpoint
        res = self._http.head(
            url=url,
            params=params,
            headers=headers,
            auth=(self._username, self._password)
        )
        if self._enable_logging:
            self._logger.debug('HEAD {} {}'.format(url, res.status_code))
        return res

    def get(self, endpoint, params=None, headers=None, **_):
        """Execute a **GET** API method.

        :param endpoint: the API endpoint
        :type endpoint: str | unicode
        :param params: the request parameters
        :type params: dict
        :param headers: the request headers
        :type headers: dict
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        url = self._url_prefix + endpoint
        res = self._http.get(
            url=url,
            params=params,
            headers=headers,
            auth=(self._username, self._password)
        )
        if self._enable_logging:
            self._logger.debug('GET {} {}'.format(url, res.status_code))
        return res

    def put(self, endpoint, data=None, params=None, headers=None, **_):
        """Execute a **PUT** API method.

        :param endpoint: the API endpoint
        :type endpoint: str | unicode
        :param data: the request payload
        :type data: str | unicode | dict
        :param params: the request parameters
        :type params: dict
        :param headers: the request headers
        :type headers: dict
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        url = self._url_prefix + endpoint
        res = self._http.put(
            url=url,
            data=sanitize(data),
            params=params,
            headers=headers,
            auth=(self._username, self._password)
        )
        if self._enable_logging:
            self._logger.debug('PUT {} {}'.format(url, res.status_code))
        return res

    def post(self, endpoint, data=None, params=None, headers=None, **_):
        """Execute a **POST** API method.

        :param endpoint: the API endpoint
        :type endpoint: str | unicode
        :param data: the request payload
        :type data: str | unicode | dict
        :param params: the request parameters
        :type params: dict
        :param headers: the request headers
        :type headers: dict
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        url = self._url_prefix + endpoint
        res = self._http.post(
            url=url,
            data=sanitize(data),
            params=params,
            headers=headers,
            auth=(self._username, self._password)
        )
        if self._enable_logging:
            self._logger.debug('POST {} {}'.format(url, res.status_code))
        return res

    def patch(self, endpoint, data=None, params=None, headers=None, **_):
        """Execute a **PATCH** API method.

        :param endpoint: the API endpoint
        :type endpoint: str | unicode
        :param data: the request payload
        :type data: str | unicode | dict
        :param params: the request parameters
        :type params: dict
        :param headers: the request headers
        :type headers: dict
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        url = self._url_prefix + endpoint
        res = self._http.patch(
            url=url,
            data=sanitize(data),
            params=params,
            headers=headers,
            auth=(self._username, self._password)
        )
        if self._enable_logging:
            self._logger.debug('PATCH {} {}'.format(url, res.status_code))
        return res

    def delete(self, endpoint, data=None, params=None, headers=None, **_):
        """Execute a **DELETE** API method.

        :param endpoint: the API endpoint
        :type endpoint: str | unicode
        :param data: the request payload
        :type data: str | unicode | dict
        :param params: the request parameters
        :type params: dict
        :param headers: the request headers
        :type headers: dict
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        url = self._url_prefix + endpoint
        res = self._http.delete(
            url=url,
            data=sanitize(data),
            params=params,
            headers=headers,
            auth=(self._username, self._password)
        )
        if self._enable_logging:
            self._logger.debug('DELETE {} {}'.format(url, res.status_code))
        return res
