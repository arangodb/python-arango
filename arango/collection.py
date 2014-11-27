"""ArangoDB Collection."""

from arango.util import camelify, filter_keys
from arango.index import IndexMixin
from arango.aql import AQLMixin
from arango.query import QueryMixin
from arango.connection import Connection
from arango.exceptions import (
    ArangoDocumentGetError,
    ArangoDocumentCreateError,
    ArangoDocumentDeleteError,
    ArangoDocumentPatchError,
    ArangoDocumentReplaceError,
    ArangoDocumentInvalidError,
    ArangoCollectionModifyError,
    ArangoCollectionPropertyError,
    ArangoCollectionLoadError,
    ArangoCollectionUnloadError,
    ArangoCollectionTruncateError,
    ArangoCollectionRotateJournalError
)


class Collection(IndexMixin, QueryMixin):
    """ArangoDB Collection.

    :param name: the name of this collection.
    :param type: str.
    :param protocol: the internet transfer protocol (default: http).
    :type protocol: str.
    :param host: ArangoDB host (default: localhost).
    :type host: str.
    :param port: ArangoDB port (default: 8529).
    :type port: int.
    :param db_name: the name of the database (default: _system).
    :type db_name: str.
    """

    def __init__(self, name, client):
        self.name = name
        self._conn = client

    def __len__(self):
        """Return the number of documents in this collection."""
        return self.count

    def __iter__(self):
        """Iterate through the documents in this collection."""
        return self.execute_query(
            "FOR d in {} RETURN d".format(self.name)
        )

    def __setattr__(self, attr, value):
        """Modify the properties of this collection.

        Only the values of ``wait_for_sync`` and ``journal_size``
        properties can be changed.
        """
        if attr == "wait_for_sync" or attr == "journal_size":
            res = self._conn.put(
                "/_api/collection/{}/properties".format(self.name),
                data={camelify(attr): value}
            )
            if res.status_code != 200:
                raise ArangoCollectionModifyError(res)
        else:
            super(Collection, self).__setattr__(attr, value)

    def __getitem__(self, key):
        """Return the document from this collection.

        :param key: the document key.
        :type key: str.
        :returns: dict -- the requested document.
        :raises: TypeError.
        """
        if not isinstance(key, str):
            raise TypeError("Expecting a str.")
        return self.get(key)

    def __setitem__(self, key, doc):
        """Write the document into this collection.

        :param key: the document key.
        :type key: str.
        """

    @property
    def _url_prefix(self):
        """Return the URL prefix for this collection."""
        return "{protocol}://{host}:{port}/_db/{db_name}".format(
            protocol=self.protocol,
            host=self.host,
            port=self.port,
            db_name=self.db_name
        )

    @property
    def properties(self):
        """Return the properties of this collection.

        :returns: dict.
        :raises: ArangoCollectionPropertyError.
        """
        res = self._conn.get("/_api/collection/{}/properties".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionPropertyError(res)
        return res.obj

    @property
    def count(self):
        """Return the number of documents in this collection.

        :returns: int.
        :raises: ArangoCollectionPropertyError.
        """
        res = self._conn.get("/_api/collection/{}/count".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionPropertyError(res)
        return res.obj["count"]

    @property
    def id(self):
        """Return the ID of this collection.

        :returns: str.
        :raises: ArangoCollectionPropertyError.
        """
        return self.properties["id"]

    @property
    def status(self):
        """Return the status of this collection.

        :returns: str.
        :raises: ArangoCollectionPropertyError.
        """
        return self.properties["status"]

    @property
    def key_options(self):
        """Return this collection's key options.

        :returns: dict.
        :raises: ArangoCollectionPropertyError.
        """
        return self.properties["keyOptions"]

    @property
    def wait_for_sync(self):
        return self.properties["waitForSync"]

    @property
    def journal_size(self):
        return self.properties["journalSize"]

    @property
    def is_volatile(self):
        return self.properties["isVolatile"]

    @property
    def is_system(self):
        return self.properties["isSystem"]

    @property
    def is_edge(self):
        return self.properties["type"] == 3

    @property
    def figures(self):
        """Return the statistics of this collection."""
        res = self._conn.get("/_api/collection/{}/figures".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionPropertyError(res)
        return res.obj["figures"]

    @property
    def revision(self):
        """Return the revision of this collection."""
        res = self._conn.get("/_api/collection/{}/revision".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionPropertyError(res)
        return res.obj["revision"]

    def checksum(self, revision=False, data=False):
        """Return the checksum for this collection."""
        res = self._conn.get(
            "/_api/collection/{}/checksum".format(self.name),
            params={"withRevision": revision, "withData": data}
        )
        if res.status_code != 200:
            raise ArangoCollectionPropertyError(res)
        return res.obj["checksum"]

    def truncate(self):
        """Remove all documents from this collection.

        :raises: ArangoCollectionTruncateError
        """
        res = self._conn.put("/_api/collection/{}/truncate".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionTruncateError(res)

    def load(self):
        """Load this collection into memory.

        :raises: ArangoCollectionLoadError
        """
        res = self._conn.put("/_api/collection/{}/load".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionLoadError(res)

    def unload(self):
        """Unload this collection from memory.

        :raises: ArangoCollectionUnloadError
        """
        res = self._conn.put("/_api/collection/{}/unload".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionUnloadError(res)

    def rotate_journal(self):
        """Rotate the journal of this collection.

        :raises: ArangoCollectionRotateJournalError
        """
        res = self._conn.put("/_api/collection/{}/rotate".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionRotateJournalError(res)

    def get(self, key, rev=None, match=True):
        """Return the document of the given key.

        :param key: the document key.
        :type key: str.
        :param rev: the document revision to check against (optional).
        :type rev: str.
        :param match: if True ``rev`` must match, else ``rev`` must differ.
        :type match: bool.
        :returns: dict -- the requested document.
        :raises: ArangoDocumentGetError.
        """
        headers = {"If-Match" if match else "If-None-Match": rev} if rev else {}
        res = self._conn.get(
            "/_api/document/{}/{}".format(self.name, key),
            headers=headers
        )
        if res.status_code != 200:
            raise ArangoDocumentGetError(res)
        return res.obj

    def create(self, doc, wait_for_sync=False):
        """Create the given document in this collection.

        :param doc: the document to create in this collection.
        :type doc: dict.
        :param wait_for_sync: block until the document is synced to disk.
        :type wait_for_sync: bool.
        :raises: ArangoDocumentCreateError.
        """
        res = self._conn.post(
            "/_api/document".format(self.name),
            data=doc,
            params = {
                "collection": self.name,
                "waitForSync": wait_for_sync,
            }
        )
        if res.status_code != 201 and res.status_code != 202:
            raise ArangoDocumentCreateError(res)
        return filter_keys(res.obj, ["error"])

    def replace(self, doc, ignore_rev=True, wait_for_sync=False):
        """Replace the document in this collection.

        :param doc: the new document to replace the one in this collection.
        :type doc: dict.
        :param ignore_rev: ignore the revision of the document ("_rev") if present.
        :type ignore_rev: bool.
        :param wait_for_sync: block until the document is synced to disk.
        :type wait_for_sync: bool.
        :raises: ArangoDocumentReplaceError.
        """
        if "_key" not in doc:
            raise ArangoDocumentInvalidError("'_key' missing")
        res = self._conn.put(
            "/_api/document/{}/{}".format(self.name, doc["_key"]),
            data=doc,
            params={
                "waitForSync": wait_for_sync,
                "rev": doc.get("_rev"),
                "policy": "last" if ignore_rev else "error",
            }
        )
        if res.status_code != 201 and res.status_code != 202:
            raise ArangoDocumentReplaceError(res)
        return filter_keys(res.obj, ["error"])

    def patch(self, doc, ignore_rev=True, keep_none=True,
              wait_for_sync=False):
        if "_key" not in doc:
            raise ArangoDocumentInvalidError("'_key' missing")
        res = self._conn.patch(
            "/_api/document/{}/{}".format(self.name, doc["_key"]),
            data=doc,
            params={
                "waitForSync": wait_for_sync,
                "rev": doc.get("_rev"),
                "policy": "last" if ignore_rev else "error",
                "keepNull": keep_none,
            }
        )
        if res.status_code != 201 and res.status_code != 202:
            raise ArangoDocumentPatchError(res)
        return filter_keys(res.obj, ["error"])

    def delete(self, key, ignore_rev=True, wait_for_sync=False):
        res = self._conn.delete(
            "/_api/document/{}/{}".format(self.name, key),
            params={
                "waitForSync": wait_for_sync,
                "rev": doc.get("_rev"),
                "policy": "last" if ignore_rev else "error",
            }
        )
        if res.status_code != 200 and res.status_code != 202:
            raise ArangoDocumentDeleteError(res)
        return filter_keys(res.obj, ["error"])
