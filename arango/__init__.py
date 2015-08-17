"""ArangoDB's Top-Level API."""

from arango.database import Database
from arango.api import API
from arango.exceptions import *
from arango.constants import HTTP_OK, LOG_LEVELS
from arango.clients import DefaultClient
from arango.utils import uncamelify


class Arango(object):
    """Wrapper for ArangoDB's top-level APIs:

    1. Database Management
    2. User Management
    3. Administration & Monitoring
    4. Miscellaneous Functions
    """

    def __init__(self, protocol="http", host="localhost", port=8529,
                 username="root", password="", client=None):
        """Initialize the wrapper object.

        :param protocol: the internet transfer protocol (default: 'http')
        :type protocol: str
        :param host: ArangoDB host (default: 'localhost')
        :type host: str
        :param port: ArangoDB port (default: 8529)
        :type port: int or str
        :param username: ArangoDB username (default: 'root')
        :type username: str
        :param password: ArangoDB password (default: '')
        :type password: str
        :param client: HTTP client for this wrapper to use
        :type client: arango.clients.base.BaseClient or None
        :raises: ConnectionError
        """
        self.protocol = protocol
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        # Initialize the ArangoDB HTTP Client if not given
        if client is not None:
            self.client = client
        else:
            client_init_data = {"auth": (self.username, self.password)}
            self.client = DefaultClient(client_init_data)

        # Initialize the ArangoDB API wrapper object
        self.api = API(
            protocol=self.protocol,
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            client=self.client,
        )

        # Check the connection by requesting a header
        res = self.api.head("/_api/version")
        if res.status_code not in HTTP_OK:
            raise ConnectionError(res)

        # Cache for Database objects
        self._database_cache = {}

        # Default ArangoDB database wrapper object
        self._default_database = Database("_system", self.api)

    def __getattr__(self, attr):
        """Call __getattr__ of the default database."""
        return getattr(self._default_database, attr)

    def __getitem__(self, item):
        """Call __getitem__ of the default database."""
        return self._default_database.collection(item)

    def _invalidate_database_cache(self):
        """Invalidate the Database object cache."""
        real_dbs = set(self.databases["all"])
        cached_dbs = set(self._database_cache)
        for db_name in cached_dbs - real_dbs:
            del self._database_cache[db_name]
        for db_name in real_dbs - cached_dbs:
            self._database_cache[db_name] = Database(
                name=db_name,
                api=API(
                    protocol=self.protocol,
                    host=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    database=db_name,
                    client=self.client
                )
            )

    ###########################
    # Miscellaneous Functions #
    ###########################

    @property
    def version(self):
        """Return the version of ArangoDB.

        :returns: the version number
        :rtype: str
        :raises: VersionGetError
        """
        res = self.api.get("/_api/version")
        if res.status_code not in HTTP_OK:
            raise VersionGetError(res)
        return res.obj["version"]

    #######################
    # Database Management #
    #######################

    @property
    def databases(self):
        """"Return the database names.

        :returns: the database names
        :rtype: dict
        :raises: DatabaseListError
        """
        # Get the current user's databases
        res = self.api.get("/_api/database/user")
        if res.status_code not in HTTP_OK:
            raise DatabaseListError(res)
        user_databases = res.obj["result"]

        # Get all databases
        res = self.api.get("/_api/database")
        if res.status_code not in HTTP_OK:
            raise DatabaseListError(res)
        all_databases = res.obj["result"]

        return {"all": all_databases, "user": user_databases}

    def db(self, name):
        """Alias for self.database."""
        return self.database(name)

    def database(self, name):
        """Return the ``Database`` object of the specified name.

        :returns: the database object
        :rtype: arango.database.Database
        :raises: DatabaseNotFoundError
        """
        if name in self._database_cache:
            return self._database_cache[name]
        else:
            self._invalidate_database_cache()
            if name not in self._database_cache:
                raise DatabaseNotFoundError(name)
            return self._database_cache[name]

    def create_database(self, name, users=None):
        """Create a new database.

        :param name: the name of the new database
        :type name: str
        :param users: the users configurations
        :type users: dict
        :returns: the Database object
        :rtype: arango.database.Database
        :raises: DatabaseCreateError
        """
        data = {"name": name, "users": users} if users else {"name": name}
        res = self.api.post("/_api/database", data=data)
        if res.status_code not in HTTP_OK:
            raise DatabaseCreateError(res)
        self._invalidate_database_cache()
        return self.db(name)

    def delete_database(self, name, safe_delete=False):
        """Remove the database of the specified name.

        :param name: the name of the database to delete
        :type name: str
        :param safe_delete: whether to execute a safe delete (ignore 404)
        :type safe_delete: bool
        :raises: DatabaseDeleteError
        """
        res = self.api.delete("/_api/database/{}".format(name))
        if res.status_code not in HTTP_OK:
            if not (res.status_code == 404 and safe_delete):
                raise DatabaseDeleteError(res)
        self._invalidate_database_cache()

    ###################
    # User Management #
    ###################

    @property
    def users(self):
        """Return details on all users.

        :returns: a dictionary mapping user names to their information
        :rtype: dict
        :raises: UserGetAllError
        """
        res = self.api.get("/_api/user")
        if res.status_code not in HTTP_OK:
            raise UserGetAllError(res)
        # Uncamelify key(s) for consistent style
        result = {}
        for record in res.obj["result"]:
            result[record["user"]] = {
                "change_password": record.get("changePassword"),
                "active": record.get("active"),
                "extra": record.get("extra"),
            }
        return result

    def create_user(self, username, password, active=None, extra=None,
                    change_password=None):
        """Create a new user.

        if ``change_password`` is set to true, the only operation allowed by
        the user will be ``self.replace_user`` or ``self.update_user``. All
        other operations executed by the user will result in an HTTP 403.

        :param username: the name of the user
        :type username: str
        :param password: the user password
        :type password: str
        :param active: whether the user is active
        :type active: bool or None
        :param extra: any extra data about the user
        :type extra: dict or None
        :param change_password: whether the user must change the password
        :type change_password: bool or None
        :returns: the information about the new user
        :rtype: dict
        :raises: UserCreateError
        """
        data = {"user": username, "passwd": password}
        if active is not None:
            data["active"] = active
        if extra is not None:
            data["extra"] = extra
        if change_password is not None:
            data["changePassword"] = change_password

        res = self.api.post("/_api/user", data=data)
        if res.status_code not in HTTP_OK:
            raise UserCreateError(res)
        return {
            "active": res.obj.get("active"),
            "change_password": res.obj.get("changePassword"),
            "extra": res.obj.get("extra"),
        }

    def update_user(self, username, password=None, active=None, extra=None,
                    change_password=None):
        """Update an existing user.

        if ``change_password`` is set to true, the only operation allowed by
        the user will be ``self.replace_user`` or ``self.update_user``. All
        other operations executed by the user will result in an HTTP 403.

        :param username: the name of the existing user
        :type username: str
        :param password: the user password
        :type password: str
        :param active: whether the user is active
        :type active: bool or None
        :param extra: any extra data about the user
        :type extra: dict or None
        :param change_password: whether the user must change the password
        :type change_password: bool or None
        :returns: the information about the updated user
        :rtype: dict
        :raises: UserUpdateError
        """
        data = {}
        if password is not None:
            data["password"] = password
        if active is not None:
            data["active"] = active
        if extra is not None:
            data["extra"] = extra
        if change_password is not None:
            data["changePassword"] = change_password

        res = self.api.patch(
            "/_api/user/{user}".format(user=username), data=data
        )
        if res.status_code not in HTTP_OK:
            raise UserUpdateError(res)
        return {
            "active": res.obj.get("active"),
            "change_password": res.obj.get("changePassword"),
            "extra": res.obj.get("extra"),
        }

    def replace_user(self, username, password, active=None, extra=None,
                     change_password=None):
        """Replace an existing user.

        if ``change_password`` is set to true, the only operation allowed by
        the user will be ``self.replace_user`` or ``self.update_user``. All
        other operations executed by the user will result in an HTTP 403.

        :param username: the name of the existing user
        :type username: str
        :param password: the user password
        :type password: str
        :param active: whether the user is active
        :type active: bool or None
        :param extra: any extra data about the user
        :type extra: dict or None
        :param change_password: whether the user must change the password
        :type change_password: bool or None
        :returns: the information about the replaced user
        :rtype: dict
        :raises: UserReplaceError
        """
        data = {"user": username, "password": password}
        if active is not None:
            data["active"] = active
        if extra is not None:
            data["extra"] = extra
        if change_password is not None:
            data["changePassword"] = change_password

        res = self.api.put(
            "/_api/user/{user}".format(user=username), data=data
        )
        if res.status_code not in HTTP_OK:
            raise UserReplaceError(res)
        return {
            "active": res.obj.get("active"),
            "change_password": res.obj.get("changePassword"),
            "extra": res.obj.get("extra"),
        }

    def delete_user(self, username, safe_delete=False):
        """Delete an existing user.

        :param username: the name of the user
        :type username: str
        :param safe_delete: ignores HTTP 404 if set to True
        :type safe_delete: bool
        :returns: True if the operation succeeds
        :rtype: bool
        :raises: UserDeleteError
        """
        res = self.api.delete("/_api/user/{user}".format(user=username))
        if res.status_code not in HTTP_OK:
            if not (res.status_code == 404 and safe_delete):
                raise UserDeleteError(res)
        return True

    ###############################
    # Administration & Monitoring #
    ###############################

    def read_log(self, upto=None, level=None, start=None, size=None,
                 offset=None, search=None, sort=None):
        """Read global log from the server

        The parameters ``upto`` and ``level`` are mutually exclusive.
        The values for ``upto`` and ``level`` must be one of:

        'fatal' or 0
        'error' or 1
        'warning' or 2
        'info' or 3 (default)
        'debug' or 4

        The parameters ``offset`` and ``size`` can be used for pagination.
        The values for ``sort`` must be one of 'asc' or 'desc'.

        :param upto: return entries up to this level
        :type upto: str or int or None
        :param level: return entries of this level only
        :type level: str or int or None
        :param start: return entries whose id >= to the given value
        :type start: int or None
        :param size: restrict the result to the given value
        :type size: int or None
        :param offset: return entries skipping the given number
        :type offset: int or None
        :param search: return only the entires containing the given text
        :type search: str or None
        :param sort: sort the entries according to their lid values
        :type sort: str or None
        :returns: the server log
        :rtype: dict
        :raises: LogGetError
        """
        params = {}
        if upto is not None:
            params["upto"] = upto
        if level is not None:
            params["level"] = level
        if start is not None:
            params["start"] = start
        if size is not None:
            params["size"] = size
        if offset is not None:
            params["offset"] = offset
        if search is not None:
            params["search"] = search
        if sort is not None:
            params["sort"] = sort
        res = self.api.get("/_admin/log")
        if res.status_code not in HTTP_OK:
            LogGetError(res)
        return res.obj

    def reload_routing_info(self):
        """Reload the routing information from the collection ``routing``.

        :returns: True if the operation succeeds
        :rtype: bool
        :raises: RoutingInfoReloadError
        """
        res = self.api.post("/_admin/routing/reload")
        if res.status_code not in HTTP_OK:
            raise RountingInfoReloadError(res)
        return True

    @property
    def statistics(self):
        """Return the statisics information.

        :returns: the statistics information
        :rtype: dict
        :raises: StatisticsGetError
        """
        res = self.api.get("/_admin/statistics")
        if res.status_code not in HTTP_OK:
            raise StatisticsGetError(res)
        del res.obj["code"]
        del res.obj["error"]
        return res.obj

    @property
    def statistics_description(self):
        """Return the description of the statistics from self.statistics.

        :returns: the statistics description
        :rtype: dict
        :raises: StatisticsDescriptionError
        """
        res = self.api.get("/_admin/statistics-description")
        if res.status_code not in HTTP_OK:
            raise StatisticsDescriptionGetError(res)
        del res.obj["code"]
        del res.obj["error"]
        return res.obj

    @property
    def server_role(self):
        """Return the role of the server in cluster

        Possible return values are:

        COORDINATOR: the server is a coordinator in a cluster
        PRIMARY:     the server is a primary database server in a cluster
        SECONDARY:   the server is a secondary database server in a cluster
        UNDEFINED:   in a cluster, UNDEFINED is returned if the server role
                     cannot be determined. On a single server, UNDEFINED is
                     the only possible return value.

        :returns: the server role
        :rtype: str
        :raises: ServerRoleGetError
        """
        res = self.api.get("/_admin/server/role")
        if res.status_code not in HTTP_OK:
            raise ServerRoleGetError(res)
        return res.obj["role"]

if __name__ == "__main__":
    a = Arango()
    print(a.version)
