"""ArangoDB Connection Module."""

import json
import requests
from arango.exceptions import (
    ArangoError,
    ArangoDatabaseReadError,
    ArangoDatabaseCreateError,
    ArangoDatabaseDeleteError,
)


class ArangoConnection(object):
    """A wrapper around ArangoDB API."""

    def __init__(self, host="localhost", port=8529, db_name="_system"):
        self._host = host
        self._port = port
        self._db_name = db_name
        self._session = requests.Session()

    def _get_url(self, path, db_name=None):
        """Return the full request URL.

        :param path: path for the URL
        :type path: str
        :param db_name: name of the database
        :type db_name: str or None
        :returns: str
        """
        return "http://{host}:{port}/_db/{db_name}/{path}".format(
            host=self._host,
            port=self._port,
            db_name=db_name if db_name else self._db_name,
            path=path[1:] if path.startswith("/") else path
        )

    def _get(self, path, db_name=None, **kwargs):
        """Execute an HTTP GET method."""
        return self._session.get(
            self._get_url(path, db_name), **kwargs
        )

    def _put(self, path, data="", db_name=None, **kwargs):
        """Execute an HTTP PUT method."""
        return self._session.put(
            self._get_url(path, db_name), data, **kwargs
        )

    def _post(self, path, data="", db_name=None, **kwargs):
        """Execute an HTTP POST method."""
        return self._session.post(
            self._get_url(path, db_name), data, **kwargs
        )

    def _delete(self, path, db_name=None, **kwargs):
        """Execute an HTTP DELETE method."""
        return self._session.delete(
            self._get_url(path, db_name), **kwargs
        )

    @property
    def version(self):
        """Return the version number of ArangoDB.

        :returns: str -- version number
        :raises: ArangoError
        """
        res = self._get("/_api/version")
        if res.status_code == 200:
            return str(res.json()["version"])
        else:
            raise ArangoError(
                "Failed to retrieve the version", res
            )

    ####################
    # Database Methods #
    ####################

    def database_info(self, db_name=None):
        """Return the information of the current/specified database.

        :param db_name: name of the database
        :type db_name: str or None
        :returns: str -- the name of the current database
        :raises: ArangoDatabaseReadError
        """
        db_name = db_name if db_name is not None else self._db_name
        res = self._get("/_api/database/current", db_name)
        if res.status_code == 200:
            return res.json()["result"]
        elif res.status_code == 404:
            raise ArangoDatabaseReadError(
                "Database '{}' does not exist".format(db_name)
            )
        else:
            raise ArangoDatabaseReadError(
                "Failed to read database '{}'".format(db_name), res
            )

    def database_exists(self, db_name):
        """Return True iff the given database exists.

        :param db_name: the name of the database
        :type db_name: str
        :return: bool
        """
        return db_name in self.list_databases()

    def list_databases(self, user_only=False):
        """Return a list of all databases.

        :param user_only: return only the databases the user has access to
        :type user_only: bool
        :returns: list -- list of the database names
        :raises: ArangoDatabaseReadError
        """
        if user_only:
            res = self._get("/_api/database/user")
        else:
            res = self._get("/_api/database", db_name="_system")
        if res.status_code == 200:
            return res.json()["result"]
        else:
            raise ArangoDatabaseReadError(
                "Failed to retrieve the list of the databases", res
            )

    def use_database(self, db_name):
        """Switch to an existing database.

        :param db_name: the name of the database
        :type db_name: str
        :raises: ArangoDatabaseReadError
        """
        if db_name in self.list_databases(user_only=True):
            self._db_name = db_name
        elif db_name in self.list_databases():
            raise ArangoDatabaseReadError(
                "The user does not have access to database '{}'"
                .format(db_name)
            )
        else:
            raise ArangoDatabaseReadError(
                "Database '{}' does not exist".format(db_name)
            )

    def create_database(self, db_name, users=None):
        """Create a new database.

        :param db_name: the name of the database
        :type db_name: str
        :param users: the ``users`` config sub-object
        :type users: dict
        :raises: ArangoDatabaseCreateError
        """
        data = {"name": db_name}
        if users is not None:
            data["users"] = users
        res = self._post(
            "/_api/database",
            data=json.dumps(data),
            db_name="_system"
        )
        if res.status_code == 201:
            return
        elif res.status_code == 409:
            raise ArangoDatabaseCreateError(
                "Database '{}' already exists".format(db_name)
            )
        else:
            raise ArangoDatabaseCreateError(
                "Failed to create database '{}'".format(db_name), res
            )

    def delete_database(self, db_name):
        """Delete the given database.

        :param db_name: the name of the database
        :type db_name: str
        :raises: ArangoDatabaseDeleteError
        """
        if db_name == self._db_name:
            self._db_name = "_system"
        res = self._delete("/_api/database/{}".format(db_name))
        if res.status_code != 200:
            raise ArangoDatabaseDeleteError(
                "Failed to delete database '{}'".format(db_name), res
            )

    ######################
    # Collection Methods #
    ######################

    def list_collections(self):
        """Return of list of the collections in the current database."""

    def collection_exists(self, col_name):
        """Return True iff the collection exists in the current database."""

    def get_collection(self, col_name):
        """Get collection by identifier/name."""

    def create_collection(self, col_name, is_edge=False, properties=None):
        """Create a new collection."""

    def delete_collection(self, col_name):
        """Delete the specified collection."""

    ####################
    # Document Methods #
    ####################

    def has_document(self, doc_id):
        """Return True if the given document exists else False."""

    def get_document(self, doc_id):
        """Get document by handle (_id)."""

    def create_document(self, data):
        """Create a new document"""

    def update_document(self, doc_id, data, overwrite):
        """Partially update document."""

    def delete_document(self, doc_id, data, overwrite):
        """Delete the specified document."""


if __name__ == "__main__":
    TEST = ArangoConnection()
