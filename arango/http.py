__all__ = [
    "HTTPClient",
    "DefaultHTTPClient",
    "DeflateRequestCompression",
    "RequestCompression",
    "DEFAULT_REQUEST_TIMEOUT",
]

import typing
import zlib
from abc import ABC, abstractmethod
from typing import Any, MutableMapping, Optional, Tuple, Union

from requests import Session
from requests.adapters import DEFAULT_POOLBLOCK, DEFAULT_POOLSIZE, HTTPAdapter
from requests_toolbelt import MultipartEncoder
from urllib3.poolmanager import PoolManager
from urllib3.util.retry import Retry

from arango.response import Response
from arango.typings import Headers

DEFAULT_REQUEST_TIMEOUT = 60


class HTTPClient(ABC):  # pragma: no cover
    """Abstract base class for HTTP clients."""

    @abstractmethod
    def create_session(self, host: str) -> Session:
        """Return a new requests session given the host URL.

        This method must be overridden by the user.

        :param host: ArangoDB host URL.
        :type host: str
        :returns: Requests session object.
        :rtype: requests.Session
        """
        raise NotImplementedError

    @abstractmethod
    def send_request(
        self,
        session: Session,
        method: str,
        url: str,
        headers: Optional[Headers] = None,
        params: Optional[MutableMapping[str, str]] = None,
        data: Union[str, bytes, MultipartEncoder, None] = None,
        auth: Optional[Tuple[str, str]] = None,
    ) -> Response:
        """Send an HTTP request.

        This method must be overridden by the user.

        :param session: Requests session object.
        :type session: requests.Session
        :param method: HTTP method in lowercase (e.g. "post").
        :type method: str
        :param url: Request URL.
        :type url: str
        :param headers: Request headers.
        :type headers: dict
        :param params: URL (query) parameters.
        :type params: dict
        :param data: Request payload.
        :type data: str | bytes | MultipartEncoder | None
        :param auth: Username and password.
        :type auth: tuple
        :returns: HTTP response.
        :rtype: arango.response.Response
        """
        raise NotImplementedError


class DefaultHTTPAdapter(HTTPAdapter):
    """Default transport adapter implementation

    :param connection_timeout: Socket timeout in seconds for each individual connection.
    :type connection_timeout: int | float
    :param pool_connections: The number of urllib3 connection pools to cache.
    :type pool_connections: int
    :param pool_maxsize: The maximum number of connections to save in the pool.
    :type pool_maxsize: int
    :param pool_timeout: If set, then the pool will be set to block=True,
        and requests will block for pool_timeout seconds and raise
        EmptyPoolError if no connection is available within the time period.
    :type pool_timeout: int | float | None
    :param kwargs: Additional keyword arguments passed to the HTTPAdapter constructor.
    :type kwargs: Any
    """

    __attrs__ = [
        "max_retries",
        "config",
        "_connection_timeout",
        "_pool_connections",
        "_pool_maxsize",
        "_pool_timeout",
        "_pool_block",
    ]

    def __init__(
        self,
        connection_timeout: Union[int, float, None] = DEFAULT_REQUEST_TIMEOUT,
        pool_connections: int = DEFAULT_POOLSIZE,
        pool_maxsize: int = DEFAULT_POOLSIZE,
        pool_timeout: Union[int, float, None] = None,
        **kwargs: Any,
    ) -> None:
        self._connection_timeout = connection_timeout
        self._pool_timeout = pool_timeout
        super().__init__(
            pool_connections=pool_connections, pool_maxsize=pool_maxsize, **kwargs
        )

    @typing.no_type_check
    def init_poolmanager(
        self, connections, maxsize, block=DEFAULT_POOLBLOCK, **pool_kwargs
    ) -> None:
        kwargs = pool_kwargs
        kwargs.update(
            dict(
                num_pools=connections,
                maxsize=maxsize,
                timeout=self._connection_timeout,
            )
        )
        if self._pool_timeout is not None:
            kwargs["block"] = True
            kwargs["timeout"] = self._pool_timeout
        else:
            kwargs["block"] = False
        self.poolmanager = PoolManager(**kwargs)


