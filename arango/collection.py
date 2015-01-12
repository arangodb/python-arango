"""ArangoDB Collection."""

import json

from arango.utils import camelify, uncamelify, filter_keys
from arango.exceptions import *
from arango.cursor import CursorFactory


class Collection(CursorFactory):
    """A wrapper around ArangoDB collection specific API.

    :param name: the name of this collection
    :type name: str
    :param api: ArangoDB API object
    :type api: arango.api.ArangoAPI
    """

    COLLECTION_STATUS = {
        1: "new",
        2: "unloaded",
        3: "loaded",
        4: "unloading",
        5: "deleted",
    }

    def __init__(self, name, api):
        super(Collection, self).__init__(api)
        self.name = name
        self._api = api
        self._type = "edge" if self.is_edge else "document"

    def __iter__(self):
        """Iterate through the documents in this collection."""
        return self.all()

    def __len__(self):
        """Return the number of documents in this collection."""
        return self.count

    def __setattr__(self, attr, value):
        """Modify the properties of this collection.

        Only ``wait_for_sync`` and ``journal_size`` are mutable.
        """
        if attr in {"wait_for_sync", "journal_size"}:
            res = self._api.put(
                "/_api/collection/{}/properties".format(self.name),
                data={camelify(attr): value}
            )
            if res.status_code != 200:
                raise CollectionModifyError(res)
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
        return self.get_document(key)

    def __contains__(self, key):
        """Return True if the document exists in this collection.

        :param key: the document key
        :type key: str
        :returns: True if the document exists, else False
        :rtype: bool
        :raises: DocumentGetError
        """
        return self.contains(key)

    @property
    def count(self):
        """Return the number of documents present in this collection.

        :returns: the number of documents
        :rtype: int
        :raises: CollectionPropertyError
        """
        res = self._api.get(
            "/_api/collection/{}/count".format(self.name)
        )
        if res.status_code != 200:
            raise CollectionPropertyError(res)
        return res.obj["count"]

    @property
    def properties(self):
        """Return the properties of this collection.

        :returns: the collection's id, status, key_options etc.
        :rtype: dict
        :raises: CollectionPropertyError
        """
        res = self._api.get(
            "/_api/collection/{}/properties".format(self.name)
        )
        if res.status_code != 200:
            raise CollectionPropertyError(res)
        return {
            "id": res.obj["id"],
            "name": res.obj["name"],
            "is_edge": res.obj["type"] == 3,
            "status": self.COLLECTION_STATUS.get(
                res.obj["status"],
                "corrupted ({})".format(res.obj["status"])
            ),
            "do_compact": res.obj["doCompact"],
            "is_system": res.obj["isSystem"],
            "is_volatile": res.obj["isVolatile"],
            "journal_size": res.obj["journalSize"],
            "wait_for_sync": res.obj["waitForSync"],
            "key_options": uncamelify(res.obj["keyOptions"])
        }

    @property
    def id(self):
        """Return the ID of this collection.

        :returns: the ID of this collection
        :rtype: str
        :raises: CollectionPropertyError
        """
        return self.properties["id"]

    @property
    def status(self):
        """Return the status of this collection.

        :returns: the collection status
        :rtype: str
        :raises: CollectionPropertyError
        """
        return self.properties["status"]

    @property
    def key_options(self):
        """Return this collection's key options.

        :returns: the key options of this collection
        :rtype: dict
        :raises: CollectionPropertyError
        """
        return self.properties["key_options"]

    @property
    def wait_for_sync(self):
        """Return True if this collection waits for changes to sync to disk.

        :returns: True if collection waits for sync, False otherwise
        :rtype: bool
        :raises: CollectionPropertyError
        """
        return self.properties["wait_for_sync"]

    @property
    def journal_size(self):
        """Return the journal size of this collection.

        :returns: the journal size of this collection
        :rtype: str
        :raises: CollectionPropertyError
        """
        return self.properties["journal_size"]

    @property
    def is_volatile(self):
        """Return True if this collection is kept in memory and not persistent.

        :returns: True if the collection is volatile, False otherwise
        :rtype: bool
        :raises: CollectionPropertyError
        """
        return self.properties["is_volatile"]

    @property
    def is_system(self):
        """Return True if this collection is a system Collection.

        :returns: True if system collection, False otherwise
        :rtype: bool
        :raises: CollectionPropertyError
        """
        return self.properties["is_system"]

    @property
    def is_edge(self):
        """Return True if this collection is a system Collection.

        :returns: True if edge collection, False otherwise
        :rtype: bool
        :raises: CollectionPropertyError
        """
        return self.properties["is_edge"]

    @property
    def do_compact(self):
        """Return True if this collection is compacted.

        :returns: True if collection is compacted, False otherwise
        :rtype: bool
        :raises: CollectionPropertyError
        """
        return self.properties["do_compact"]

    @property
    def figures(self):
        """Return the statistics of this collection.

        :returns: the statistics of this collection
        :rtype: dict
        :raises: CollectionPropertyError
        """
        res = self._api.get(
            "/_api/collection/{}/figures".format(self.name)
        )
        if res.status_code != 200:
            raise CollectionPropertyError(res)
        return uncamelify(res.obj["figures"])

    @property
    def revision(self):
        """Return the revision of this collection.

        :returns: the collection revision (etag)
        :rtype: str
        :raises: CollectionPropertyError
        """
        res = self._api.get(
            "/_api/collection/{}/revision".format(self.name)
        )
        if res.status_code != 200:
            raise CollectionPropertyError(res)
        return res.obj["revision"]

    def load(self):
        """Load this collection into memory.

        :returns: the status of the collection
        :rtype: str
        :raises: CollectionLoadError
        """
        res = self._api.put(
            "/_api/collection/{}/load".format(self.name)
        )
        if res.status_code != 200:
            raise CollectionLoadError(res)
        return self.COLLECTION_STATUS.get(
            res.obj["status"],
            "corrupted ({})".format(res.obj["status"])
        )

    def unload(self):
        """Unload this collection from memory.

        :returns: the status of the collection
        :rtype: str
        :raises: CollectionUnloadError
        """
        res = self._api.put(
            "/_api/collection/{}/unload".format(self.name)
        )
        if res.status_code != 200:
            raise CollectionUnloadError(res)
        return self.COLLECTION_STATUS.get(
            res.obj["status"],
            "corrupted ({})".format(res.obj["status"])
        )

    def rotate_journal(self):
        """Rotate the journal of this collection.

        :raises: CollectionRotateJournalError
        """
        res = self._api.put(
            "/_api/collection/{}/rotate".format(self.name)
        )
        if res.status_code != 200:
            raise CollectionRotateJournalError(res)
        return res.obj["result"]

    def checksum(self, with_rev=False, with_data=False):
        """Return the checksum of this collection.

        :param with_rev: include the revision in the checksum calculation
        :type with_rev: bool
        :param with_data: include the data in the checksum calculation
        :type with_data: bool
        :returns: the checksum
        :rtype: int
        :raises: CollectionGetChecksumError
        """
        res = self._api.get(
            "/_api/collection/{}/checksum".format(self.name),
            params={"withRevision": with_rev, "withData": with_data}
        )
        if res.status_code != 200:
            raise CollectionGetChecksumError(res)
        return res.obj["checksum"]

    def truncate(self):
        """Remove all documents from this collection.

        :raises: CollectionTruncateError
        """
        res = self._api.put(
            "/_api/collection/{}/truncate".format(self.name)
        )
        if res.status_code != 200:
            raise CollectionTruncateError(res)

    def contains(self, key):
        """Return True if the document exists in this collection.

        :param key: the document key
        :type key: str
        :returns: True if the document exists, else False
        :rtype: bool
        :raises: DocumentGetError
        """
        res = self._api.head(
            "/_api/{}/{}/{}".format(self._type, self.name, key)
        )
        if res.status_code == 200:
            return True
        elif res.status_code == 404:
            return False
        else:
            raise DocumentGetError(res)

    ######################
    # Handling Documents #
    ######################

    def get_document(self, key, rev=None, match=True):
        """Return the document of the given key.

        If the document revision ``rev`` is specified, it is compared
        against the revision of the retrieved document. If ``match`` is set
        to True and the revisions do NOT match, or if ``match`` is set to
        False and the revisions DO match, ``RevisionMismatchError`` is thrown.

        :param key: the key of the document to retrieve
        :type key: str
        :param rev: the document revision is compared against this value
        :type rev: str or None
        :param match: whether or not the revision should match
        :type match: bool
        :returns: the requested document or None if not found
        :rtype: dict or None
        :raises: RevisionMismatchError, DocumentGetError
        """
        res = self._api.get(
            "/_api/{}/{}/{}".format(self._type, self.name, key),
            headers={
                "If-Match" if match else "If-None-Match": rev
            } if rev else {}
        )
        if res.status_code in {412, 304}:
            raise RevisionMismatchError(res)
        elif res.status_code == 404:
            return None
        elif res.status_code != 200:
            raise DocumentGetError(res)
        return res.obj

    def add_document(self, data, wait_for_sync=False, _batch=False):
        """Add the new document to this collection.

        If ``data`` contains the ``_key`` key, its value must be free.
        If this collection is an edge collection, ``data`` must contain the
        ``_from`` and ``_to`` keys with valid vertex IDs as their values.

        :param data: the body of the new document
        :type data: dict
        :param wait_for_sync: wait for add to sync to disk
        :type wait_for_sync: bool
        :param
        :returns: the id, rev and key of the new document
        :rtype: bool
        :raises: DocumentInvalidError, DocumentAddError
        """
        if self._type is "edge":
            if "_to" not in data:
                raise DocumentInvalidError(
                    "the new document data is missing the '_to' key")
            if "_from" not in data:
                raise DocumentInvalidError(
                    "the new document data is missing the '_from' key")
        path = "/_api/{}".format(self._type)
        params = {
            "collection": self.name,
            "waitForSync": wait_for_sync,
        }
        if "_from" in data:
            params["from"] = data["_from"]
        if "_to" in data:
            params["to"] = data["_to"]
        if _batch:
            return {
                "method": "post",
                "path": path,
                "data": data,
                "params": params,
            }
        res = self._api.post(path=path, data=data, params=params)
        if res.status_code not in {201, 202}:
            raise DocumentAddError(res)
        return res.obj

    def update_document(self, key, data, rev=None, keep_none=True,
                        wait_for_sync=False, _batch=False):
        """Update the specified document in this collection.

        If ``keep_none`` is set to True, then attributes with values None
        are retained. Otherwise, they are removed from the document.

        If ``data`` contains the ``_key`` key, it is ignored.

        If the ``_rev`` key is in ``data``, the revision of the target
        document must match against its value. Otherwise a RevisionMismatch
        error is thrown. If ``rev`` is also provided, its value is preferred.

        The ``_from`` and ``_to`` attributes are immutable, and they are
        ignored if present in ``data``

        :param key: the key of the document to be updated
        :type key: str
        :param data: the body to update the document with
        :type data: dict
        :param rev: the document revision must match this value
        :type rev: str or None
        :param keep_none: whether or not to keep the items with value None
        :type keep_none: bool
        :param wait_for_sync: wait for the update to sync to disk
        :type wait_for_sync: bool
        :returns: the id, rev and key of the updated document
        :rtype: dict
        :raises: DocumentUpdateError
        """
        path = "/_api/{}/{}/{}".format(self._type, self.name, key)
        params = {
            "waitForSync": wait_for_sync,
            "keepNull": keep_none
        }
        if rev is not None:
            params["rev"] = rev
            params["policy"] = "error"
        elif "_rev" in data:
            params["rev"] = data["_rev"]
            params["policy"] = "error"
        if _batch:
            return {
                "method": "patch",
                "path": path,
                "data": data,
                "params": params,
            }
        res = self._api.patch(path=path, data=data, params=params)
        if res.status_code == 412:
            raise RevisionMismatchError(res)
        if res.status_code not in {201, 202}:
            raise DocumentUpdateError(res)
        del res.obj["error"]
        return res.obj

    def replace_document(self, key, data, rev=None, wait_for_sync=False,
                         _batch=False):
        """Replace the specified document in this collection.

        If ``data`` contains the ``_key`` key, it is ignored.

        If the ``_rev`` key is in ``data``, the revision of the target
        document must match against its value. Otherwise a RevisionMismatch
        error is thrown. If ``rev`` is also provided, its value is preferred.

        The ``_from`` and ``_to`` attributes are immutable, and they are
        ignored if present in ``data``.

        :param key: the key of the document to be replaced
        :type key: str
        :param data: the body to replace the document with
        :type data: dict
        :param rev: the document revision must match this value
        :type rev: str or None
        :param wait_for_sync: wait for the replace to sync to disk
        :type wait_for_sync: bool
        :returns: the id, rev and key of the replaced document
        :rtype: dict
        :raises: DocumentReplaceError
        """
        params = {"waitForSync": wait_for_sync}
        if rev is not None:
            params["rev"] = rev
            params["policy"] = "error"
        elif "_rev" in data:
            params["rev"] = data["_rev"]
            params["policy"] = "error"
        path = "/_api/{}/{}/{}".format(self._type, self.name, key)
        if _batch:
            return {
                "method": "put",
                "path": path,
                "data": data,
                "params": params,
            }
        res = self._api.put(path=path, params=params, data=data)
        if res.status_code == 412:
            raise RevisionMismatchError(res)
        elif res.status_code not in {201, 202}:
            raise DocumentReplaceError(res)
        del res.obj["error"]
        return res.obj

    def remove_document(self, key, rev=None, wait_for_sync=False,
                        _batch=False):
        """Remove the specified document from this collection.

        :param key: the key of the document to be removed
        :type key: str
        :param rev: the document revision must match this value
        :type rev: str or None
        :param wait_for_sync: wait for the remove to sync to disk
        :type wait_for_sync: bool
        :returns: the id, rev and key of the deleted document
        :rtype: dict
        :raises: RevisionMismatchError, DocumentRemoveError
        """
        params = {"waitForSync": wait_for_sync}
        if rev is not None:
            params["rev"] = rev
            params["policy"] = "error"
        path = "/_api/{}/{}/{}".format(self._type, self.name, key)
        if _batch:
            return {
                "method": "delete",
                "path": path,
                "params": params
            }
        res = self._api.delete(path=path, params=params)
        if res.status_code == 412:
            raise RevisionMismatchError(res)
        elif res.status_code not in {200, 202}:
            raise DocumentRemoveError(res)
        del res.obj["error"]
        return res.obj

    ##################
    # Simple Queries #
    ##################

    def first(self, count=1):
        """Return the first ``count`` number of documents in this collection.

        :param count: the number of documents to return
        :type count: int
        :returns: the list of documents
        :rtype: list
        :raises: SimpleQueryFirstError
        """
        res = self._api.put(
            "/_api/simple/first",
            data={"collection": self.name, "count": count}
        )
        if res.status_code != 200:
            raise SimpleQueryFirstError(res)
        return res.obj["result"]

    def last(self, count=1):
        """Return the last ``count`` number of documents in this collection.

        :param count: the number of documents to return
        :type count: int
        :returns: the list of documents
        :rtype: list
        :raises: SimpleQueryLastError
        """
        res = self._api.put(
            "/_api/simple/last",
            data={"collection": self.name, "count": count}
        )
        if res.status_code != 200:
            raise SimpleQueryLastError(res)
        return res.obj["result"]

    def all(self, skip=None, limit=None):
        """Return all documents in this collection.

        ``skip`` is applied before ``limit`` if both are provided.

        :param skip: the number of documents to skip
        :type skip: int
        :param limit: maximum number of documents to return
        :type limit: int
        :returns: the list of all documents
        :rtype: list
        :raises: SimpleQueryAllError
        """
        data = {"collection": self.name}
        if skip is not None:
            data["skip"] = skip
        if limit is not None:
            data["limit"] = limit
        res = self._api.put("/_api/simple/all", data=data)
        if res.status_code != 201:
            raise SimpleQueryAllError(res)
        return self.cursor(res)

    def any(self):
        """Return a random document from this collection.

        :returns: the random document
        :rtype: dict
        :raises: SimpleQueryAnyError
        """
        res = self._api.put(
            "/_api/simple/any",
            data={"collection": self.name}
        )
        if res.status_code != 200:
            raise SimpleQueryAnyError(res)
        return res.obj["document"]

    def get_first_example(self, example):
        """Return the first document matching the given example document body.

        :param example: the example document body
        :type example: dict
        :returns: the first matching document
        :rtype: dict
        :raises: SimpleQueryFirstExampleError
        """
        data = {"collection": self.name, "example": example}
        res = self._api.put("/_api/simple/first-example", data=data)
        if res.status_code == 404:
            return
        elif res.status_code != 200:
            raise SimpleQueryFirstExampleError(res)
        return res.obj["document"]

    def get_by_example(self, example, skip=None, limit=None):
        """Return all documents matching the given example document body.

        ``skip`` is applied before ``limit`` if both are provided.

        :param example: the example document body
        :type example: dict
        :param skip: the number of documents to skip
        :type skip: int
        :param limit: maximum number of documents to return
        :type limit: int
        :returns: the list of matching documents
        :rtype: list
        :raises: SimpleQueryGetByExampleError
        """
        data = {"collection": self.name, "example": example}
        if skip is not None:
            data["skip"] = skip
        if limit is not None:
            data["limit"] = limit
        res = self._api.put("/_api/simple/by-example", data=data)
        if res.status_code != 201:
            raise SimpleQueryGetByExampleError(res)
        return self.cursor(res)

    def update_by_example(self, example, new_value, keep_none=True, limit=None,
                          wait_for_sync=False):
        """Update all documents matching the given example document body.

        :param example: the example document body
        :type example: dict
        :param new_value: the new document body to update with
        :type new_value: dict
        :param keep_none: whether or not to keep the None values
        :type keep_none: bool
        :param limit: maximum number of documents to return
        :type limit: int
        :param wait_for_sync: wait for the update to sync to disk
        :type wait_for_sync: bool
        :returns: the number of documents updated
        :rtype: int
        :raises: SimpleQueryUpdateByExampleError
        """
        data = {
            "collection": self.name,
            "example": example,
            "newValue": new_value,
            "keepNull": keep_none,
            "waitForSync": wait_for_sync,
        }
        if limit is not None:
            data["limit"] = limit
        res = self._api.put("/_api/simple/update-by-example", data=data)
        if res.status_code != 200:
            raise SimpleQueryUpdateByExampleError(res)
        return res.obj["updated"]

    def replace_by_example(self, example, new_value, limit=None,
                           wait_for_sync=False):
        """Replace all documents matching the given example.

        ``skip`` is applied before ``limit`` if both are provided.

        :param example: the example document
        :type example: dict
        :param new_value: the new document
        :type new_value: dict
        :param limit: maximum number of documents to return
        :type limit: int
        :param wait_for_sync: wait for the replace to sync to disk
        :type wait_for_sync: bool
        :returns: the number of documents replaced
        :rtype: int
        :raises: SimpleQueryReplaceByExampleError
        """
        data = {
            "collection": self.name,
            "example": example,
            "newValue": new_value,
            "waitForSync": wait_for_sync,
        }
        if limit is not None:
            data["limit"] = limit
        res = self._api.put("/_api/simple/replace-by-example", data=data)
        if res.status_code != 200:
            raise SimpleQueryReplaceByExampleError(res)
        return res.obj["replaced"]

    def remove_by_example(self, example, limit=None, wait_for_sync=False):
        """Remove all documents matching the given example.

        :param example: the example document
        :type example: dict
        :param limit: maximum number of documents to return
        :type limit: int
        :param wait_for_sync: wait for the remove to sync to disk
        :type wait_for_sync: bool
        :returns: the number of documents remove
        :rtype: int
        :raises: SimpleQueryRemoveByExampleError
        """
        data = {
            "collection": self.name,
            "example": example,
            "waitForSync": wait_for_sync,
        }
        if limit is not None:
            data["limit"] = limit
        res = self._api.put("/_api/simple/remove-by-example", data=data)
        if res.status_code != 200:
            raise SimpleQueryRemoveByExampleError(res)
        return res.obj["deleted"]

    def range(self, attribute, left, right, closed=True, skip=None, limit=None):
        """Return all the documents within a given range.

        In order to execute this query a skiplist index must be present on the
        queried attribute.

        :param attribute: the attribute path with a skip-list index
        :type attribute: str
        :param left: the lower bound
        :type left: int
        :param right: the upper bound
        :type right: int
        :param closed: whether or not to include left and right, or just left
        :type closed: bool
        :param skip: the number of documents to skip
        :type skip: int
        :param limit: maximum number of documents to return
        :type limit: int
        :returns: the list of documents
        :rtype: list
        :raises: SimpleQueryRangeError
        """
        data = {
            "collection": self.name,
            "attribute": attribute,
            "left": left,
            "right": right,
            "closed": closed
        }
        if skip is not None:
            data["skip"] = skip
        if limit is not None:
            data["limit"] = limit
        res = self._api.put("/_api/simple/range", data=data)
        if res.status_code != 201:
            raise SimpleQueryRangeError(res)
        return self.cursor(res)

    def near(self, latitude, longitude, distance=None, radius=None, skip=None,
             limit=None, geo=None):
        """Return all the documents near the given coordinate.

        By default number of documents returned is 100. The returned list is
        sorted based on the distance, with the nearest document being the first
        in the list. Documents of equal distance are ordered randomly.

        In order to execute this query a geo index must be defined for the
        collection. If there are more than one geo-spatial index, the ``geo``
        argument can be used to select a particular index.

        if ``distance`` is given, return the distance (in meters) to the
        coordinate in a new attribute whose key is the value of the argument.

        :param latitude: the latitude of the coordinate
        :type latitude: int
        :param longitude: the longitude of the coordinate
        :type longitude: int
        :param distance: return the distance to the coordinate in this key
        :type distance: str
        :param skip: the number of documents to skip
        :type skip: int
        :param limit: maximum number of documents to return
        :type limit: int
        :param geo: the identifier of the geo-index to use
        :type geo: str
        :returns: the list of documents that are near the coordinate
        :rtype: list
        :raises: SimpleQueryNearError
        """
        data = {
            "collection": self.name,
            "latitude": latitude,
            "longitude": longitude
        }
        if distance is not None:
            data["distance"] = distance
        if radius is not None:
            data["radius"] = radius
        if skip is not None:
            data["skip"] = skip
        if limit is not None:
            data["limit"] = limit
        if geo is not None:
            data["geo"] = geo

        res = self._api.put("/_api/simple/near", data=data)
        if res.status_code != 201:
            raise SimpleQueryNearError(res)
        return self.cursor(res)

    # TODO this endpoint does not seem to work
    # Come back to this and check that it works in the next version of ArangoDB
    def within(self, latitude, longitude, radius, distance=None, skip=None,
               limit=None, geo=None):
        """Return all documents within the radius around the coordinate.

        The returned list is sorted by distance from the coordinate. In order
        to execute this query a geo index must be defined for the collection.
        If there are more than one geo-spatial index, the ``geo`` argument can
        be used to select a particular index.

        if ``distance`` is given, return the distance (in meters) to the
        coordinate in a new attribute whose key is the value of the argument.

        :param latitude: the latitude of the coordinate
        :type latitude: int
        :param longitude: the longitude of the coordinate
        :type longitude: int
        :param radius: the maximum radius (in meters)
        :type radius: int
        :param distance: return the distance to the coordinate in this key
        :type distance: str
        :param skip: the number of documents to skip
        :type skip: int
        :param limit: maximum number of documents to return
        :type limit: int
        :param geo: the identifier of the geo-index to use
        :type geo: str
        :returns: the list of documents are within the radius
        :rtype: list
        :raises: SimpleQueryWithinError
        """
        data = {
            "collection": self.name,
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius
        }
        if distance is not None:
            data["distance"] = distance
        if skip is not None:
            data["skip"] = skip
        if limit is not None:
            data["limit"] = limit
        if geo is not None:
            data["geo"] = geo

        res = self._api.put("/_api/simple/within", data=data)
        if res.status_code != 201:
            return SimpleQueryWithinError(res)
        return self.cursor(res)

    def fulltext(self, attribute, query, skip=None, limit=None, index=None):
        """Return all documents that match the specified fulltext ``query``.

        In order to execute this query a fulltext index must be defined for the
        collection and the specified attribute.

        For more information on fulltext queries please refer to:
        https://docs.arangodb.com/SimpleQueries/FulltextQueries.html

        :param attribute: the attribute path with a fulltext index
        :type attribute: str
        :param query: the fulltext query
        :type query: str
        :param skip: the number of documents to skip
        :type skip: int
        :param limit: maximum number of documents to return
        :type limit: int
        :returns: the list of documents
        :rtype: list
        :raises: SimpleQueryFullTextError
        """
        data = {
            "collection": self.name,
            "attribute": attribute,
            "query": query,
        }
        if skip is not None:
            data["skip"] = skip
        if limit is not None:
            data["limit"] = limit
        if index is not None:
            data["index"] = index
        res = self._api.put("/_api/simple/fulltext", data=data)
        if res.status_code != 201:
            return SimpleQueryFullTextError(res)
        return self.cursor(res)

    ####################
    # Batch Operations #
    ####################

    def bulk_import(self, documents, complete=True, details=True):
        """Import documents into this collection in bulk.

        If ``complete`` is set to a value other than True, valid documents
        will be imported while invalid ones are rejected, meaning only some of
        the uploaded documents might have been imported.

        If ``details`` parameter is set to True, the response will also contain
        ``details`` attribute which is a list of detailed error messages.

        :param documents: list of documents to import
        :type documents: list
        :param complete: entire import fails if any document is invalid
        :type complete: bool
        :param details: return details about invalid documents
        :type details: bool
        :returns: the import results
        :rtype: dict
        :raises: CollectionBulkImportError
        """
        res = self._api.post(
            "/_api/import",
            data="\r\n".join([json.dumps(d) for d in documents]),
            params={
                "type": "documents",
                "collection": self.name,
                "complete": complete,
                "details": details
            }
        )
        if res.status_code != 201:
            raise CollectionBulkImportError(res)
        del res.obj["error"]
        return res.obj

    ####################
    # Handling Indexes #
    ####################

    @property
    def indexes(self):
        """Return the details on the indexes of this collection.

        :returns: the index details
        :rtype: dict
        :raises: IndexListError
        """
        res = self._api.get(
            "/_api/index?collection={}".format(self.name)
        )
        if res.status_code != 200:
            raise IndexListError(res)

        indexes = {}
        for index_id, details in res.obj["identifiers"].items():
            del details["id"]
            indexes[index_id.split("/", 1)[1]] = uncamelify(details)
        return indexes

    def _add_index(self, data):
        """Helper method for adding new indexes."""
        res = self._api.post(
            "/_api/index?collection={}".format(self.name),
            data=data
        )
        if res.status_code not in {200, 201}:
            raise IndexAddError(res)

    def add_hash_index(self, fields, unique=None):
        """Add a new hash index to this collection.

        :param fields: the attribute paths to index
        :type fields: list
        :param unique: whether or not the index is unique
        :type unique: bool or None
        :raises: IndexAddError
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
        :raises: IndexAddError
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
        :raises: IndexAddError
        """
        data = {"type": "skiplist", "fields": fields}
        if unique is not None:
            data["unique"] = unique
        self._add_index(data)

    def add_geo_index(self, fields, geo_json=None, unique=None,
                      ignore_null=None):
        """Add a geo index to this collection

        If ``fields`` is a list with ONE attribute path, then a geo-spatial
        index on all documents is created using the value at the path as the
        coordinates. The value must be a list with at least two doubles. The
        list must contain the latitude (first value) and the longitude (second
        value). All documents without the attribute paths or with invalid values
        are ignored.

        If ``fields`` is a list with TWO attribute paths (i.e. latitude and
        longitude, in that order) then a geo-spatial index on all documents is
        created using the two attributes (again, their values must be doubles).
        All documents without the attribute paths or with invalid values are
        ignored.

        :param fields: the attribute paths to index (length must be <= 2)
        :type fields: list
        :param geo_json: whether or not the order is longitude -> latitude
        :type geo_json: bool or None
        :param unique: whether or not to create a geo-spatial constraint
        :type unique: bool or None
        :param ignore_null: ignore docs with None in latitude/longitude
        :type ignore_null: bool or None
        :raises: IndexAddError
        """
        data = {"type": "geo", "fields": fields}
        if geo_json is not None:
            data["geoJson"] = geo_json
        if unique is not None:
            data["unique"] = unique
        if ignore_null is not None:
            data["ignore_null"] = ignore_null
        self._add_index(data)

    def add_fulltext_index(self, fields, min_length=None):
        """Add a fulltext index to this collection.

        A fulltext index can be used to find words, or prefixes of words inside
        documents. A fulltext index can be set on one attribute only, and will
        index all words contained in documents that have a textual value in this
        attribute. Only words with a (specifiable) minimum length are indexed.
        Word tokenization is done using the word boundary analysis provided by
        libicu, which is taking into account the selected language provided at
        server start. Words are indexed in their lower-cased form. The index
        supports complete match queries (full words) and prefix queries.

        Fulltext index cannot be unique.

        :param fields: the attribute paths to index (length must be 1)
        :type fields: list
        :param min_length: minimum character length of words to index
        :type min_length: int
        :raises: IndexAddError
        """
        data = {"type": "fulltext", "fields": fields}
        if min_length is not None:
            data["minLength"] = min_length
        self._add_index(data)

    def remove_index(self, index_id):
        """Delete an index from this collection.

        :param index_id: the ID of the index to remove
        :type index_id: str
        :raises: IndexRemoveError
        """
        res = self._api.delete(
            "/_api/index/{}/{}".format(self.name, index_id)
        )
        if res.status_code != 200:
            raise IndexRemoveError(res)
