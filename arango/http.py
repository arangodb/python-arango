__all__ = ["HTTPClient", "DefaultHTTPClient"]

from abc import ABC, abstractmethod
from typing import MutableMapping, Optional, Tuple, Union

from requests import Session
from requests.adapters import HTTPAdapter
from requests_toolbelt import MultipartEncoder
from urllib3.util.retry import Retry

from arango.response import Response
from arango.typings import Headers


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
        data: Union[str, MultipartEncoder, None] = None,
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
        :type data: str | MultipartEncoder | None
        :param auth: Username and password.
        :type auth: tuple
        :returns: HTTP response.
        :rtype: arango.response.Response
        """
        raise NotImplementedError


class DefaultHTTPClient(HTTPClient):
    """Default HTTP client implementation."""

    REQUEST_TIMEOUT = 60
    RETRY_ATTEMPTS = 3
    BACKOFF_FACTOR = 1

    def create_session(self, host: str) -> Session:
        """Create and return a new session/connection.

        :param host: ArangoDB host URL.
        :type host: str
        :returns: requests session object
        :rtype: requests.Session
        """
        retry_strategy = Retry(
            total=self.RETRY_ATTEMPTS,
            backoff_factor=self.BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
        http_adapter = HTTPAdapter(max_retries=retry_strategy)

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
        data: Union[str, MultipartEncoder, None] = None,
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
        :type data: str | MultipartEncoder | None
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
            timeout=self.REQUEST_TIMEOUT,
        )
        return Response(
            method=method,
            url=response.url,
            headers=response.headers,
            status_code=response.status_code,
            status_text=response.reason,
            raw_body=response.text,
        )