class DefaultHTTPClient(HTTPClient):
    """Default HTTP client implementation.

    :param request_timeout: Timeout in seconds for each individual connection.
    :type request_timeout: int | float
    :param retry_attempts: Number of retry attempts.
    :type retry_attempts: int
    :param backoff_factor: Backoff factor for retry attempts.
    :type backoff_factor: float
    :param pool_connections: The number of urllib3 connection pools to cache.
    :type pool_connections: int
    :param pool_maxsize: The maximum number of connections to save in the pool.
    :type pool_maxsize: int
    :param pool_timeout: If set, then the pool will be set to block=True,
        and requests will block for pool_timeout seconds and raise
        EmptyPoolError if no connection is available within the time period.
    :type pool_timeout: int | float | None
    """

    def __init__(
        self,
        request_timeout: Union[int, float, None] = DEFAULT_REQUEST_TIMEOUT,
        retry_attempts: int = 3,
        backoff_factor: float = 1.0,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
        pool_timeout: Union[int, float, None] = None,
    ) -> None:
        self.request_timeout = request_timeout
        self._retry_attempts = retry_attempts
        self._backoff_factor = backoff_factor
        self._pool_connections = pool_connections
        self._pool_maxsize = pool_maxsize
        self._pool_timeout = pool_timeout

    def create_session(self, host: str) -> Session:
        """Create and return a new session/connection.

        :param host: ArangoDB host URL.
        :type host: str
        :returns: requests session object
        :rtype: requests.Session
        """
        retry_strategy = Retry(
            total=self._retry_attempts,
            backoff_factor=self._backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
        http_adapter = DefaultHTTPAdapter(
            connection_timeout=self.request_timeout,
            pool_connections=self._pool_connections,
            pool_maxsize=self._pool_maxsize,
            pool_timeout=self._pool_timeout,
            max_retries=retry_strategy,
        )

        session = Session()
        session.mount("https://", http_adapter)
        session.mount("http://", http_adapter)

        return session

    def send_request(
        self,
        session: Session,
        method: str,
        url: str,
        headers: Optional[Headers] = None,
        params: Optional[MutableMapping[str, str]] = None,
        data: Union[str, bytes, MultipartEncoder, None] = None,
        auth: Optional[Tuple[str, str]] = None,
    ) -> Response:
        """Send an HTTP request.

        :param session: Requests session object.
        :type session: requests.Session
        :param method: HTTP method in lowercase (e.g. "post").
        :type method: str
        :param url: Request URL.
        :type url: str
        :param headers: Request headers.
        :type headers: dict
        :param params: URL (query) parameters.
        :type params: dict
        :param data: Request payload.
        :type data: str | bytes | MultipartEncoder | None
        :param auth: Username and password.
        :type auth: tuple
        :returns: HTTP response.
        :rtype: arango.response.Response
        """
        response = session.request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            auth=auth,
            timeout=self.request_timeout,
        )
        return Response(
            method=method,
            url=response.url,
            headers=response.headers,
            status_code=response.status_code,
            status_text=response.reason,
            raw_body=response.text,
        )


class RequestCompression(ABC):  # pragma: no cover
    """Abstract base class for request compression."""

    @abstractmethod
    def needs_compression(self, data: str) -> bool:
        """
        :param data: Data to be compressed.
        :type data: str
        :returns: True if the data needs to be compressed.
        :rtype: bool
        """
        raise NotImplementedError

    @abstractmethod
    def compress(self, data: str) -> bytes:
        """Compress the data.

        :param data: Data to be compressed.
        :type data: str
        :returns: Compressed data.
        :rtype: bytes
        """
        raise NotImplementedError

    @abstractmethod
    def encoding(self) -> str:
        """Return the content encoding exactly as it should
            appear in the headers.

        :returns: Content encoding.
        :rtype: str
        """
        raise NotImplementedError


class DeflateRequestCompression(RequestCompression):
    """Compress requests using the 'deflate' algorithm."""

    def __init__(self, threshold: int = 1024, level: int = 6):
        """
        :param threshold: Will compress requests to the server if
        the size of the request body (in bytes) is at least the value of this
        option.
        :type threshold: int
        :param level: Compression level, in 0-9 or -1.
        :type level: int
        """
        self._threshold = threshold
        self._level = level

    def needs_compression(self, data: str) -> bool:
        """
        :param data: Data to be compressed.
        :type data: str
        :returns: True if the data needs to be compressed.
        :rtype: bool
        """
        return len(data) >= self._threshold

    def compress(self, data: str) -> bytes:
        """
        :param data: Data to be compressed.
        :type data: str
        :returns: Compressed data.
        :rtype: bytes
        """
        return zlib.compress(data.encode("utf-8"), level=self._level)

    def encoding(self) -> str:
        return "deflate"
