import sys

from arango.http_clients.default import DefaultHTTPClient

if sys.version_info >= (3, 5):
    from arango.http_clients.aio import AsyncioHTTPClient
