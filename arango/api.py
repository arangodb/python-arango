"""ArangoDB Request Client."""

import json

from arango.constants import DEFAULT_DATABASE
from arango.clients import DefaultArangoClient
from arango.utils import is_string


class API(object):
    """A simple wrapper for making REST API calls to ArangoDB.

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
    :type client: arango.clients.base.BaseArangoClient or None
    """

    def __init__(self, protocol="http", host="localhost", port=8529,
                 username="root", password="", database=None, client=None):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = DEFAULT_DATABASE if database is None else database
        self.url_prefix = "{protocol}://{host}:{port}/_db/{database}".format(
            protocol=self.protocol,
            host=self.host,
            port=self.port,
            database=self.database,
        )
        if client is not None:
            self.client = client
        else:
            client_init_data = {"auth": (self.username, self.password)}
            self.client = DefaultArangoClient(client_init_data)

    def head(self, path, params=None, headers=None):
        """Call a HEAD method in ArangoDB's REST API.

        :param path: the API path (e.g. '/_api/version')
        :type path: str
        :param params: the request parameters
        :type params: dict or None
        :param headers: the request headers
        :type headers: dict or None
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        return self.client.head(
            url=self.url_prefix + path,
            params=params,
            headers=headers,
            auth=(self.username, self.password)
        )

    def get(self, path, params=None, headers=None):
        """Call a GET method in ArangoDB's REST API.

        :param path: the API path (e.g. '/_api/version')
        :type path: str
        :param params: the request parameters
        :type params: dict or None
        :param headers: the request headers
        :type headers: dict or None
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        return self.client.get(
            url=self.url_prefix + path,
            params=params,
            headers=headers,
            auth=(self.username, self.password),
        )

    def put(self, path, data=None, params=None, headers=None):
        """Call a PUT method in ArangoDB's REST API.

        :param path: the API path (e.g. '/_api/version')
        :type path: str
        :param data: the request payload
        :type data: str or dict or None
        :param params: the request parameters
        :type params: dict or None
        :param headers: the request headers
        :type headers: dict or None
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        return self.client.put(
            url=self.url_prefix + path,
            data=data if is_string(data) else json.dumps(data),
            params=params,
            headers=headers,
            auth=(self.username, self.password)
        )

    def post(self, path, data=None, params=None, headers=None):
        """Call a POST method in ArangoDB's REST API.

        :param path: the API path (e.g. '/_api/version')
        :type path: str
        :param data: the request payload
        :type data: str or dict or None
        :param params: the request parameters
        :type params: dict or None
        :param headers: the request headers
        :type headers: dict or None
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        return self.client.post(
            url=self.url_prefix + path,
            data=data if is_string(data) else json.dumps(data),
            params=params,
            headers=headers,
            auth=(self.username, self.password)
        )

    def patch(self, path, data=None, params=None, headers=None):
        """Call a PATCH method in ArangoDB's REST API.

        :param path: the API path (e.g. '/_api/version')
        :type path: str
        :param data: the request payload
        :type data: str or dict or None
        :param params: the request parameters
        :type params: dict or None
        :param headers: the request headers
        :type headers: dict or None
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        return self.client.patch(
            url=self.url_prefix + path,
            data=data if is_string(data) else json.dumps(data),
            params=params,
            headers=headers,
            auth=(self.username, self.password)
        )

    def delete(self, path, params=None, headers=None):
        """Call a DELETE method in ArangoDB's REST API.

        :param path: the API path (e.g. '/_api/version')
        :type path: str
        :param params: the request parameters
        :type params: dict or None
        :param headers: the request headers
        :type headers: dict or None
        :returns: the ArangoDB http response
        :rtype: arango.response.Response
        """
        return self.client.delete(
            url=self.url_prefix + path,
            params=params,
            headers=headers,
            auth=(self.username, self.password)
        )
