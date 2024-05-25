__all__ = ["ArangoClient"]

from json import dumps, loads
from typing import Any, Callable, Optional, Sequence, Union

import importlib_metadata

from arango.connection import (
    BasicConnection,
    Connection,
    JwtConnection,
    JwtSuperuserConnection,
)
from arango.database import StandardDatabase
from arango.exceptions import ArangoClientError, ServerConnectionError
from arango.http import (
    DEFAULT_REQUEST_TIMEOUT,
    DefaultHTTPClient,
    HTTPClient,
    RequestCompression,
)
from arango.resolver import (
    FallbackHostResolver,
    HostResolver,
    PeriodicHostResolver,
    RandomHostResolver,
    RoundRobinHostResolver,
    SingleHostResolver,
)


def default_serializer(x: Any) -> str:
    """
    Default JSON serializer

    :param x: A JSON data type object to serialize
    :type x: Any
    :return: The object serialized as a JSON string
    :rtype: str
    """
    return dumps(x, separators=(",", ":"))


def default_deserializer(x: str) -> Any:
    """
    Default JSON de-serializer

    :param x: A JSON string to deserialize
    :type x: str
    :return: The de-serialized JSON object
    :rtype: Any
    """
    return loads(x)


class ArangoClient:
    """ArangoDB client.

    :param hosts: Host URL or list of URLs (coordinators in a cluster).
    :type hosts: str | [str]
    :param host_resolver: Host resolver. This parameter used for clusters (when
        multiple host URLs are provided). Accepted values are "fallback",
        "roundrobin", "random" and "periodic". The default value is "fallback".
    :type host_resolver: str | arango.resolver.HostResolver
    :param resolver_max_tries: Number of attempts to process an HTTP request
        before throwing a ConnectionAbortedError. Must not be lower than the
        number of hosts.
    :type resolver_max_tries: int
    :param http_client: User-defined HTTP client.
    :type http_client: arango.http.HTTPClient
    :param serializer: User-defined JSON serializer. Must be a callable
        which takes a JSON data type object as its only argument and return
        the serialized string. If not given, ``json.dumps`` is used by default.
    :type serializer: callable
    :param deserializer: User-defined JSON de-serializer. Must be a callable
        which takes a JSON serialized string as its only argument and return
        the de-serialized object. If not given, ``json.loads`` is used by
        default.
    :type deserializer: callable
    :param verify_override: Override TLS certificate verification. This will
       override the verify method of the underlying HTTP client.
       None: Do not change the verification behavior of the underlying HTTP client.
       True: Verify TLS certificate using the system CA certificates.
       False: Do not verify TLS certificate.
       str: Path to a custom CA bundle file or directory.
    :type verify_override: Union[bool, str, None]
    :param request_timeout: This is the default request timeout (in seconds)
       for http requests issued by the client if the parameter http_client is
       not specified. The default value is 60.
       None: No timeout.
       int: Timeout value in seconds.
    :type request_timeout: int | float
    :param request_compression: Will compress requests to the server according to
        the given algorithm. No compression happens by default.
    :type request_compression: arango.http.RequestCompression | None
    :param response_compression: Tells the server what compression algorithm is
        acceptable for the response. No compression happens by default.
    :type response_compression: str | None
    """

    def __init__(
        self,
        hosts: Union[str, Sequence[str]] = "http://127.0.0.1:8529",
        host_resolver: Union[str, HostResolver] = "fallback",
        resolver_max_tries: Optional[int] = None,
        http_client: Optional[HTTPClient] = None,
        serializer: Callable[..., str] = default_serializer,
        deserializer: Callable[[str], Any] = default_deserializer,
        verify_override: Union[bool, str, None] = None,
        request_timeout: Union[int, float, None] = DEFAULT_REQUEST_TIMEOUT,
        request_compression: Optional[RequestCompression] = None,
        response_compression: Optional[str] = None,
    ) -> None:
        if isinstance(hosts, str):
            self._hosts = [host.strip("/") for host in hosts.split(",")]
        else:
            self._hosts = [host.strip("/") for host in hosts]

        host_count = len(self._hosts)
        self._host_resolver: HostResolver

        if host_count == 1:
            self._host_resolver = SingleHostResolver(1, resolver_max_tries)
        elif host_resolver == "fallback":
            self._host_resolver = FallbackHostResolver(host_count, resolver_max_tries)
        elif host_resolver == "random":
            self._host_resolver = RandomHostResolver(host_count, resolver_max_tries)
        elif host_resolver == "roundrobin":
            self._host_resolver = RoundRobinHostResolver(host_count, resolver_max_tries)
        elif host_resolver == "periodic":
            self._host_resolver = PeriodicHostResolver(host_count, resolver_max_tries)
        else:
            if not isinstance(host_resolver, HostResolver):
                raise ValueError("Invalid host resolver")
            self._host_resolver = host_resolver

        # Initializes the http client
        self._http = http_client or DefaultHTTPClient(request_timeout=request_timeout)

        self._serializer = serializer
        self._deserializer = deserializer
        self._sessions = [self._http.create_session(h) for h in self._hosts]

        # override SSL/TLS certificate verification if provided
        if verify_override is not None:
            for session in self._sessions:
                session.verify = verify_override

        self._request_compression = request_compression
        self._response_compression = response_compression

    def __repr__(self) -> str:
        return f"<ArangoClient {','.join(self._hosts)}>"

    def close(self) -> None:  # pragma: no cover
        """Close HTTP sessions."""
        for session in self._sessions:
            session.close()

    @property
    def hosts(self) -> Sequence[str]:
        """Return the list of ArangoDB host URLs.

        :return: List of ArangoDB host URLs.
        :rtype: [str]
        """
        return self._hosts

    @property
    def version(self) -> str:
        """Return the client version.

        :return: Client version.
        :rtype: str
        """
        version: str = importlib_metadata.version("python-arango")
        return version

    @property
    def request_timeout(self) -> Any:
        """Return the request timeout of the http client.

        :return: Request timeout.
        :rtype: Any
        """
        return self._http.request_timeout  # type: ignore

    # Setter for request_timeout
    @request_timeout.setter
    def request_timeout(self, value: Any) -> None:
        self._http.request_timeout = value  # type: ignore

    def db(
        self,
        name: str = "_system",
        username: str = "root",
        password: str = "",
        verify: bool = False,
        auth_method: str = "basic",
        user_token: Optional[str] = None,
        superuser_token: Optional[str] = None,
    ) -> StandardDatabase:
        """Connect to an ArangoDB database and return the database API wrapper.

        :param name: Database name.
        :type name: str
        :param username: Username for basic authentication.
        :type username: str
        :param password: Password for basic authentication.
        :type password: str
        :param verify: Verify the connection by sending a test request.
        :type verify: bool
        :param auth_method: HTTP authentication method. Accepted values are
            "basic" (default) and "jwt". If set to "jwt", the token is
            refreshed automatically using ArangoDB username and password. This
            assumes that the clocks of the server and client are synchronized.
        :type auth_method: str
        :param user_token: User generated token for user access.
            If set, parameters **username**, **password** and **auth_method**
            are ignored. This token is not refreshed automatically. If automatic
            token refresh is required, consider setting **auth_method** to "jwt"
            and using the **username** and **password** parameters instead. Token
            expiry will be checked.
        :type user_token: str
        :param superuser_token: User generated token for superuser access.
            If set, parameters **username**, **password** and **auth_method**
            are ignored. This token is not refreshed automatically. Token
            expiry will not be checked.
        :type superuser_token: str
        :return: Standard database API wrapper.
        :rtype: arango.database.StandardDatabase
        :raise arango.exceptions.ServerConnectionError: If **verify** was set
            to True and the connection fails.
        """
        connection: Connection

        if superuser_token is not None:
            connection = JwtSuperuserConnection(
                hosts=self._hosts,
                host_resolver=self._host_resolver,
                sessions=self._sessions,
                db_name=name,
                http_client=self._http,
                serializer=self._serializer,
                deserializer=self._deserializer,
                superuser_token=superuser_token,
                request_compression=self._request_compression,
                response_compression=self._response_compression,
            )
        elif user_token is not None:
            connection = JwtConnection(
                hosts=self._hosts,
                host_resolver=self._host_resolver,
                sessions=self._sessions,
                db_name=name,
                http_client=self._http,
                serializer=self._serializer,
                deserializer=self._deserializer,
                user_token=user_token,
                request_compression=self._request_compression,
                response_compression=self._response_compression,
            )
        elif auth_method.lower() == "basic":
            connection = BasicConnection(
                hosts=self._hosts,
                host_resolver=self._host_resolver,
                sessions=self._sessions,
                db_name=name,
                username=username,
                password=password,
                http_client=self._http,
                serializer=self._serializer,
                deserializer=self._deserializer,
                request_compression=self._request_compression,
                response_compression=self._response_compression,
            )
        elif auth_method.lower() == "jwt":
            connection = JwtConnection(
                hosts=self._hosts,
                host_resolver=self._host_resolver,
                sessions=self._sessions,
                db_name=name,
                username=username,
                password=password,
                http_client=self._http,
                serializer=self._serializer,
                deserializer=self._deserializer,
                request_compression=self._request_compression,
                response_compression=self._response_compression,
            )
        else:
            raise ValueError(f"invalid auth_method: {auth_method}")

        if verify:
            try:
                connection.ping()
            except ServerConnectionError as err:
                raise err
            except Exception as err:
                raise ArangoClientError(f"bad connection: {err}")

        return StandardDatabase(connection)
