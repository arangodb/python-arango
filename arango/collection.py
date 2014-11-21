"""ArangoDB Collection."""

from arango.util import camelify
from arango.index import ArangoIndexMixin
from arango.client import ArangoClient
from arango.exceptions import *


class ArangoCollection(ArangoClient, ArangoIndexMixin):

    def __init__(self, url_prefix, name):
        self._url_prefix = url_prefix
        self.name = name

    def __len__(self):
        """Return the number of documents in this collection."""
        return self.count

    def __setattr__(self, attr, value):
        if attr == "wait_for_sync" or attr == "journal_size":
            res = self._put(
                "/_api/collection/{}/properties".format(self.name),
                data={camelify(attr): value}
            )
            if res.status_code != 200:
                raise ArangoCollectionModifyError(res)
        else:
            super(ArangoCollection, self).__setattr__(attr, value)

    @property
    def properties(self):
        """Return the properties of this collection."""
        res = self._get("/_api/collection/{}/properties".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionPropertyError(res)
        return res.obj

    @property
    def count(self):
        res = self._get("/_api/collection/{}/count".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionPropertyError(res)
        return res.obj["count"]

    @property
    def id(self):
        return self.properties["id"]

    @property
    def status(self):
        return self.properties["status"]

    @property
    def key_options(self):
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
            "/_api/collection/{}/checksum?withRevision={}?withData={}"
            .format(self.name, revision, data)
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
        """Load this collection into memory."""
        res = self._put("/_api/collection/{}/load".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionLoadError(res)

    def unload(self):
        """Unload this collection from memory."""
        res = self._put("/_api/collection/{}/unload".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionUnloadError(res)

    def rotate_journal(self):
        """Rotate the journal of this collection."""
        res = self._put("/_api/collection/{}/rotate".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionRotateJournalError(res)
