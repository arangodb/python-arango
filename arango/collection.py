"""ArangoDB Collection."""

from arango.util import camelify, filter_keys
from arango.document import DocumentMixin
from arango.index import IndexMixin
from arango.aql import AQLMixin
from arango.client import ClientMixin
from arango.exceptions import (
    ArangoCollectionListError,
    ArangoCollectionCreateError,
    ArangoCollectionDeleteError,
    ArangoCollectionModifyError,
    ArangoCollectionCreateError

)


class Collection(ClientMixin, DocumentMixin, IndexMixin, AQLMixin):
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

    def __init__(self, name, protocol="http", host="localhost",
                 port=8529, db_name="_system"):
        self.name = name
        self.protocol = protocol
        self.host = host
        self.port = port
        self.db_name = db_name

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
            res = self._put(
                "/_api/collection/{}/properties".format(self.name),
                data={camelify(attr): value}
            )
            if res.status_code != 200:
                raise ArangoCollectionModifyError(res)
        else:
            super(Collection, self).__setattr__(attr, value)

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
        res = self._get("/_api/collection/{}/properties".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionPropertyError(res)
        return res.obj

    @property
    def count(self):
        """Return the number of documents in this collection.

        :returns: int.
        :raises: ArangoCollectionPropertyError.
        """
        res = self._get("/_api/collection/{}/count".format(self.name))
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
        res = self._get("/_api/collection/{}/figures".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionPropertyError(res)
        return res.obj["figures"]

    @property
    def revision(self):
        """Return the revision of this collection."""
        res = self._get("/_api/collection/{}/revision".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionPropertyError(res)
        return res.obj["revision"]

    def checksum(self, revision=False, data=False):
        """Return the checksum for this collection."""
        res = self._get(
            "/_api/collection/{}/checksum".format(self.name),
            params={"withRevision": revision, "withData": data}
        )
        if res.status_code != 200:
            raise ArangoCollectionPropertyError(res)
        return res.obj["checksum"]

    def truncate(self):
        """Remove all documents from this collection."""
        res = self._put("/_api/collection/{}/truncate".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionTruncateError(res)

    def load(self):
        """Load this collection into memory.

        :raises: ArangoCollectionLoadError
        """
        res = self._put("/_api/collection/{}/load".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionLoadError(res)

    def unload(self):
        """Unload this collection from memory.

        :raises: ArangoCollectionUnloadError
        """
        res = self._put("/_api/collection/{}/unload".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionUnloadError(res)

    def rotate_journal(self):
        """Rotate the journal of this collection.

        :raises: ArangoCollectionRotateJournalError
        """
        res = self._put("/_api/collection/{}/rotate".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionRotateJournalError(res)
