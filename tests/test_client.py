import json
import pickle
from typing import Union

import importlib_metadata
import pytest
from requests import Session

from arango.client import ArangoClient
from arango.database import StandardDatabase
from arango.exceptions import ArangoClientError, ServerConnectionError
from arango.http import DefaultHTTPClient, DeflateRequestCompression
from arango.resolver import FallbackHostResolver, RandomHostResolver, SingleHostResolver
from tests.helpers import (
    generate_col_name,
    generate_db_name,
    generate_string,
    generate_username,
)


def test_client_attributes(url):
    http_client = DefaultHTTPClient()

    client = ArangoClient(hosts=url, http_client=http_client)
    assert client.version == importlib_metadata.version("python-arango")
    assert client.hosts == [url]

    assert repr(client) == f"<ArangoClient {url}>"
    assert isinstance(client._host_resolver, SingleHostResolver)

    client_repr = f"<ArangoClient {url},{url}>"  # noqa: E231
    client_hosts = [url, url]

    client = ArangoClient(
        hosts=f"{url},{url}",  # noqa: E231
        http_client=http_client,
        serializer=json.dumps,
        deserializer=json.loads,
    )
    assert client.version == importlib_metadata.version("python-arango")
    assert client.hosts == client_hosts
    assert repr(client) == client_repr
    assert isinstance(client._host_resolver, FallbackHostResolver)

    client = ArangoClient(
        hosts=client_hosts,
        host_resolver="random",
        http_client=http_client,
        serializer=json.dumps,
        deserializer=json.loads,
    )
    assert client.version == importlib_metadata.version("python-arango")
    assert client.hosts == client_hosts
    assert repr(client) == client_repr
    assert isinstance(client._host_resolver, RandomHostResolver)

    client = ArangoClient(hosts=client_hosts, request_timeout=120)
    assert client.request_timeout == client._http.request_timeout == 120


def test_client_good_connection(db, username, password, url):
    client = ArangoClient(hosts=url)

    # Test connection with verify flag on and off
    for verify in (True, False):
        db = client.db(db.name, username, password, verify=verify)
        assert isinstance(db, StandardDatabase)
        assert db.name == db.name
        assert db.username == username
        assert db.context == "default"


def test_client_bad_connection(db, username, password, cluster, url):
    client = ArangoClient(hosts=url)

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
    with pytest.raises(ArangoClientError) as err:
        client.db(db.name, username, password, verify=True)
    assert "bad connection" in str(err.value)


def test_client_http_client_attributes(db, username, password, url):
    http_client = DefaultHTTPClient(
        request_timeout=80,
        retry_attempts=5,
        backoff_factor=1.0,
        pool_connections=16,
        pool_maxsize=12,
        pool_timeout=120,
    )
    client = ArangoClient(hosts=url, http_client=http_client, request_timeout=30)
    client.db(db.name, username, password, verify=True)
    assert http_client.request_timeout == 80
    assert client.request_timeout == http_client.request_timeout


def test_client_custom_http_client(db, username, password, url):
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
    client = ArangoClient(hosts=url, http_client=http_client)
    # Set verify to True to send a test API call on initialization.
    client.db(db.name, username, password, verify=True)
    assert http_client.counter == 1


def test_client_override_validate(url) -> None:
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
            hosts=url,
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


def test_can_serialize_deserialize_client(url) -> None:
    client = ArangoClient(hosts=url)
    client_pstr = pickle.dumps(client)
    client2 = pickle.loads(client_pstr)
    assert len(client2._sessions) > 0


def test_client_compression(db, username, password, url):
    class CheckCompression:
        def __init__(self, should_compress: bool):
            self.should_compress = should_compress

        def check(self, headers):
            if self.should_compress:
                assert headers["content-encoding"] == "deflate"
            else:
                assert "content-encoding" not in headers

    class MyHTTPClient(DefaultHTTPClient):
        def __init__(self, compression_checker: CheckCompression) -> None:
            super().__init__()
            self.checker = compression_checker

        def send_request(
            self, session, method, url, headers=None, params=None, data=None, auth=None
        ):
            self.checker.check(headers)
            return super().send_request(
                session, method, url, headers, params, data, auth
            )

    checker = CheckCompression(should_compress=False)

    # should not compress, as threshold is 0
    client = ArangoClient(
        hosts=url,
        http_client=MyHTTPClient(compression_checker=checker),
        response_compression="gzip",
    )
    db = client.db(db.name, username, password)
    col = db.create_collection(generate_col_name())
    col.insert({"_key": "1"})

    # should not compress, as size of payload is less than threshold
    checker = CheckCompression(should_compress=False)
    client = ArangoClient(
        hosts=url,
        http_client=MyHTTPClient(compression_checker=checker),
        request_compression=DeflateRequestCompression(250, level=7),
        response_compression="deflate",
    )
    db = client.db(db.name, username, password)
    col = db.create_collection(generate_col_name())
    col.insert({"_key": "2"})

    # should compress
    checker.should_compress = True
    col.insert({"_key": "3" * 250})
