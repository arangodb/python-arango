"""ArangoDB Connection."""

from arango.database import Database
from arango.client import Client
from arango.exceptions import *


class Arango(object):
    """A wrapper around ArangoDB API.

    :param str protocol: the internet transfer protocol (default: http)
    :param str host: ArangoDB host (default: localhost)
    :param int port: ArangoDB port (default: 8529)
    :raises: ArangoConnectionError
    """

    def __init__(self, protocol="http", host="localhost", port=8529,
                 username="root", password=""):
        self._protocol = protocol
        self._host = host
        self._port = port
        self._username = username
        self._password = password

        self._client = Client(
            protocol=self._protocol,
            host=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
        )
        # Check the connection by requesting a header of the version endpoint
        res = self._client.head("/_api/version")
        if res.status_code != 200:
            raise ArangoConnectionError(
                "Failed to connect to '{host}' ({status}: {reason})".format(
                    host=self._host,
                    status=res.status_code,
                    reason=res.reason
                )
            )
        # Cache for Collection objects
        self._database_cache = {}
        # Default database (i.e. "_system")
        self._default_database = Database("_system", self._client)

    def __getattr__(self, attr):
        """Call __getattr__ of the default database if not here."""
        return getattr(self._default_database, attr)

    def __getitem__(self, item):
        """Call __getitem__ of the default database if not here."""
        return self._default_database[item]

    def _invalidate_database_cache(self):
        """Invalidate the Database object cache."""
        real_dbs = set(self.databases["all"])
        cached_dbs = set(self._database_cache)
        for db_name in cached_dbs - real_dbs:
            del self._database_cache[db_name]
        for db_name in real_dbs - cached_dbs:
            self._database_cache[db_name] = Database(
                name=db_name,
                client=Client(
                    protocol=self._protocol,
                    host=self._host,
                    port=self._port,
                    username=self._username,
                    password=self._password,
                    db_name=db_name
                )
            )

    @property
    def version(self):
        """Return the version of ArangoDB.

        :returns: str -- the version number
        :raises: ArangoVersionError
        """
        res = self._client.get("/_api/version")
        if res.status_code != 200:
            raise ArangoVersionError(res)
        return res.obj["version"]

    @property
    def databases(self):
        """"Return the database names.

        :returns: dict -- database names
        :raises: ArangoDatabaseListError
        """
        res = self._client.get("/_api/database/user")
        if res.status_code != 200:
            raise ArangoDatabaseListError(res)
        user_databases = res.obj["result"]

        res = self._client.get("/_api/database")
        if res.status_code != 200:
            raise ArangoDatabaseListError(res)
        all_databases = res.obj["result"]

        return {"user": user_databases, "all": all_databases}

    def db(self, name):
        """Return the ``Database`` object of the given name.

        :returns: Database -- the Database object
        :raises: ArangoDatabaseNotFoundError
        """
        if name in self._database_cache:
            return self._database_cache[name]
        else:
            self._invalidate_database_cache()
            if name not in self._database_cache:
                raise ArangoDatabaseNotFoundError(name)
            return self._database_cache[name]

    def create_database(self, name, users=None):
        """Create a new database.

        :param str name: the name of the new database
        :param dict users: the ``users`` configurations
        :raises: ArangoDatabaseCreateError
        """
        data = {"name": name, "users": users} if users else {"name": name}
        res = self._client.post("/_api/database", data=data)
        if res.status_code != 201:
            raise ArangoDatabaseCreateError(res)
        self._invalidate_database_cache()

    def delete_database(self, name):
        """Delete the database of the given name.

        :param str name: the name of the database to delete
        :raises: ArangoDatabaseDeleteError
        """
        res = self._client.delete("/_api/database/{}".format(name))
        if res.status_code != 200:
            raise ArangoDatabaseDeleteError(res)
        self._invalidate_database_cache()


if __name__ == "__main__":
    a = Arango()
    print a.version