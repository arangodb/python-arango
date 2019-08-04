from __future__ import absolute_import, unicode_literals

import json

import pytest

from arango.client import ArangoClient
from arango.database import StandardDatabase
from arango.exceptions import ServerConnectionError
from arango.http import DefaultHTTPClient
from arango.resolver import (
    SingleHostResolver,
    RandomHostResolver,
    RoundRobinHostResolver
)
from arango.version import __version__

from tests.helpers import (
    generate_db_name,
    generate_username,
    generate_string
)


def test_client_attributes():
    http_client = DefaultHTTPClient()

    client = ArangoClient(
        hosts='http://127.0.0.1:8529',
        http_client=http_client
    )
    assert client.version == __version__
    assert client.hosts == ['http://127.0.0.1:8529']

    assert repr(client) == '<ArangoClient http://127.0.0.1:8529>'
    assert isinstance(client._host_resolver, SingleHostResolver)

    client_repr = '<ArangoClient http://127.0.0.1:8529,http://localhost:8529>'
    client_hosts = ['http://127.0.0.1:8529', 'http://localhost:8529']

    client = ArangoClient(
        hosts='http://127.0.0.1:8529,http://localhost'
              ':8529',
        http_client=http_client,
        serializer=json.dumps,
        deserializer=json.loads,
    )
    assert client.version == __version__
    assert client.hosts == client_hosts
    assert repr(client) == client_repr
    assert isinstance(client._host_resolver, RoundRobinHostResolver)

    client = ArangoClient(
        hosts=client_hosts,
        host_resolver='random',
        http_client=http_client,
        serializer=json.dumps,
        deserializer=json.loads,
    )
    assert client.version == __version__
    assert client.hosts == client_hosts
    assert repr(client) == client_repr
    assert isinstance(client._host_resolver, RandomHostResolver)


def test_client_good_connection(db, username, password):
    client = ArangoClient(hosts='http://127.0.0.1:8529')

    # Test connection with verify flag on and off
    for verify in (True, False):
        db = client.db(db.name, username, password, verify=verify)
        assert isinstance(db, StandardDatabase)
        assert db.name == db.name
        assert db.username == username
        assert db.context == 'default'


def test_client_bad_connection(db, username, password, cluster):
    client = ArangoClient(hosts='http://127.0.0.1:8529')

    bad_db_name = generate_db_name()
    bad_username = generate_username()
    bad_password = generate_string()

    if not cluster:
        # Test connection with bad username password
        with pytest.raises(ServerConnectionError):
            client.db(db.name, bad_username, bad_password, verify=True)

    # Test connection with missing database
    with pytest.raises(ServerConnectionError):
        client.db(bad_db_name, bad_username, bad_password, verify=True)

    # Test connection with invalid host URL
    client = ArangoClient(hosts='http://127.0.0.1:8500')
    with pytest.raises(ServerConnectionError) as err:
        client.db(db.name, username, password, verify=True)
    assert 'bad connection' in str(err.value)


def test_client_custom_http_client(db, username, password):

    # Define custom HTTP client which increments the counter on any API call.
    class MyHTTPClient(DefaultHTTPClient):

        def __init__(self):
            super(MyHTTPClient, self).__init__()
            self.counter = 0

        def send_request(self,
                         session,
                         method,
                         url,
                         headers=None,
                         params=None,
                         data=None,
                         auth=None):
            self.counter += 1
            return super(MyHTTPClient, self).send_request(
                session, method, url, headers, params, data, auth
            )

    http_client = MyHTTPClient()
    client = ArangoClient(
        hosts='http://127.0.0.1:8529',
        http_client=http_client
    )
    # Set verify to True to send a test API call on initialization.
    client.db(db.name, username, password, verify=True)
    assert http_client.counter == 1
