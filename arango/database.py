"""ArangoDB Database."""

from arango.aql import AQLMixin
from arango.client import Client
from arango.collection import Collection
from arango.exceptions import *


class Database(Client, AQLMixin):
    """A wrapper around ArangoDB database API."""

    def __init__(self, name="_system", protocol="http",
                 host="localhost", port=8529):
        self.name = name
        self.protocol = protocol
        self.host = host
        self.port = port
        # Cache for ArangoCollection objects
        self._collections = {}

    def __getitem__(self, name):
        """Return the Collection object of the specified name.

        :param name: the name of the collection.
        :type name: str.
        :returns: Collection.
        :raises: TypeError, ArangoCollectionNotFound.
        """
        if not isinstance(name, str):
            raise TypeError("Expecting a str.")
        if name in self._collections:
            return self._collections[name]
        else:
            self._update_collection_cache()
            if name not in self._collections:
                raise ArangoCollectionNotFoundError(name)
            return self._collections[name]

    def _update_collection_cache(self):
        """Invalidate the collection cache."""
        real_cols = set(self.collections)
        cached_cols = set(self._collections)
        for col in cached_cols - real_cols:
            del self._collections[col]
        for col in real_cols - cached_cols:
            self._collections[col] = Collection(
                name=col,
                protocol=self.protocol,
                host=self.host,
                port=self.port,
                db_name=self.name,
            )

    @property
    def _url_prefix(self):
        """Return the URL prefix of this database."""
        return "{protocol}://{host}:{port}/_db/{name}".format(
            protocol=self.protocol,
            host=self.host,
            port=self.port,
            name=self.name
        )

    @property
    def properties(self):
        """Return the properties of this database.

        :returns: dict -- the database properties.
        :raises: ArangoDatabasePropertyError.
        """
        res = self._get("/_api/database/current")
        if res.status_code != 200:
            raise ArangoDatabasePropertyError(res)
        return res.obj["result"]

    @property
    def id(self):
        """Return the ID of this database.

        :returns: str.
        """
        return self.properties["id"]

    @property
    def path(self):
        """Return the file path of this database.

        :returns: str.
        """
        return self.properties["path"]

    @property
    def is_system(self):
        """Return True if this is a system database, otherwise False.

        :returns: bool.
        """
        return self.properties["isSystem"]

    @property
    def collections(self):
        """Return the names of the collections in this database.

        :returns: list -- list of collection names.
        :raises: ArangoCollectionListError.
        """
        res = self._get("/_api/collection")
        if res.status_code != 200:
            raise ArangoCollectionListError(res)
        return res.obj["names"]

    def create_collection(self, name, wait_for_sync=False, do_compact=True,
                          journal_size=None, is_system=False, is_volatile=False,
                          key_options=None, is_edge=False):
        """Create a new collection."""
        data = {
            "name": name,
            "waitForSync": wait_for_sync,
            "doCompact": do_compact,
            "isSytem": is_system,
            "isVolatile": is_volatile,
            "type": 3 if is_edge else 2,
            "keyOptions": key_options if key_options is not None else {},
        }
        if journal_size:
            data["journalSize"] = journal_size

        res = self._post("/_api/collection", data=data)
        if res.status_code != 200:
            raise ArangoCollectionCreateError(res)
        self._update_collection_cache()

    def delete_collection(self, name):
        """Delete the specified collection.

        :param name: the name of the collection.
        :type name: str.
        :raises: ArangoCollectionDeleteError.
        """
        res = self._delete("/_api/collection/{}".format(name))
        if res.status_code != 200:
            raise ArangoCollectionDeleteError(res)
        self._update_collection_cache()

    def rename_collection(self, name, new_name):
        """Rename the specified collection.

        :param name: the name of the collection.
        :type name: str.
        :param new_name: the new name for the collection.
        :type new_name: str.
        :raises: ArangoCollectionRenameError.
        """
        res = self._put("/_api/collection/{}/rename".format(name),
                        data={"name": new_name})
        if res.status_code != 200:
            raise ArangoCollectionRenameError(res)
        self._update_collection_cache()
