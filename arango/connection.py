"""ArangoDB Connection."""

import json
from arango.client import ClientMixin
from arango.database import Database
from arango.exceptions import *


class Connection(ClientMixin):
    """A wrapper around ArangoDB API.

    :param protocol: the internet transfer protocol (default: http).
    :type protocol: str.
    :param host: ArangoDB host (default: localhost).
    :type host: str.
    :param port: ArangoDB port (default: 8529).
    :type port: int.
    :raises: ArangoConnectionError
    """

    def __init__(self, protocol="http", host="localhost", port=8529):
        self.protocol = protocol
        self.host = host
        self.port = port

        # Check the connection by requesting a header of the version endpoint
        url_prefix = "{}://{}:{}".format(protocol, host, port)
        test_endpoint = "{}/_api/version".format(url_prefix)
        if self._head(test_endpoint, full_path=True).status_code != 200:
            raise ArangoConnectionError(
                "Failed to connect to '{}'".format(url_prefix))

        # Cache for ArangoDatabase objects
        self._databases = {}

        # Default database (i.e. "_system")
        self._default_database = Database(
            name="_system",
            protocol=protocol,
            host=host,
            port=port
        )

    def __getattr__(self, attr):
        """Call __getattr__ of the default database if not here."""
        return getattr(self._default_database, attr)

    def __getitem__(self, item):
        """Call __getitem__ of the default database if not here."""
        return self._default_database[item]

    def _invalidate_database_cache(self):
        """Invalidate the Database object cache."""
        real_dbs = set(self.databases)
        cached_dbs = set(self._databases)
        for db in cached_dbs - real_dbs:
            del self._databases[db]
        for db in real_dbs - cached_dbs:
            self._databases[db] = Database(
                name=db,
                protocol=self.protocol,
                host=self.host,
                port=self.port,
            )

    @property
    def _url_prefix(self):
        """Return the URL prefix of this connection."""
        return "{protocol}://{host}:{port}".format(
            protocol=self.protocol,
            host=self.host,
            port=self.port
        )

    @property
    def version(self):
        """Return the version of ArangoDB.

        :returns: str -- the version number.
        :raises: ArangoVersionError.
        """
        res = self._get("/_api/version")
        if res.status_code != 200:
            raise ArangoVersionError(res)
        return res.obj["version"]

    @property
    def databases(self):
        """"Return the list of the database names.

        :returns: list -- list of the database names.
        :raises: ArangoDatabaseListError.
        """
        res = self._get("/_api/database")
        if res.status_code != 200:
            raise ArangoDatabaseListError(res)
        return res.obj["result"]

    def db(self, name):
        """Return the ArangoDatabase object of the specified name.

        :returns: Database -- the Database object.
        :raises: ArangoDatabaseNotFoundError.
        """
        if name in self._databases:
            return self._databases[name]
        else:
            self._invalidate_database_cache()
            if name not in self._databases:
                raise ArangoDatabaseNotFoundError(name)
            return self._databases[name]

    def create_database(self, name, users=None):
        """Create a new database.

        :param name: the name of the database to create.
        :type name: str.
        :param users: the ``users`` config sub-object.
        :type users: dict.
        :raises: ArangoDatabaseCreateError.
        """
        data = {"name": name, "users": users} if users else {"name": name}
        res = self._post("/_api/database", data=data)
        if res.status_code != 201:
            raise ArangoDatabaseCreateError(res)
        self._invalidate_database_cache()

    def delete_database(self, name):
        """Delete the specified database.

        :param name: the name of the database to delete.
        :type name: str.
        :raises: ArangoDatabaseDeleteError.
        """
        res = self._delete("/_api/database/{}".format(name))
        if res.status_code != 200:
            raise ArangoDatabaseDeleteError(res)
        self._invalidate_database_cache()


if __name__ == "__main__":
    a = Connection()
    print a.version
    for doc in a["blue"]:
        print doc["name"]