__all__ = [
    "BaseConnection",
    "BasicConnection",
    "Connection",
    "JwtConnection",
    "JwtSuperuserConnection",
]

import logging
import sys
import time
from abc import abstractmethod
from typing import Any, Callable, Optional, Sequence, Set, Tuple, Union

import jwt
from jwt.exceptions import ExpiredSignatureError
from requests import ConnectionError, Session
from requests_toolbelt import MultipartEncoder

from arango.exceptions import (
    JWTAuthError,
    JWTExpiredError,
    JWTRefreshError,
    ServerConnectionError,
)
from arango.http import HTTPClient, RequestCompression
from arango.request import Request
from arango.resolver import HostResolver
from arango.response import Response
from arango.typings import Fields, Json

Connection = Union["BasicConnection", "JwtConnection", "JwtSuperuserConnection"]


class BaseConnection:
    """Base connection to a specific ArangoDB database."""

    def __init__(
        self,
        hosts: Fields,
        host_resolver: HostResolver,
        sessions: Sequence[Session],
        db_name: str,
        http_client: HTTPClient,
        serializer: Callable[..., str],
        deserializer: Callable[[str], Any],
        request_compression: Optional[RequestCompression] = None,
        response_compression: Optional[str] = None,
    ) -> None:
        self._url_prefixes = [f"{host}/_db/{db_name}" for host in hosts]
        self._host_resolver = host_resolver
        self._sessions = sessions
        self._db_name = db_name
        self._http = http_client
        self._serializer = serializer
        self._deserializer = deserializer
        self._username: Optional[str] = None
        self._request_compression = request_compression
        self._response_compression = response_compression

    @property
    def db_name(self) -> str:
        """Return the database name.

        :returns: Database name.
        :rtype: str
        """
        return self._db_name

    @property
    def username(self) -> Optional[str]:
        """Return the username.

        :returns: Username.
        :rtype: str
        """
        return self._username

    def serialize(self, obj: Any) -> str:
        """Serialize the given object.

        :param obj: JSON object to serialize.
        :type obj: str | bool | int | float | list | dict | None
        :return: Serialized string.
        :rtype: str
        """
        return self._serializer(obj)

    def deserialize(self, string: str) -> Any:
        """De-serialize the string and return the object.

        :param string: String to de-serialize.
        :type string: str
        :return: De-serialized JSON object.
        :rtype: str | bool | int | float | list | dict | None
        """
        try:
            return self._deserializer(string)
        except (ValueError, TypeError):
            return string

    def prep_response(self, resp: Response, deserialize: bool = True) -> Response:
        """Populate the response with details and return it.

        :param deserialize: Deserialize the response body.
        :type deserialize: bool
        :param resp: HTTP response.
        :type resp: arango.response.Response
        :return: HTTP response.
        :rtype: arango.response.Response
        """
        if deserialize:
            resp.body = self.deserialize(resp.raw_body)
            if isinstance(resp.body, dict):
                resp.error_code = resp.body.get("errorNum")
                resp.error_message = resp.body.get("errorMessage")
                if resp.status_code == resp.error_code == 503:
                    raise ConnectionError  # Fallback to another host
        else:
            resp.body = resp.raw_body

        http_ok = 200 <= resp.status_code < 300
        resp.is_success = http_ok and resp.error_code is None
        return resp

    def process_request(
        self, host_index: int, request: Request, auth: Optional[Tuple[str, str]] = None
    ) -> Response:
        """Execute a request until a valid response has been returned.

        :param host_index: The index of the first host to try
        :type host_index: int
        :param request: HTTP request.
        :type request: arango.request.Request
        :return: HTTP response.
        :rtype: arango.response.Response
        """
        tries = 0
        indexes_to_filter: Set[int] = set()

        data = self.normalize_data(request.data)
        if (
            self._request_compression is not None
            and isinstance(data, str)
            and self._request_compression.needs_compression(data)
        ):
            request.headers["content-encoding"] = self._request_compression.encoding()
            data = self._request_compression.compress(data)

        if self._response_compression is not None:
            request.headers["accept-encoding"] = self._response_compression

        while tries < self._host_resolver.max_tries:
            try:
                resp = self._http.send_request(
                    session=self._sessions[host_index],
                    method=request.method,
                    url=self._url_prefixes[host_index] + request.endpoint,
                    params=request.params,
                    data=data,
                    headers=request.headers,
                    auth=auth,
                )

                return self.prep_response(resp, request.deserialize)
            except ConnectionError:
                url = self._url_prefixes[host_index] + request.endpoint
                logging.debug(f"ConnectionError: {url}")

                if len(indexes_to_filter) == self._host_resolver.host_count - 1:
                    indexes_to_filter.clear()
                indexes_to_filter.add(host_index)

                host_index = self._host_resolver.get_host_index(indexes_to_filter)
                tries += 1

        raise ConnectionAbortedError(
            f"Can't connect to host(s) within limit ({self._host_resolver.max_tries})"
        )

    def prep_bulk_err_response(self, parent_response: Response, body: Json) -> Response:
        """Build and return a bulk error response.

        :param parent_response: Parent response.
        :type parent_response: arango.response.Response
        :param body: Error response body.
        :type body: dict
        :return: Child bulk error response.
        :rtype: arango.response.Response
        """
        resp = Response(
            method=parent_response.method,
            url=parent_response.url,
            headers=parent_response.headers,
            status_code=parent_response.status_code,
            status_text=parent_response.status_text,
            raw_body=self.serialize(body),
        )
        resp.body = body
        resp.error_code = body["errorNum"]
        resp.error_message = body["errorMessage"]
        resp.is_success = False
        return resp

    def normalize_data(self, data: Any) -> Union[str, MultipartEncoder, None]:
        """Normalize request data.

        :param data: Request data.
        :type data: str | MultipartEncoder | None
        :return: Normalized data.
        :rtype: str | MultipartEncoder | None
        """
        if data is None:
            return None
        elif isinstance(data, (str, MultipartEncoder)):
            return data
        else:
            return self.serialize(data)

    def ping(self) -> int:
        """Ping the next host to check if connection is established.

        :return: Response status code.
        :rtype: int
        """
        request = Request(method="get", endpoint="/_api/collection")
        resp = self.send_request(request)
        if resp.status_code in {401, 403}:
            raise ServerConnectionError(
                resp, request, "bad username/password or token is expired"
            )
        if not resp.is_success:  # pragma: no cover
            raise ServerConnectionError(
                resp, request, resp.error_message or "bad server response"
            )
        return resp.status_code

    @abstractmethod
    def send_request(self, request: Request) -> Response:  # pragma: no cover
        """Send an HTTP request to ArangoDB server.

        :param request: HTTP request.
        :type request: arango.request.Request
        :return: HTTP response.
        :rtype: arango.response.Response
        """
        raise NotImplementedError


