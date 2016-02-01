"""Wrapper for making REST API calls to ArangoDB."""

import json

from arango.constants import DEFAULT_DATABASE
from arango.clients import DefaultHTTPClient
from arango.utils import is_str


class Connection(object):
    """Connection used to make API calls to ArangoDB.

    :param protocol: the internet transfer protocol (default: 'http')
    :type protocol: str
    :param host: ArangoDB host (default: 'localhost')
    :type host: str
    :param port: ArangoDB port (default: 8529)
    :type port: int or str
    :param username: ArangoDB username (default: 'root')
    :type username: str
    :param password: ArangoDB password (default: '')
    :type password: str
    :param database: the ArangoDB database to point the API calls to
    :type database: str
    :param client: HTTP client for this wrapper to use
    :type client: arango.clients.base.BaseHTTPClient or None
    """

    def __init__(self, protocol="http", host="localhost", port=8529,
                 username="root", password="", database=None, client=None):
        self._protocol = protocol
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._database = DEFAULT_DATABASE if database is None else database
        self.url_prefix = "{protocol}://{host}:{port}/_db/{database}".format(
            protocol=self._protocol,
            host=self._host,
            port=self._port,
            database=self._database,
        )
        if client is not None:
            self._client = client
        else:
            client_init_data = {"auth": (self._username, self._password)}
            self._client = DefaultHTTPClient()

    def head(self, endpoint, params=None, headers=None):
        """Call a HEAD method in ArangoDB's REST API.

        :param endpoint: the API path (e.g. '/_api/version')
        :type endpoint: str
        :param params: the request parameters
        :type params: dict or None
        :param headers: the request headers
        :type headers: dict or None
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        return self._client.head(
            url=self.url_prefix + endpoint,
            params=params,
            headers=headers,
            auth=(self._username, self._password)
        )

    def get(self, endpoint, params=None, headers=None):
        """Call a GET method in ArangoDB's REST API.

        :param endpoint: the API path (e.g. '/_api/version')
        :type endpoint: str
        :param params: the request parameters
        :type params: dict or None
        :param headers: the request headers
        :type headers: dict or None
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        return self._client.get(
            url=self.url_prefix + endpoint,
            params=params,
            headers=headers,
            auth=(self._username, self._password),
        )

    def put(self, endpoint, data=None, params=None, headers=None):
        """Call a PUT method in ArangoDB's REST API.

        :param endpoint: the API path (e.g. '/_api/version')
        :type endpoint: str
        :param data: the request payload
        :type data: str or dict or None
        :param params: the request parameters
        :type params: dict or None
        :param headers: the request headers
        :type headers: dict or None
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        return self._client.put(
            url=self.url_prefix + endpoint,
            data=data if is_str(data) else json.dumps(data),
            params=params,
            headers=headers,
            auth=(self._username, self._password)
        )

    def post(self, endpoint, data=None, params=None, headers=None):
        """Call a POST method in ArangoDB's REST API.

        :param endpoint: the API path (e.g. '/_api/version')
        :type endpoint: str
        :param data: the request payload
        :type data: str or dict or None
        :param params: the request parameters
        :type params: dict or None
        :param headers: the request headers
        :type headers: dict or None
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        return self._client.post(
            url=self.url_prefix + endpoint,
            data=data if is_str(data) else json.dumps(data),
            params=params,
            headers=headers,
            auth=(self._username, self._password)
        )

    def patch(self, endpoint, data=None, params=None, headers=None):
        """Call a PATCH method in ArangoDB's REST API.

        :param endpoint: the API path (e.g. '/_api/version')
        :type endpoint: str
        :param data: the request payload
        :type data: str or dict or None
        :param params: the request parameters
        :type params: dict or None
        :param headers: the request headers
        :type headers: dict or None
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        return self._client.patch(
            url=self.url_prefix + endpoint,
            data=data if is_str(data) else json.dumps(data),
            params=params,
            headers=headers,
            auth=(self._username, self._password)
        )

    def delete(self, endpoint, params=None, headers=None):
        """Call a DELETE method in ArangoDB's REST API.

        :param endpoint: the API path (e.g. '/_api/version')
        :type endpoint: str
        :param params: the request parameters
        :type params: dict or None
        :param headers: the request headers
        :type headers: dict or None
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        return self._client.delete(
            url=self.url_prefix + endpoint,
            params=params,
            headers=headers,
            auth=(self._username, self._password)
        )
