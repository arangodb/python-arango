"""ArangoDB Database."""


from arango.query import Query
from arango.collection import Collection
from arango.exceptions import *


class Database(object):
    """A wrapper around ArangoDB database API.

    :param str name: the name of this database
    :param Client client: the http client
    """

    def __init__(self, name, client):
        self.name = name
        self._client = client
        self._collection_cache = {}
        self._query = Query(self._client)

    def __getitem__(self, name):
        """Return the Collection object of the specified name.

        :param str name: the name of the collection
        :returns: Collection -- the requested collection
        :raises: TypeError, ArangoCollectionNotFound
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
                client=self._client
            )

    @property
    def properties(self):
        """Return all properties of this database.

        :returns: dict -- the database properties
        :raises: ArangoDatabasePropertyError
        """
        res = self._client.get("/_api/database/current")
        if res.status_code != 200:
            raise ArangoDatabasePropertyError(res)
        return res.obj["result"]

    @property
    def id(self):
        """Return the ID of this database.

        :returns: str -- the database ID
        :raises: ArangoDatabasePropertyError
        """
        return self.properties["id"]

    @property
    def path(self):
        """Return the file path of this database.

        :returns: str -- the path of this database
        :raises: ArangoDatabasePropertyError
        """
        return self.properties["path"]

    @property
    def is_system(self):
        """Return True if this is a system database, otherwise False.

        :returns: bool -- whether this is a system database or not
        :raises: ArangoDatabasePropertyError
        """
        return self.properties["isSystem"]

    @property
    def collections(self):
        """Return the names of the collections in this database.

        :returns: list -- list of collection names
        :raises: ArangoCollectionListError
        """
        res = self._client.get("/_api/collection")
        if res.status_code != 200:
            raise ArangoCollectionListError(res)
        return res.obj["names"]

    @property
    def aql_functions(self):
        """Return the AQL functions defined in this database.

        :returns: dict -- mapping of function names to its code
        :raises: ArangoAQLFunctionListError
        """
        res = self._client.get("/_api/aqlfunction")
        if res.status_code != 200:
            raise ArangoAQLFunctionListError(res)
        return {func["name"]: func["code"]for func in res.obj}

    def collection(self, name):
        """Return the Collection object of the specified name.

        :param str name: the name of the collection
        :returns: Collection -- the requested collection
        :raises: TypeError, ArangoCollectionNotFound
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

        :param str name: name of the new collection
        :param bool wait_for_sync: if True the collection waits for syncs to disk
        :param bool do_compact: whether or not the collection is compacted
        :param int journal_size: the maximal size of journal or datafile
        :param bool is_system: whether or not the collection is a system collection
        :param bool is_volatile: whether or not the collection is kept in memory only
        :param dict key_options: options for document key generation
        :param bool is_edge: whether or not the collection is an edge collection
        :raises: ArangoCollectionCreateError
        """
        data = {
            "name": name,
            "waitForSync": wait_for_sync,
            "doCompact": do_compact,
            "isSystem": is_system,
            "isVolatile": is_volatile,
            "type": 3 if is_edge else 2,
            "keyOptions": {} if key_options is None else key_options,
        }
        if journal_size:
            data["journalSize"] = journal_size

        res = self._client.post("/_api/collection", data=data)
        if res.status_code != 200:
            raise ArangoCollectionCreateError(res)
        self._update_collection_cache()

    def delete_collection(self, name):
        """Delete the specified collection in this database.

        :param str name: the name of the collection to delete
        :raises: ArangoCollectionDeleteError
        """
        res = self._client.delete("/_api/collection/{}".format(name))
        if res.status_code != 200:
            raise ArangoCollectionDeleteError(res)
        self._update_collection_cache()

    def rename_collection(self, name, new_name):
        """Rename the specified collection in this database.

        :param str name: the name of the collection to rename
        :param str new_name: the new name for the collection
        :raises: ArangoCollectionRenameError
        """
        res = self._client.put(
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
        res = self._client.post("/_api/aqlfunction", data=data)
        if res.status_code not in (200, 201):
            raise ArangoAQLFunctionCreateError(res)

    def delete_aql_function(self, name, **kwargs):
        res = self._client.delete(
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