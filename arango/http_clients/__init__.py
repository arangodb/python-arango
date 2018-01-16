import sys

from arango.http_clients.base import BaseHTTPClient  # noqa: F401
from arango.http_clients.default import DefaultHTTPClient  # noqa: F401

if sys.version_info >= (3, 5):
    from arango.http_clients.asyncio import AsyncioHTTPClient  # noqa: F401
