"""ArangoDB Collection."""

from arango.utils import camelify, filter_keys
from arango.query import Query
from arango.exceptions import  *


class Collection(object):
    """A wrapper around ArangoDB collection specific API.

    :param name: the name of this collection
    :type name: str
    :param client: ArangoDB http client object
    :type client: arango.client.Client
    """

    collection_status = {
        1: "new",
        2: "unloaded",
        3: "loaded",
        4: "unloading",
        5: "deleted",
    }

    def __init__(self, name, client):
        self.name = name
        self._client = client
        self._query = Query(self._client)
        self._type = "edge" if self.is_edge else "document"

    def __len__(self):
        """Return the number of documents in this collection."""
        return self.count

    def __iter__(self):
        """Iterate through the documents in this collection."""
        return self._query.execute(
            "FOR d in {} RETURN d".format(self.name)
        )

    def __setattr__(self, attr, value):
        """Modify the properties of this collection.

        Only ``wait_for_sync`` and ``journal_size`` are mutable.
        """
        if attr in {"wait_for_sync", "journal_size"}:
            res = self._client.put(
                "/_api/collection/{}/properties".format(self.name),
                data={camelify(attr): value}
            )
            if res.status_code != 200:
                raise ArangoCollectionModifyError(res)
        else:
            super(Collection, self).__setattr__(attr, value)

    def __getitem__(self, key):
        """Return the document from this collection.

        :param key: the document key
        :type key: str
        :returns: the requested document
        :rtype: dict
        :raises: TypeError
        """
        if not isinstance(key, str):
            raise TypeError("Expecting a str.")
        return self.get(key)

    def __setitem__(self, key, data):
        """Write the document into this collection.

        First attempt to add the document. If the document with the
        specified key exists already attempt to replace the document.

        If ``_key`` is provided in ``data``, its value is overwritten by
        the value of parameter ``key``.

        :param key: the document key
        :type key: str
        :param data: the document body
        :type data: dict
        :raises: TypeError, ArangoDocumentCreateError
        """
        if not isinstance(key, str):
            raise TypeError("Excepting a str for the key.")
        if not isinstance(data, dict):
            raise TypeError("Expecting a dict for the value.")
        data["_key"] = key
        try:
            self.add(data)
        except ArangoDocumentCreateError as err:
            if err.status_code == 409:
                self.replace(data)

    @property
    def all(self):
        """Return the list of all documents/edges in this collection.

        :returns: all documents/edges
        :rtype: list
        """
        return list(self.__iter__())

    @property
    def properties(self):
        """Return the properties of this collection.

        :returns: the collection's id, status, key_options etc.
        :rtype: dict
        :raises: ArangoCollectionPropertyError
        """
        res = self._client.get(
            "/_api/collection/{}/properties".format(self.name)
        )
        if res.status_code != 200:
            raise ArangoCollectionPropertyError(res)
        return res.obj

    @property
    def count(self):
        """Return the number of documents in this collection.

        :returns: the number of documents in this collection
        :rtype: int
        :raises: ArangoCollectionPropertyError
        """
        res = self._client.get("/_api/collection/{}/count".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionPropertyError(res)
        return res.obj["count"]

    @property
    def id(self):
        """Return the ID of this collection.

        :returns: the ID of this collection
        :rtype: str
        :raises: ArangoCollectionPropertyError
        """
        return self.properties["id"]

    @property
    def status(self):
        """Return the status of this collection.

        :returns: the collection status
        :rtype: str
        :raises: ArangoCollectionPropertyError, ArangoCollectionCorruptedError
        """
        status_num = self.properties["status"]
        if status_num not in self.collection_status:
            raise ArangoCollectionCorruptedError(
                "Got unknown status number: {}".format(status_num)
            )
        return self.collection_status[status_num]

    @property
    def key_options(self):
        """Return this collection's key options.

        :returns: the key options
        :rtype: dict
        :raises: ArangoCollectionPropertyError
        """
        return self.properties["keyOptions"]

    @property
    def wait_for_sync(self):
        """Return True if this collection waits for changes to sync to disk.

        :returns: True if collection waits for sync, False otherwise
        :rtype: bool
        :raises: ArangoCollectionPropertyError
        """
        return self.properties["waitForSync"]

    @property
    def journal_size(self):
        """Return the journal size of this collection.

        :returns: the journal size of this collection
        :rtype: str
        :raises: ArangoCollectionPropertyError
        """
        return self.properties["journalSize"]

    @property
    def is_volatile(self):
        """Return True if this collection is kept in memory and not persistent.

        :returns: True if the collection is volatile, False otherwise
        :rtype: bool
        :raises: ArangoCollectionPropertyError
        """
        return self.properties["isVolatile"]

    @property
    def is_system(self):
        """Return True if this collection is a system Collection.

        :returns: True if system collection, False otherwise
        :rtype: bool
        :raises: ArangoCollectionPropertyError
        """
        return self.properties["isSystem"]

    @property
    def is_edge(self):
        """Return True if this collection is a system Collection.

        :returns: True if edge collection, False otherwise
        :rtype: bool
        :raises: ArangoCollectionPropertyError
        """
        return self.properties["type"] == 3

    @property
    def figures(self):
        """Return the statistics of this collection.

        :returns: the statistics of this collection
        :rtype: dict
        :raises: ArangoCollectionPropertyError
        """
        res = self._client.get("/_api/collection/{}/figures".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionPropertyError(res)
        return res.obj["figures"]

    @property
    def revision(self):
        """Return the revision of this collection.

        :returns: the collection revision (etag)
        :rtype: str
        :raises: ArangoCollectionPropertyError
        """
        res = self._client.get("/_api/collection/{}/revision".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionPropertyError(res)
        return res.obj["revision"]

    def truncate(self):
        """Remove all documents from this collection.

        :raises: ArangoCollectionTruncateError
        """
        res = self._client.put("/_api/collection/{}/truncate".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionTruncateError(res)

    def load(self):
        """Load this collection into memory.

        :raises: ArangoCollectionLoadError
        """
        res = self._client.put("/_api/collection/{}/load".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionLoadError(res)

    def unload(self):
        """Unload this collection from memory.

        :raises: ArangoCollectionUnloadError
        """
        res = self._client.put("/_api/collection/{}/unload".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionUnloadError(res)

    def rotate_journal(self):
        """Rotate the journal of this collection.

        :raises: ArangoCollectionRotateJournalError
        """
        res = self._client.put("/_api/collection/{}/rotate".format(self.name))
        if res.status_code != 200:
            raise ArangoCollectionRotateJournalError(res)

    def checksum(self, with_rev=False, with_data=False):
        """Return the checksum for this collection.

        :param with_rev: include the revision in checksum calculation
        :type with_rev: bool
        :param with_data: include the data in checksum calculation
        :type with_data: bool
        :returns: the checksum
        :rtype: str
        :raises: ArangoCollectionGetChecksumError
        """
        res = self._client.get(
            "/_api/collection/{}/checksum".format(self.name),
            params={"withRevision": with_rev, "withData": with_data}
        )
        if res.status_code != 200:
            raise ArangoCollectionGetChecksumError(res)
        return res.obj["checksum"]

    ############################
    # Handling Documents/Edges #
    ############################

    def get(self, key, rev=None, match=True):
        """Return the document/edge of the given key.

        If the document revision ``rev`` is specified, it is compared against
        the revision of the retrieved document. If ``match`` is set to True
        and the revisions do NOT match, or if ``match is set to False and the
        revisions DO match, an ``ArangoRevisionMismatchError`` is thrown.

        :param key: the document/edge key
        :type key: str
        :param rev: the document/edge revision
        :type rev: str
        :param match: whether the revision must match or not
        :type match: bool
        :returns: the requested document/edge.
        :rtype: dict
        :raises:
            ArangoRevisionMisMatchError,
            ArangoDocumentGetError,
            ArangoEdgeGetError
        """
        res = self._client.get(
            "/_api/{}/{}/{}".format(self._type, self.name, key),
            headers={
                "If-Match" if match else "If-None-Match": rev
            } if rev else {}
        )
        if res.status_code == 412:
            raise ArangoRevisionMismatchError(res)
        elif res.status_code != 200:
            if self.is_edge:
                raise ArangoEdgeGetError(res)
            raise ArangoDocumentGetError(res)

        return res.obj

    def add(self, data, wait_for_sync=False):
        """Create the given document/edge in this collection.

        If ``data`` contains ``_key`` attribute, use its value as the key
        of the document. If this collection is an edge collection, ``data`` must
        contain the ``_from`` and ``_to`` attributes with valid document handles
        as values.

        :param data: the body of the new document/edge
        :type data: dict
        :param wait_for_sync: wait for add to sync to disk
        :type wait_for_sync: bool
        :returns: the id, rev and key of the new document/edge
        :rtype: bool
        :raises: ArangoDocumentCreateError, ArangoEdgeAddError
        """
        if self.is_edge:
            if "_from" not in data:
                raise ArangoEdgeInvalidError("the '_from' key is missing")
            if "_to" not in data:
                raise ArangoEdgeInvalidError("the '_to' key is missing")
        params = {
            "collection": self.name,
            "waitForSync": wait_for_sync,
        }
        if self.is_edge:
            params["from"] = data["_from"]
            params["to"] = data["_to"]

        res = self._client.post(
            "/_api/{}".format(self._type),
            data=data,
            params=params
        )
        if res.status_code not in {201, 202}:
            if self.is_edge:
                raise ArangoEdgeAddError(res)
            raise ArangoDocumentCreateError(res)

        return filter_keys(res.obj, ["error"])

    def replace(self, data, wait_for_sync=False):
        """Replace the document/edge in this collection.

        If ``data`` contains the ``_rev`` attribute, its value is compared
        against the revision of the target document/edge. If there is a
        mismatch between the values an ``ArangoRevisionMismatchError`` is
        thrown.

        The ``_from`` and ``_to`` attributes are immutable, and they are
        ignored if present in ``data``.

        :param data: the body of the new document/edge
        :rtype data: dict
        :param wait_for_sync: wait for the replace to sync to disk
        :type wait_for_sync: bool
        :returns: the id, rev and key of the new document/edge
        :rtype: dict
        :raises:
            ArangoRevisionMismatchError,
            ArangoDocumentReplaceError,
            ArangoEdgeReplaceError
        """
        if "_key" not in data:
            if self.is_edge:
                raise ArangoEdgeInvalidError("'_key' is missing")
            raise ArangoDocumentInvalidError("'_key' is missing")

        params = {"waitForSync": wait_for_sync}
        if "_rev" in data:
            params["rev"] = data["_rev"]
            params["policy"] = "error"

        res = self._client.put(
            "/_api/{}/{}/{}".format(self._type, self.name, data["_key"]),
            data=data,
            params=params
        )
        if res.status_code == 412:
            raise ArangoRevisionMismatchError(res)
        elif res.status_code not in {201, 202}:
            if self.is_edge:
                raise ArangoEdgeReplaceError(res)
            raise ArangoDocumentReplaceError(res)

        return filter_keys(res.obj, ["error"])

    def patch(self, data, keep_none=True, wait_for_sync=False):
        """Patch the document/edge in this collection.

        If ``data`` contains the ``_rev`` attribute, its value is compared
        against the revision of the target document/edge. If there is a
        mismatch between the values, an ``ArangoRevisionMismatchError`` is
        thrown.

        If ``keep_none`` is set to True, then attributes with None as values
        are retained. Otherwise they are removed from the document/edge.

        The ``_from`` and ``_to`` attributes are immutable, and they are
        ignored if provided in ``data``.

        :param data: the body of the document/edge to patch
        :type data: dict
        :param keep_none: whether to keep the items with value None
        :type keep_none: bool
        :param wait_for_sync: wait for the replace to sync to disk
        :type wait_for_sync: bool
        :returns: the id, rev and key of the new document/edge
        :rtype: dict
        :raises:
            ArangoRevisionMismatchError,
            ArangoDocumentPatchError,
            ArangoEdgeUpdateError
        """
        if "_key" not in data:
            if self.is_edge:
                raise ArangoEdgeInvalidError("'_key' is missing")
            raise ArangoDocumentInvalidError("'_key' is missing")

        params = {
            "waitForSync": wait_for_sync,
            "keepNull": keep_none
        }
        if "_rev" in data:
            params["rev"] = data["_rev"]
            params["policy"] = "error"

        res = self._client.patch(
            "/_api/{}/{}/{}".format(self._type, self.name, data["_key"]),
            data=data,
            params=params
        )
        if res.status_code == 412:
            raise ArangoRevisionMismatchError(res)
        elif res.status_code not in {201, 202}:
            if self.is_edge:
                raise ArangoEdgeUpdateError(res)
            raise ArangoDocumentPatchError(res)

        return filter_keys(res.obj, ["error"])

    def delete(self, key, rev=None, wait_for_sync=False):
        """Delete the document/edge in this collection.

        If the document revision ``rev`` is specified, it is compared against
        the revision of the target document. If there is a mismatch between
        the values, an ArangoRevisionMismatchError is thrown.

        :param key: the key of the document/edge to delete
        :type key: str
        :param wait_for_sync: wait for the delete to sync to disk
        :type wait_for_sync: bool
        :raises:
            ArangoRevisionMismatchError,
            ArangoDocumentDeleteError,
            ArangoEdgeRemoveError
        """
        params = {"waitForSync": wait_for_sync}
        if rev is not None:
            params["rev"] = rev
            params["policy"] = "error"

        res = self._client.delete(
            "/_api/{}/{}/{}".format(self._type, self.name, key),
            params=params
        )
        if res.status_code not in {200, 202}:
            if self.is_edge:
                raise ArangoEdgeRemoveError(res)
            raise ArangoDocumentPatchError(res)

    def bulk_import(self, data, complete=True, details=True):
        """Import documents/edges into this collection in bulk.

        :param data: list of documents/edges (dict) to import
        :type data: list
        :param complete: entire import fails if any document/edge is invalid
        :type complete: bool
        :param details: return details about invalid documents/edges
        :type details: bool
        :returns: the bulk import results
        :rtype: dict
        :raises: ArangoCollectionBulkImportError
        """
        res = self._client.post(
            "_api/import",
            data=data,
            params={
                "type": self._type,
                "collection": self.name,
                "complete": complete,
                "details": details
            }
        )
        if res.status_code != 201:
            raise ArangoCollectionBulkImportError(res)
        del res.obj["error"]
        return res.obj

    ####################
    # Handling Indexes #
    ####################

    @property
    def indexes(self):
        """Return the details of this collection's indexes.

        :returns: the indexes of this collection
        :rtype: dict
        :raises: ArangoIndexListError
        """
        res = self._client.get(
            "/_api/index?collection={}".format(self.name)
        )
        if res.status_code != 200:
            raise ArangoIndexListError(res)
        return {
            index_id.split("/", 1)[1]: details for
            index_id, details in res.obj["identifiers"].items()
        }

    def _add_index(self, data):
        """Helper method for adding indexes."""
        res = self._client.post(
            "/_api/index?collection={}".format(self.name),
            data=data
        )
        if res.status_code not in {200, 201}:
            raise ArangoIndexAddError(res)

    def add_hash_index(self, fields, unique=None):
        """Add a new hash index to this collection.

        :param fields: the attribute paths to index
        :type fields: list
        :param unique: whether or not the index is unique
        :type unique: bool or None
        :raises: ArangoIndexAddError
        """
        data = {"type": "hash", "fields": fields}
        if unique is not None:
            data["unique"] = unique
        self._add_index(data)

    def add_cap_constraint(self, size=None, byte_size=None):
        """Add a cap constraint to this collection.

        :param size: the number for documents allowed in this collection
        :type size: int or None
        :param byte_size: the max size of the active document data (> 16384)
        :type byte_size: int or None
        :raises: ArangoIndexAddError
        """
        data = {"type": "cap"}
        if size is not None:
            data["size"] = size
        if byte_size is not None:
            data["byteSize"] = byte_size
        self._add_index(data)

    def add_skiplist_index(self, fields, unique=None):
        """Add a new skiplist index to this collection.

        A skiplist index is used to find ranges of documents (e.g. time).

        :param fields: the attribute paths to index
        :type fields: list
        :param unique: whether or not the index is unique
        :type unique: bool or None
        :raises: ArangoIndexAddError
        """
        data = {"type": "skiplist", "fields": fields}
        if unique is not None:
            data["unique"] = unique
        self._add_index(data)

    def add_geo_index(self, fields, geo_json=None, unique=None,
                      ignore_none=None):
        """Add a geo index to this collection

        If ``fields`` is a list with one attribute path ``location``, then
        a geo-spatial index on all documents is created using ``location`` as
        path to the coordinates. The value of the attribute must be a list
        with at least two double values. The list must contain the latitude
        (first value) and the longitude (second value). All documents without
        the attribute paths or with invalid values are ignored.

        If it is a list with two attribute paths ``latitude`` and ``longitude``,
        then a geo-spatial index on all documents is created using the two
        attributes (their values must be doubles). All documents without the
        attribute paths or with invalid values are ignored.

        :param fields: the attribute paths to index (length must be <= 2)
        :type fields: list
        :param geo_json: whether or not the order is longitude -> latitude
        :type geo_json: bool or None
        :param unique: whether or not to create a geo-spatial constraint
        :type unique: bool or None
        :param ignore_none: ignore docs with None in latitude/longitude
        :type ignore_non: bool or None
        :raises: ArangoIndexAddError
        """
        data = {"type": "geo", "fields": fields}
        if geo_json is not None:
            data["geoJson"] = geo_json
        if unique is not None:
            data["unique"] = unique
        if ignore_none is not None:
            data["ignore_none"] = ignore_none
        self._add_index(data)

    def add_fulltext_index(self, fields, min_length=None):
        """Add a fulltext index to this collection.

        A fulltext index can be used to find words, or prefixes of words inside
        documents. A fulltext index can be set on one attribute only, and will
        index all words contained in documents that have a textual value in
        this attribute. Only words with a (specifiable) minimum length are
        indexed. Word tokenization is done using the word boundary analysis
        provided by libicu, which is taking into account the selected language
        provided at server start. Words are indexed in their lower-cased form.
        The index supports complete match queries (full words) and prefix
        queries.

        :param fields: the attribute paths to index (length must be 1)
        :type fields: list
        :param min_length: minimum character length of words to index
        :type min_length: int
        :raises: ArangoIndexAddError
        """
        data = {"type": "fulltext", "fields": fields}
        if min_length is not None:
            data["minLength"] = min_length
        self._add_index(data)

    def remove_index(self, index_id):
        """Delete an index from this collection.

        :param index_id: the ID of the index to delete
        :type index_id: str
        :raises: ArangoIndexRemoveError
        """
        res = self._client.delete(
            "/_api/index/{}/{}".format(self.name, index_id)
        )
        if res.status_code != 200:
            raise ArangoIndexRemoveError(res)
