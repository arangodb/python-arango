from __future__ import absolute_import, unicode_literals

import json

from six import string_types

__all__ = ['ArangoClient']

from arango.connection import Connection
from arango.database import StandardDatabase
from arango.exceptions import ServerConnectionError
from arango.http import DefaultHTTPClient
from arango.resolver import (
    SingleHostResolver,
    RandomHostResolver,
    RoundRobinHostResolver
)
from arango.version import __version__


class ArangoClient(object):
    """ArangoDB client.

    :param hosts: Host URL or list of URLs (coordinators in a cluster).
    :type hosts: [str | unicode]
    :param host_resolver: Host resolver. This parameter used for clusters (when
        multiple host URLs are provided). Accepted values are "roundrobin" and
        "random". Any other value defaults to round robin.
    :type host_resolver: str | unicode
    :param http_client: User-defined HTTP client.
    :type http_client: arango.http.HTTPClient
    :param serializer: User-defined JSON serializer. Must be a callable
        which takes a JSON data type object as its only argument and return
        the serialized string. If not given, ``json.dumps`` is used by default.
    :type serializer: callable
    :param deserializer: User-defined JSON de-serializer. Must be a callable
        which takes a JSON serialized string as its only argument and return
        the de-serialized object. If not given, ``json.loads`` is used by
        default.
    :type deserializer: callable
    """

    def __init__(self,
                 hosts='http://127.0.0.1:8529',
                 host_resolver='roundrobin',
                 http_client=None,
                 serializer=json.dumps,
                 deserializer=json.loads):
        if isinstance(hosts, string_types):
            self._hosts = [host.strip('/') for host in hosts.split(',')]
        else:
            self._hosts = [host.strip('/') for host in hosts]

        host_count = len(self._hosts)
        if host_count == 1:
            self._host_resolver = SingleHostResolver()
        elif host_resolver == 'random':
            self._host_resolver = RandomHostResolver(host_count)
        else:
            self._host_resolver = RoundRobinHostResolver(host_count)

        self._http = http_client or DefaultHTTPClient()
        self._serializer = serializer
        self._deserializer = deserializer
        self._sessions = [self._http.create_session(h) for h in self._hosts]

    def __repr__(self):
        return '<ArangoClient {}>'.format(','.join(self._hosts))

    @property
    def hosts(self):
        """Return the list of ArangoDB host URLs.

        :return: List of ArangoDB host URLs.
        :rtype: [str | unicode]
        """
        return self._hosts

    @property
    def version(self):
        """Return the client version.

        :return: Client version.
        :rtype: str | unicode
        """
        return __version__

    def db(self, name='_system', username='root', password='', verify=False):
        """Connect to an ArangoDB database and return the database API wrapper.

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
            to True and the connection fails.
        """
        connection = Connection(
            hosts=self._hosts,
            host_resolver=self._host_resolver,
            sessions=self._sessions,
            db_name=name,
            username=username,
            password=password,
            http_client=self._http,
            serializer=self._serializer,
            deserializer=self._deserializer
        )
        if verify:
            try:
                connection.ping()
            except ServerConnectionError as err:
                raise err
            except Exception as err:
                raise ServerConnectionError('bad connection: {}'.format(err))

        return StandardDatabase(connection)
