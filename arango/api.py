"""ArangoDB Request Client."""

import json

from arango.clients.default import DefaultArangoClient


class ArangoAPI(object):
    """A simple wrapper for making HTTP clients to ArangoDB.

    :param protocol: the internet transfer protocol (default: http)
    :type protocol: str
    :param host: ArangoDB host (default: localhost)
    :type host: str
    :param port: ArangoDB port (default: 8529)
    :type port: int or str
    :param username: username for ArangoDB (default: root)
    :type username: str
    :param password: password for ArangoDB (default: empty string)
    :type password: str
    :param db_name: the database to use (default: _system)
    :type db_name: str
    :param client: HTTP client for the connection to use
    :type client: arango.clients.base.BaseArangoClient
    """

    def __init__(self, protocol="http", host="localhost", port=8529,
                 username="root", password="", db_name="_system", client=None):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.db_name = db_name
        self.client = DefaultArangoClient() if client is None else client

    @property
    def url_prefix(self):
        """Generate and return the URL prefix.

        e.g. http://localhost:8529/_db/_system

        :returns: the URL prefix
        :rtype: str
        """
        return "{protocol}://{host}:{port}/_db/{db}".format(
            protocol = self.protocol,
            host = self.host,
            port = self.port,
            db = self.db_name,
        )

    def head(self, path, params=None, headers=None):
        """Execute an HTTP HEAD method."""
        return self.client.head(
            url=self.url_prefix + path,
            params=params,
            headers=headers,
            auth=(self.username, self.password)
        )

    def get(self, path, params=None, headers=None):
        """Execute an HTTP GET method."""
        return self.client.get(
            url=self.url_prefix + path,
            params=params,
            headers=headers,
            auth=(self.username, self.password),
        )

    def put(self, path, data=None, params=None, headers=None):
        """Execute an HTTP PUT method."""
        return self.client.put(
            url=self.url_prefix + path,
            data=data if isinstance(data, basestring) else json.dumps(data),
            params=params,
            headers=headers,
            auth=(self.username, self.password)
        )

    def post(self, path, data=None, params=None, headers=None):
        """Execute an HTTP POST method."""
        return self.client.post(
            url=self.url_prefix + path,
            data=data if isinstance(data, basestring) else json.dumps(data),
            params=params,
            headers=headers,
            auth=(self.username, self.password)
        )

    def patch(self, path, data=None, params=None, headers=None):
        """Execute an HTTP PATCH method."""
        return self.client.patch(
            url=self.url_prefix + path,
            data=data if isinstance(data, basestring) else json.dumps(data),
            params=params,
            headers=headers,
            auth=(self.username, self.password)
        )

    def delete(self, path, params=None, headers=None):
        """Execute an HTTP DELETE method."""
        return self.client.delete(
            url=self.url_prefix + path,
            params=params,
            headers=headers,
            auth=(self.username, self.password)
        )
