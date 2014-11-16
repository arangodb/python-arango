"""ArangoDB Connection Module."""

import json

from arango.util import unicode_to_str
from arango.client import ArangoRequestClient
from arango.database import ArangoDatabase
from arango.exceptions import *


class ArangoConnection(object):
    """A wrapper around ArangoDB API.

    :param host: the address of the ArangoDB host.
    :type host: str.
    :param port: the port of the ArangoDB host.
    :type port: int.
    """

    def __init__(self, host="localhost", port=8529):
        self._client = ArangoRequestClient(host, port)
        self.db = ArangoDatabase(self._client)

    def db(self, name):


    def __getattr__(self, host)

    @property
    def version(self):
        """Return the version number of ArangoDB.

        :returns: str -- version number.
        :raises: ArangoError.
        """
        res = self._client.get("/version")
        if res.status_code != 200:
            raise ArangoError("Failed to get ArangoDB version", res)
        return unicode_to_str(res.json()["version"])

    def databases(self, user_only=False):
        """Return a list of all database names.

        :param user_only: return only the dbs the user has access to.
        :type user_only: bool.
        :returns: list -- list of the database names.
        :raises: ArangoDatabaseReadError.
        """
        res = self._get("/database/user" if user_only else "/database")
        if res.status_code != 200:
            raise ArangoDatabaseError("Failed to get the database list", res)
        return unicode_to_str(res.json()["result"])

    def database_exists(self, name):
        """Return True if the given database exists, False otherwise.

        :param name: the name of the database.
        :type name: str.
        :return: bool -- True if exists else False.
        """
        return name in self.databases()

    def database_info(self, name=None):
        """Return the information of the current/specified database.

        :param name: the name of the database (if not given use current).
        :type name: str or None.
        :returns: str -- the name of the current database.
        :raises: ArangoDatabaseNotFoundError, ArangoDatabaseError.
        """
        res = self._get("/database/current", name)
        if res.status_code == 200:
            return unicode_to_str(res.json()["result"])
        elif res.status_code == 404:
            raise ArangoDatabaseNotFoundError(name)
        else:
            raise ArangoDatabaseError(
                "Failed to get info on database '{}'".format(name), res
            )

    def create_database(self, name, users=None):
        """Create a new database.

        :param name: the name of the database.
        :type name: str.
        :param users: the ``users`` config sub-object.
        :type users: dict.
        :raises: ArangoDatabaseCreateError.
        """
        data = {"name": name, "users": users} if users else {"name": name}
        res = self._post("/database", data=json.dumps(data))
        if res.status_code == 201:
            return  # Database created successfully
        elif res.status_code == 409:
            raise ArangoDatabaseCreateError(
                "Database '{}' already exists".format(name), res
            )
        else:
            raise ArangoDatabaseCreateError(
                "Failed to create database '{}'".format(name), res
            )

    def delete_database(self, name):
        """Delete the given database.

        :param name: the name of the database.
        :type name: str.
        :raises: ArangoDatabaseDeleteError.
        """
        res = self._delete("/database/{}".format(name))
        if res.status_code != 200:
            raise ArangoDatabaseDeleteError(name, res)

    ######################
    # Collection Methods #
    ######################

    def collections(self, exclude_system=False):
        """Return of list of the collections in the current database.

        :returns: list -- list of the names of the collections.
        :raises: ArangoCollectionReadError.
        """
        res = self._get("/collection?excludeSystem={}"
                        .format("true" if exclude_system else "false"))
        if res.status_code == 200:
            return unicode_to_str(
                [col["name"] for col in res.json()["collections"]]
            )
        else:
            raise ArangoCollectionError(
                "Failed to get the list of collections", res
            )

    def collection_exists(self, name):
        """Return True the collection exists, otherwise False.

        :param name: the name of the collection.
        :type name: str.
        :returns: bool.
        """
        return name in self.collections()

    def collection_statistics(self, name):
        """Return the statistics of the given collection.

        :param name: the name of the collection.
        :type name: str.
        :returns: dict.
        """
        res = self._get("/collection/{}/figures".format(name))
        if res.status_code == 200:
            return unicode_to_str(res.json())
        elif res.status_code == 404:
            raise ArangoCollectionNotFoundError(name)
        else:
            raise ArangoCollectionError(
                "Failed to retrieve the collection statistics", res
            )

    def collection_revision(self, name):
        """"""
        res = self._get("/collection/{}/figures".format(name))
        if res.status_code == 200:
            return unicode_to_str(res.json())
        elif res.status_code == 404:
            raise ArangoCollectionNotFoundError(name)
        else:
            raise ArangoCollectionError(
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

    def modify_document(self, doc_id, data, overwrite):
        """Partially update document."""

    def delete_document(self, doc_id, data, overwrite):
        """Delete the specified document."""


if __name__ == "__main__":
    a = ArangoConnection()
    print a.version
    print a.databases(user_only=True)
    print a.databases()

