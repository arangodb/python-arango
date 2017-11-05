import pytest


def test_fail_import():
    with pytest.raises(ImportError):
        from arango.http_clients import AsyncioHTTPClient

