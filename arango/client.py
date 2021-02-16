__all__ = ["ArangoClient"]

from json import dumps, loads
from typing import Any, Callable, Optional, Sequence, Union

from pkg_resources import get_distribution

from arango.connection import (
    BasicConnection,
    Connection,
    JwtConnection,
    JwtSuperuserConnection,
)
from arango.database import StandardDatabase
from arango.exceptions import ServerConnectionError
from arango.http import DefaultHTTPClient, HTTPClient
from arango.resolver import (
    HostResolver,
    RandomHostResolver,
    RoundRobinHostResolver,
    SingleHostResolver,
)


class ArangoClient:
    """ArangoDB client.

    :param hosts: Host URL or list of URLs (coordinators in a cluster).
    :type hosts: str | [str]
    :param host_resolver: Host resolver. This parameter used for clusters (when
        multiple host URLs are provided). Accepted values are "roundrobin" and
        "random". Any other value defaults to round robin.
    :type host_resolver: str
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
    """

    def __init__(
        self,
        hosts: Union[str, Sequence[str]] = "http://127.0.0.1:8529",
        host_resolver: str = "roundrobin",
        http_client: Optional[HTTPClient] = None,
        serializer: Callable[..., str] = lambda x: dumps(x),
        deserializer: Callable[[str], Any] = lambda x: loads(x),
    ) -> None:
        if isinstance(hosts, str):
            self._hosts = [host.strip("/") for host in hosts.split(",")]
        else:
            self._hosts = [host.strip("/") for host in hosts]

        host_count = len(self._hosts)
        self._host_resolver: HostResolver

        if host_count == 1:
            self._host_resolver = SingleHostResolver()
        elif host_resolver == "random":
            self._host_resolver = RandomHostResolver(host_count)
        else:
            self._host_resolver = RoundRobinHostResolver(host_count)

        self._http = http_client or DefaultHTTPClient()
        self._serializer = serializer
        self._deserializer = deserializer
        self._sessions = [self._http.create_session(h) for h in self._hosts]

    def __repr__(self) -> str:
        return f"<ArangoClient {','.join(self._hosts)}>"

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
        return get_distribution("python-arango").version

    def db(
        self,
        name: str = "_system",
        username: str = "root",
        password: str = "",
        verify: bool = False,
        auth_method: str = "basic",
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
        :param superuser_token: User generated token for superuser access.
            If set, parameters **username**, **password** and **auth_method**
            are ignored. This token is not refreshed automatically.
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
            )
        else:
            raise ValueError(f"invalid auth_method: {auth_method}")

        if verify:
            try:
                connection.ping()
            except ServerConnectionError as err:
                raise err
            except Exception as err:
                raise ServerConnectionError(f"bad connection: {err}")

        return StandardDatabase(connection)
