import json
from typing import Union

import pytest
from pkg_resources import get_distribution
from requests import Session

from arango.client import ArangoClient
from arango.database import StandardDatabase
from arango.exceptions import ServerConnectionError
from arango.http import DefaultHTTPClient
from arango.resolver import (
    RandomHostResolver,
    RoundRobinHostResolver,
    SingleHostResolver,
)
from tests.helpers import generate_db_name, generate_string, generate_username


def test_client_attributes():
    http_client = DefaultHTTPClient()

    client = ArangoClient(hosts="http://127.0.0.1:8529", http_client=http_client)
    assert client.version == get_distribution("python-arango").version
    assert client.hosts == ["http://127.0.0.1:8529"]

    assert repr(client) == "<ArangoClient http://127.0.0.1:8529>"
    assert isinstance(client._host_resolver, SingleHostResolver)

    client_repr = "<ArangoClient http://127.0.0.1:8529,http://localhost:8529>"
    client_hosts = ["http://127.0.0.1:8529", "http://localhost:8529"]

    client = ArangoClient(
        hosts="http://127.0.0.1:8529,http://localhost" ":8529",
        http_client=http_client,
        serializer=json.dumps,
        deserializer=json.loads,
    )
    assert client.version == get_distribution("python-arango").version
    assert client.hosts == client_hosts
    assert repr(client) == client_repr
    assert isinstance(client._host_resolver, RoundRobinHostResolver)

    client = ArangoClient(
        hosts=client_hosts,
        host_resolver="random",
        http_client=http_client,
        serializer=json.dumps,
        deserializer=json.loads,
    )
    assert client.version == get_distribution("python-arango").version
    assert client.hosts == client_hosts
    assert repr(client) == client_repr
    assert isinstance(client._host_resolver, RandomHostResolver)

    client = ArangoClient(hosts=client_hosts, request_timeout=120)
    assert client.request_timeout == client._http.REQUEST_TIMEOUT == 120


def test_client_good_connection(db, username, password):
    client = ArangoClient(hosts="http://127.0.0.1:8529")

    # Test connection with verify flag on and off
    for verify in (True, False):
        db = client.db(db.name, username, password, verify=verify)
        assert isinstance(db, StandardDatabase)
        assert db.name == db.name
        assert db.username == username
        assert db.context == "default"


def test_client_bad_connection(db, username, password, cluster):
    client = ArangoClient(hosts="http://127.0.0.1:8529")

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
    client = ArangoClient(hosts="http://127.0.0.1:8500")
    with pytest.raises(ServerConnectionError) as err:
        client.db(db.name, username, password, verify=True)
    assert "bad connection" in str(err.value)


def test_client_custom_http_client(db, username, password):

    # Define custom HTTP client which increments the counter on any API call.
    class MyHTTPClient(DefaultHTTPClient):
        def __init__(self) -> None:
            super().__init__()
            self.counter = 0

        def send_request(
            self, session, method, url, headers=None, params=None, data=None, auth=None
        ):
            self.counter += 1
            return super().send_request(
                session, method, url, headers, params, data, auth
            )

    http_client = MyHTTPClient()
    client = ArangoClient(hosts="http://127.0.0.1:8529", http_client=http_client)
    # Set verify to True to send a test API call on initialization.
    client.db(db.name, username, password, verify=True)
    assert http_client.counter == 1


def test_client_override_validate() -> None:
    # custom http client that manipulates the underlying session
    class MyHTTPClient(DefaultHTTPClient):
        def __init__(self, verify: Union[None, bool, str]) -> None:
            super().__init__()
            self.verify = verify

        def create_session(self, host: str) -> Session:
            session = super().create_session(host)
            session.verify = self.verify
            return session

    def assert_verify(
        http_client_verify: Union[None, str, bool],
        arango_override: Union[None, str, bool],
        expected_result: Union[None, str, bool],
    ) -> None:
        http_client = MyHTTPClient(verify=http_client_verify)
        client = ArangoClient(
            hosts="http://127.0.0.1:8529",
            http_client=http_client,
            verify_override=arango_override,
        )
        # make sure there is at least 1 session
        assert len(client._sessions) > 0
        for session in client._sessions:
            # make sure the final session.verify has expected value
            assert session.verify == expected_result

    assert_verify(None, None, None)
    assert_verify(None, True, True)
    assert_verify(None, False, False)
    assert_verify(None, "test", "test")

    assert_verify(True, None, True)
    assert_verify(True, True, True)
    assert_verify(True, "test", "test")
    assert_verify(True, False, False)

    assert_verify(False, None, False)
    assert_verify(False, True, True)
    assert_verify(False, "test", "test")
    assert_verify(False, False, False)

    assert_verify("test", None, "test")
    assert_verify("test", True, True)
    assert_verify("test", False, False)
    assert_verify("test", False, False)
    assert_verify("test", "foo", "foo")