class BasicConnection(BaseConnection):
    """Connection to specific ArangoDB database using basic authentication.

    :param hosts: Host URL or list of URLs (coordinators in a cluster).
    :type hosts: [str]
    :param host_resolver: Host resolver (used for clusters).
    :type host_resolver: arango.resolver.HostResolver
    :param sessions: HTTP session objects per host.
    :type sessions: [requests.Session]
    :param db_name: Database name.
    :type db_name: str
    :param username: Username.
    :type username: str
    :param password: Password.
    :type password: str
    :param http_client: User-defined HTTP client.
    :type http_client: arango.http.HTTPClient
    :param: request_compression: The request compression algorithm.
    :type request_compression: arango.http.RequestCompression | None
    :param: response_compression: The response compression algorithm.
    :type response_compression: str | None
    """

    def __init__(
        self,
        hosts: Fields,
        host_resolver: HostResolver,
        sessions: Sequence[Session],
        db_name: str,
        username: str,
        password: str,
        http_client: HTTPClient,
        serializer: Callable[..., str],
        deserializer: Callable[[str], Any],
        request_compression: Optional[RequestCompression] = None,
        response_compression: Optional[str] = None,
    ) -> None:
        super().__init__(
            hosts,
            host_resolver,
            sessions,
            db_name,
            http_client,
            serializer,
            deserializer,
            request_compression,
            response_compression,
        )
        self._username = username
        self._auth = (username, password)

    def send_request(self, request: Request) -> Response:
        """Send an HTTP request to ArangoDB server.

        :param request: HTTP request.
        :type request: arango.request.Request
        :return: HTTP response.
        :rtype: arango.response.Response
        """
        host_index = self._host_resolver.get_host_index()
        return self.process_request(host_index, request, auth=self._auth)


