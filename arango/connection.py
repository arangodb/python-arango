"""ArangoDB Connection Module."""

import json
import requests
from arango.util import unicode_to_str
from arango.exceptions import *


class ArangoConnection(object):
    """A wrapper around ArangoDB API.

    :param host: the address of the ArangoDB host
    :type host: str
    :param port: the port of the ArangoDB host
    :type port: int
    """

    def __init__(self, host="localhost", port=8529):
        self._host = host
        self._port = port
        self._sess = requests.Session()

    def _url(self, path, db=None):
        """Return the full request URL.

        :param path: the API path
        :type path: str
        :param db: name of the database
        :type db: str or None
        :returns: str
        """
        path=path[1:] if path.startswith("/") else path
        if db is not None:
            return "http://{host}:{port}/_db/{db}/_api/{path}".format(
                host=self._host, port=self._port, db = db, path=path
            )
        else:  # Use the default database if not specified
            return "http://{host}:{port}/_api/{path}".format(
                host=self._host, port=self._port, path=path
            )

    def _get(self, path, db=None, **kwargs):
        """Execute an HTTP GET method."""
        return self._sess.get(self._url(path, db), **kwargs)

    def _put(self, path, data="", db=None, **kwargs):
        """Execute an HTTP PUT method."""
        return self._sess.put(self._url(path, db), data, **kwargs)

    def _post(self, path, data="", db=None, **kwargs):
        """Execute an HTTP POST method."""
        return self._sess.post(self._url(path, db), data, **kwargs)

    def _delete(self, path, db=None, **kwargs):
        """Execute an HTTP DELETE method."""
        return self._sess.delete(self._url(path, db), **kwargs)

    @property
    def version(self):
        """Return the version number of ArangoDB.

        :returns: str -- version number
        :raises: ArangoError
        """
        res = self._get("/version")
        if res.status_code == 200:
            return unicode_to_str(res.json()["version"])
        else:
            raise ArangoError("Failed to get the version", res)

    ####################
    # Database Methods #
    ####################

    def databases(self, user_only=False):
        """Return a list of all database namess.

        :param user_only: return only the dbs the user has access to
        :type user_only: bool
        :returns: list -- list of the database names
        :raises: ArangoDatabaseReadError
        """
        if user_only:
            res = self._get("/database/user")
        else:
            res = self._get("/database")
        if res.status_code == 200:
            return unicode_to_str(res.json()["result"])
        else:
            raise ArangoDatabaseReadError(
                "Failed to get the databases", res
            )

    def database_exists(self, name):
        """Return True if the given database exists, False otherwise.

        :param name: the name of the database
        :type name: str
        :return: bool -- True if exists else False
        """
        return name in self.databases()

    def database_info(self, name=None):
        """Return the information of the current/specified database.

        :param name: the name of the database
        :type name: str or None
        :returns: str -- the name of the current database
        :raises: ArangoDatabaseReadError
        """
        res = self._get("/_api/database/current", name)
        if res.status_code == 200:
            return unicode_to_str(res.json()["result"])
        elif res.status_code == 404:
            raise ArangoDatabaseNotFoundError(name)
        else:
            raise ArangoDatabaseReadError(
                "Failed to get database '{}'".format(name), res
            )

    def create_database(self, db, users=None):
        """Create a new database.

        :param db: the name of the database
        :type db: str
        :param users: the ``users`` config sub-object
        :type users: dict
        :raises: ArangoDatabaseCreateError
        """
        data = {"name": db}
        if users is not None:
            data["users"] = users
        res = self._post(
            "/_api/database",
            data=json.dumps(data),
            db="_system"
        )
        if res.status_code == 201:
            return
        elif res.status_code == 409:
            raise ArangoDatabaseCreateError(
                "Database '{}' already exists".format(db)
            )
        else:
            raise ArangoDatabaseCreateError(
                "Failed to create database '{}'".format(db), res
            )

    def delete_database(self, db):
        """Delete the given database.

        :param db: the name of the database
        :type db: str
        :raises: ArangoDatabaseDeleteError
        """
        if db == self._db:
            self._db = "_system"
        res = self._delete("/_api/database/{}".format(db))
        if res.status_code != 200:
            raise ArangoDatabaseDeleteError(
                "Failed to delete database '{}'".format(db), res
            )

    ######################
    # Collection Methods #
    ######################

    def list_collections(self, exclude_system=False):
        """Return of list of the collections in the current database.

        :returns: list -- list of the names of the collections
        :raises: ArangoCollectionReadError
        """
        res = self._get(
            "/_api/collection?excludeSystem={}"
            .format("true" if exclude_system else "false")
        )
        if res.status_code == 200:
            return unicode_to_str(
                [col["name"] for col in res.json()["collections"]]
            )
        else:
            raise ArangoCollectionReadError(
                "Failed to retrieve the list of collections", res
            )

    def collection_exists(self, col_name):
        """Return True the collection exists, otherwise False.

        :param col_name: the name of the collection
        :type col_name: str
        :returns: bool
        """
        return col_name in self.list_collections()

    def collection_info(self, col_name, include_revision=True):
        """Return the statistics of the given collection.

        :param col_name: the name of the collection
        :type col_name: str
        :returns: dict
        """
        res = self._get("/_api/collection/{}/figures".format(col_name))
        if res.status_code == 200:
            if include_revision:
                rev = self._get("/_api/collection/{}/revision".format(col_name))
                rev
            return unicode_to_str(res.json())
        elif res.status_code == 404:
            raise ArangoCollectionNotFoundError(col_name)
        else:
            raise ArangoCollectionReadError(
                "Failed to retrieve the collection statistics", res
            )

    def collection(self, col_name):
        """Return the ``Collection`` object by identifier/name."""

    def create_collection(self, col_name, edge=False, config=None):
        """Create a new collection."""

    def delete_collection(self, col_name):
        """Delete the specified collection.

        :param col_name: the name of the collection
        :type col_name: str
        :raises: ArangoCollectionDeleteError
        """
        res = self._delete("/_api/collection/{}".format(col_name))
        if res.status_code != 200:
            raise ArangoCollectionDeleteError(
                "Failed to delete collection '{}'".format(col_name), res
            )

    def truncate_collection(self, col_name):
        """Remove all documents from the specified collection.

        :param col_name: the name of the collection
        :type col_name: str
        :raises: ArangoCollectionTruncateError
        """
        res = self._put("/_api/collection/{}/truncate".format(col_name))
        if res.status_code != 200:
            raise ArangoCollectionTruncateError(
                "Failed to truncate collection '{}'".format(col_name), res
            )

    def load_collection(self, col_name):
        """Load the specified collection into memory."""

    def unload_collection(self, col_name):
        """Unload the specified collection into memory."""

    def modify_collection(self, col_name, properties):
        """Change the properties of the specified collection."""

    def rename_collection(self, col_name, new_col_name):
        """Rename the specified collection."""

    def rotate_collection(self, col_name):
        """Rotate the journal of the specified collection."""

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
