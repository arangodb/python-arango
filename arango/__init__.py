"""ArangoDB Connection."""

from arango.database import Database
from arango.api import ArangoAPI
from arango.exceptions import *


class Arango(object):
    """A wrapper around ArangoDB API.

    :param protocol: the internet transfer protocol (default: http)
    :type protocol: str
    :param host: ArangoDB host (default: localhost)
    :type host: str
    :param port: ArangoDB port (default: 8529)
    :type port: int
    :param username: the username
    :type username: str
    :param password: the password
    :type password: str
    :param client: the custom client object
    :type client: arango.clients.base.BaseArangoClient
    :raises: ArangoConnectionError
    """

    def __init__(self, protocol="http", host="localhost", port=8529,
                 username="root", password="", client=None):
        self._protocol = protocol
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._client = client
        self._api = ArangoAPI(
            protocol=self._protocol,
            host=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            client=self._client,
        )
        # Check the connection by requesting a header of the version endpoint
        res = self._api.head("/_api/version")
        if res.status_code != 200:
            raise ArangoConnectionError(
                "Failed to connect to '{host}' ({status}: {reason})".format(
                    host=self._host,
                    status=res.status_code,
                    reason=res.reason
                )
            )
        # Cache for Database objects
        self._database_cache = {}
        # Default database (i.e. "_system")
        self._default_database = Database("_system", self._api)

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
                api=ArangoAPI(
                    protocol=self._protocol,
                    host=self._host,
                    port=self._port,
                    username=self._username,
                    password=self._password,
                    db_name=db_name,
                    client=self._client
                )
            )

    @property
    def version(self):
        """Return the version of ArangoDB.

        :returns: the version number
        :rtype: str
        :raises: ArangoVersionError
        """
        res = self._api.get("/_api/version")
        if res.status_code != 200:
            raise ArangoVersionError(res)
        return res.obj["version"]

    @property
    def databases(self):
        """"Return the database names.

        :returns: the database names
        :rtype: dict
        :raises: ArangoDatabaseListError
        """
        res = self._api.get("/_api/database/user")
        if res.status_code != 200:
            raise ArangoDatabaseListError(res)
        user_databases = res.obj["result"]

        res = self._api.get("/_api/database")
        if res.status_code != 200:
            raise ArangoDatabaseListError(res)
        all_databases = res.obj["result"]

        return {"all": all_databases, "user": user_databases}

    def db(self, name):
        """Alias for self.database."""
        return self.database(name)

    def database(self, name):
        """Return the ``Database`` object of the specified name.

        :returns: the database object
        :rtype: arango.database.Database
        :raises: ArangoDatabaseNotFoundError
        """
        if name in self._database_cache:
            return self._database_cache[name]
        else:
            self._invalidate_database_cache()
            if name not in self._database_cache:
                raise ArangoDatabaseNotFoundError(name)
            return self._database_cache[name]

    def add_database(self, name, users=None):
        """Add a new database.

        :param name: the name of the new database
        :type name: str
        :param users: the users configurations
        :type users: dict
        :returns: the Database object
        :rtype: arango.database.Database
        :raises: ArangoDatabaseCreateError
        """
        data = {"name": name, "users": users} if users else {"name": name}
        res = self._api.post("/_api/database", data=data)
        if res.status_code != 201:
            raise ArangoDatabaseAddError(res)
        self._invalidate_database_cache()
        return self.db(name)

    def remove_database(self, name):
        """Remove the database of the specified name.

        :param name: the name of the database to remove
        :type name: str
        :raises: ArangoDatabaseDeleteError
        """
        res = self._api.delete("/_api/database/{}".format(name))
        if res.status_code != 200:
            raise ArangoDatabaseRemoveError(res)
        self._invalidate_database_cache()


if __name__ == "__main__":
    a = Arango()
    print a.version