class JwtConnection(BaseConnection):
    """Connection to specific ArangoDB database using JWT authentication.

    :param hosts: Host URL or list of URLs (coordinators in a cluster).
    :type hosts: [str]
    :param host_resolver: Host resolver (used for clusters).
    :type host_resolver: arango.resolver.HostResolver
    :param sessions: HTTP session objects per host.
    :type sessions: [requests.Session]
    :param db_name: Database name.
    :type db_name: str
    :param username: Username.
    :type username: str
    :param password: Password.
    :type password: str
    :param http_client: User-defined HTTP client.
    :type http_client: arango.http.HTTPClient
    :param request_compression: The request compression algorithm.
    :type request_compression: arango.http.RequestCompression | None
    :param response_compression: The response compression algorithm.
    :type response_compression: str | None
    """

    def __init__(
        self,
        hosts: Fields,
        host_resolver: HostResolver,
        sessions: Sequence[Session],
        db_name: str,
        http_client: HTTPClient,
        serializer: Callable[..., str],
        deserializer: Callable[[str], Any],
        username: Optional[str] = None,
        password: Optional[str] = None,
        user_token: Optional[str] = None,
        request_compression: Optional[RequestCompression] = None,
        response_compression: Optional[str] = None,
    ) -> None:
        super().__init__(
            hosts,
            host_resolver,
            sessions,
            db_name,
            http_client,
            serializer,
            deserializer,
            request_compression,
            response_compression,
        )
        self._username = username
        self._password = password

        self.exp_leeway: int = 0
        self._auth_header: Optional[str] = None
        self._token: Optional[str] = None
        self._token_exp: int = sys.maxsize

        if user_token is not None:
            self.set_token(user_token)
        elif username is not None and password is not None:
            self.refresh_token()
        else:
            m = "Either **user_token** or **username** & **password** must be set"
            raise ValueError(m)

    def send_request(self, request: Request) -> Response:
        """Send an HTTP request to ArangoDB server.

        :param request: HTTP request.
        :type request: arango.request.Request
        :return: HTTP response.
        :rtype: arango.response.Response
        """
        host_index = self._host_resolver.get_host_index()

        if self._auth_header is not None:
            request.headers["Authorization"] = self._auth_header

        resp = self.process_request(host_index, request)

        # Refresh the token and retry on HTTP 401 and error code 11.
        if resp.error_code != 11 or resp.status_code != 401:
            return resp

        now = int(time.time())
        if self._token_exp < now - self.exp_leeway:  # pragma: no cover
            return resp

        self.refresh_token()

        if self._auth_header is not None:
            request.headers["Authorization"] = self._auth_header

        return self.process_request(host_index, request)

    def refresh_token(self) -> None:
        """Get a new JWT token for the current user (cannot be a superuser).

        :return: JWT token.
        :rtype: str
        :raise arango.exceptions.JWTRefreshError: If missing username & password.
        :raise arango.exceptions.JWTAuthError: If token retrieval fails.
        """
        if self._username is None or self._password is None:
            raise JWTRefreshError("username and password must be set")

        request = Request(
            method="post",
            endpoint="/_open/auth",
            data={"username": self._username, "password": self._password},
        )

        host_index = self._host_resolver.get_host_index()

        resp = self.process_request(host_index, request)

        if not resp.is_success:
            raise JWTAuthError(resp, request)

        self.set_token(resp.body["jwt"])

    def set_token(self, token: str) -> None:
        """Set the JWT token.

        :param token: JWT token.
        :type token: str
        :raise arango.exceptions.JWTExpiredError: If the token is expired.
        """
        assert token is not None

        try:
            jwt_payload = jwt.decode(
                token,
                issuer="arangodb",
                algorithms=["HS256"],
                options={
                    "require_exp": True,
                    "require_iat": True,
                    "verify_iat": True,
                    "verify_exp": True,
                    "verify_signature": False,
                },
            )
        except ExpiredSignatureError:
            raise JWTExpiredError("JWT token is expired")

        self._token = token
        self._token_exp = jwt_payload["exp"]
        self._auth_header = f"bearer {self._token}"


class JwtSuperuserConnection(BaseConnection):
    """Connection to specific ArangoDB database using superuser JWT.

    :param hosts: Host URL or list of URLs (coordinators in a cluster).
    :type hosts: [str]
    :param host_resolver: Host resolver (used for clusters).
    :type host_resolver: arango.resolver.HostResolver
    :param sessions: HTTP session objects per host.
    :type sessions: [requests.Session]
    :param db_name: Database name.
    :type db_name: str
    :param http_client: User-defined HTTP client.
    :type http_client: arango.http.HTTPClient
    :param superuser_token: User generated token for superuser access.
    :type superuser_token: str
    :param request_compression: The request compression algorithm.
    :type request_compression: arango.http.RequestCompression | None
    :param response_compression: The response compression algorithm.
    :type response_compression: str | None
    """

    def __init__(
        self,
        hosts: Fields,
        host_resolver: HostResolver,
        sessions: Sequence[Session],
        db_name: str,
        http_client: HTTPClient,
        serializer: Callable[..., str],
        deserializer: Callable[[str], Any],
        superuser_token: str,
        request_compression: Optional[RequestCompression] = None,
        response_compression: Optional[str] = None,
    ) -> None:
        super().__init__(
            hosts,
            host_resolver,
            sessions,
            db_name,
            http_client,
            serializer,
            deserializer,
            request_compression,
            response_compression,
        )
        self._auth_header = f"bearer {superuser_token}"

    def send_request(self, request: Request) -> Response:
        """Send an HTTP request to ArangoDB server.

        :param request: HTTP request.
        :type request: arango.request.Request
        :return: HTTP response.
        :rtype: arango.response.Response
        """
        host_index = self._host_resolver.get_host_index()
        request.headers["Authorization"] = self._auth_header

        return self.process_request(host_index, request)

    def set_token(self, token: str) -> None:
        """Set the JWT token.

        :param token: JWT token.
        :type token: str
        :raise arango.exceptions.JWTExpiredError: If the token is expired.
        """
        assert token is not None

        try:
            jwt.decode(
                token,
                issuer="arangodb",
                algorithms=["HS256"],
                options={
                    "require_exp": True,
                    "require_iat": True,
                    "verify_iat": True,
                    "verify_exp": True,
                    "verify_signature": False,
                },
            )
        except ExpiredSignatureError:
            raise JWTExpiredError("JWT token is expired")

        self._auth_header = f"bearer {token}"
