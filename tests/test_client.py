from __future__ import absolute_import, unicode_literals

import pytest

from arango.client import ArangoClient
from arango.database import StandardDatabase
from arango.exceptions import ServerConnectionError
from arango.http import DefaultHTTPClient
from arango.version import __version__
from tests.helpers import (
    generate_db_name,
    generate_username,
    generate_string
)


def test_client_attributes():
    session = DefaultHTTPClient()
    client = ArangoClient(
        protocol='http',
        host='127.0.0.1',
        port=8529,
        http_client=session
    )
    assert client.version == __version__
    assert client.protocol == 'http'
    assert client.host == '127.0.0.1'
    assert client.port == 8529
    assert client.base_url == 'http://127.0.0.1:8529'
    assert repr(client) == '<ArangoClient http://127.0.0.1:8529>'


def test_client_good_connection(db, username, password):
    client = ArangoClient(
        protocol='http',
        host='127.0.0.1',
        port=8529,
    )

    # Test connection with verify flag on and off
    for verify in (True, False):
        db = client.db(db.name, username, password, verify=verify)
        assert isinstance(db, StandardDatabase)
        assert db.name == db.name
        assert db.username == username
        assert db.context == 'default'


def test_client_bad_connection(db, username, password):
    client = ArangoClient(protocol='http', host='127.0.0.1', port=8529)

    bad_db_name = generate_db_name()
    bad_username = generate_username()
    bad_password = generate_string()

    # Test connection with bad username password
    with pytest.raises(ServerConnectionError) as err:
        client.db(db.name, bad_username, bad_password, verify=True)
    assert 'bad username and/or password' in str(err.value)

    # Test connection with missing database
    with pytest.raises(ServerConnectionError) as err:
        client.db(bad_db_name, bad_username, bad_password, verify=True)
    assert 'database not found' in str(err.value)

    # Test connection with invalid host URL
    client._url = 'http://127.0.0.1:8500'
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
                         method,
                         url,
                         headers=None,
                         params=None,
                         data=None,
                         auth=None):
            self.counter += 1
            return super(MyHTTPClient, self).send_request(
                method, url, headers, params, data, auth
            )

    http_client = MyHTTPClient()
    client = ArangoClient(
        protocol='http',
        host='127.0.0.1',
        port=8529,
        http_client=http_client
    )
    # Set verify to True to send a test API call on initialization.
    client.db(db.name, username, password, verify=True)
    assert http_client.counter == 1
