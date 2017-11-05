import pytest
from arango.http_clients.aio import AsyncioHTTPClient
from arango.response import FutureResponse


def teardown_module(*_):
    pass


def test_errors():
    with pytest.raises(RuntimeError):
        AsyncioHTTPClient()

    with pytest.raises(RuntimeError):
        FutureResponse(None)

