"""ArangoDB Database."""


from arango.query import Query
from arango.connection import Connection
from arango.collection import Collection
from arango.exceptions import *


class Database(object):
    """A wrapper around ArangoDB database API."""

    def __init__(self, name, connection):
        self.name = name
        self._conn = connection
        self._collection_cache = {}
        self._query = Query(self._conn)

    def __getitem__(self, name):
        """Return the Collection object of the specified name.

        :param name: the name of the collection.
        :type name: str.
        :returns: Collection.
        :raises: TypeError, ArangoCollectionNotFound.
        """
        return self.collection(name)

    def _update_collection_cache(self):
        """Invalidate the collection cache."""
        real_cols = set(self.collections)
        cached_cols = set(self._collection_cache)
        for col_name in cached_cols - real_cols:
            del self._collection_cache[col_name]
        for col_name in real_cols - cached_cols:
            self._collection_cache[col_name] = Collection(
                name=col_name,
                connection=self._conn
            )

    @property
    def properties(self):
        """Return all properties of this database.

        :returns: dict -- the database properties.
        :raises: ArangoDatabasePropertyError.
        """
        res = self._conn.get("/_api/database/current")
        if res.status_code != 200:
            raise ArangoDatabasePropertyError(res)
        return res.obj["result"]

    @property
    def id(self):
        """Return the ID of this database.

        :returns: str.
        :raises: ArangoDatabasePropertyError.
        """
        return self.properties["id"]

    @property
    def path(self):
        """Return the file path of this database.

        :returns: str.
        :raises: ArangoDatabasePropertyError.
        """
        return self.properties["path"]

    @property
    def is_system(self):
        """Return True if this is a system database, otherwise False.

        :returns: bool.
        :raises: ArangoDatabasePropertyError.
        """
        return self.properties["isSystem"]

    @property
    def collections(self):
        """Return the names of the collections in this database.

        :returns: list -- list of collection names.
        :raises: ArangoCollectionListError.
        """
        res = self._conn.get("/_api/collection")
        if res.status_code != 200:
            raise ArangoCollectionListError(res)
        return res.obj["names"]

    @property
    def aql_functions(self):
        """Return the AQL functions defined in this database.

        :returns: dict -- function name to code.
        :raises: ArangoAQLFunctionListError.
        """
        res = self._conn.get("/_api/aqlfunction")
        if res.status_code != 200:
            raise ArangoAQLFunctionListError(res)
        return {func["name"]: func["code"]for func in res.obj}

    def collection(self, name):
        """Return the Collection object of the specified name.

        :param name: the name of the collection.
        :type name: str.
        :returns: Collection.
        :raises: TypeError, ArangoCollectionNotFound.
        """
        if not isinstance(name, str):
            raise TypeError("Expecting a str.")
        if name in self._collection_cache:
            return self._collection_cache[name]
        else:
            self._update_collection_cache()
            if name not in self._collection_cache:
                raise ArangoCollectionNotFoundError(name)
            return self._collection_cache[name]

    def col(self, name):
        return self.collection(name)

    ########################
    # Managing Collections #
    ########################

    def create_collection(self, name, wait_for_sync=False, do_compact=True,
                          journal_size=None, is_system=False, is_volatile=False,
                          key_options=None, is_edge=False):
        """Create a new collection in this database.

        :param name: name of the new collection.
        :type name: str.
        :param wait_for_sync: whether or not the collection waits for sync to disk.
        :type wait_for_sync: bool.
        :param do_compact: whether or not the collection will be compacted.
        :type do_compact: bool.
        :param journal_size: the maximal size of journal or datafile.
        :type journal_size: int or None.
        :param is_system: whether or not the collection is a system collection.
        :type is_system: bool.
        :param is_volatile: whether or not the col is kept in-memory only.
        :type is_volatile: bool.
        :param key_options: options for document key generation.
        :type key_options: dict.
        :param is_edge: whether or not the collection is an edge collection.
        :type is_edge: bool.
        :raises: ArangoCollectionCreateError
        """
        data = {
            "name": name,
            "waitForSync": wait_for_sync,
            "doCompact": do_compact,
            "isSytem": is_system,
            "isVolatile": is_volatile,
            "type": 3 if is_edge else 2,
            "keyOptions": {} if key_options is None else key_options,
        }
        if journal_size:
            data["journalSize"] = journal_size

        res = self._conn.post("/_api/collection", data=data)
        if res.status_code != 200:
            raise ArangoCollectionCreateError(res)
        self._update_collection_cache()

    def delete_collection(self, name):
        """Delete the specified collection in this database.

        :param name: the name of the collection to delete.
        :type name: str.
        :raises: ArangoCollectionDeleteError.
        """
        res = self._conn.delete("/_api/collection/{}".format(name))
        if res.status_code != 200:
            raise ArangoCollectionDeleteError(res)
        self._update_collection_cache()

    def rename_collection(self, name, new_name):
        """Rename the specified collection in this database.

        :param name: the name of the collection to rename.
        :type name: str.
        :param new_name: the new name for the collection.
        :type new_name: str.
        :raises: ArangoCollectionRenameError.
        """
        res = self._conn.put(
            "/_api/collection/{}/rename".format(name),
            data={"name": new_name}
        )
        if res.status_code != 200:
            raise ArangoCollectionRenameError(res)
        self._update_collection_cache()

    ##########################
    # Managing AQL Functions #
    ##########################

    def create_aql_function(self, name, code, **kwargs):
        data = {"name": name, "code": code}
        data.update(kwargs)
        res = self._conn.post("/_api/aqlfunction", data=data)
        if res.status_code not in (200, 201):
            raise ArangoAQLFunctionCreateError(res)

    def delete_aql_function(self, name, **kwargs):
        res = self._conn.delete(
            "/_api/aqlfunction/{}".format(name), data=kwargs
        )
        if res.status_code != 200:
            raise ArangoAQLFunctionDeleteError(res)

    ###############
    # AQL Queries #
    ###############

    def parse_query(self, query):
        self._query.parse(query)

    def execute_query(self, query, **kwargs):
        return self._query.execute(query, **kwargs)