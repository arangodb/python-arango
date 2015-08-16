"""ArangoDB Collection."""

import json

from arango.utils import camelify, uncamelify
from arango.exceptions import *
from arango.cursor import arango_cursor
from arango.constants import COLLECTION_STATUSES, HTTP_OK


class Collection(object):
    """Wrapper for ArangoDB's collection-specific API."""

    def __init__(self, name, api):
        """Initialize the wrapper object.

        :param name: the name of this collection
        :type name: str
        :param api: ArangoDB API object
        :type api: arango.api.API
        """
        self.name = name
        self.api = api
        self.type = "edge" if self.is_edge else "document"

    def __iter__(self):
        """Iterate through the documents in this collection."""
        return self.all()

    def __len__(self):
        """Return the number of documents in this collection."""
        return self.count

    def __setattr__(self, attr, value):
        """Update the properties of this collection.

        Only ``wait_for_sync`` and ``journal_size`` attributes are mutable.
        """
        if attr in {"wait_for_sync", "journal_size"}:
            res = self.api.put(
                "/_api/collection/{}/properties".format(self.name),
                data={camelify(attr): value}
            )
            if res.status_code not in HTTP_OK:
                raise CollectionUpdateError(res)
        else:
            super(Collection, self).__setattr__(attr, value)

    def __getitem__(self, key):
        """Return the document of the given key from this collection.

        :param key: the document key
        :type key: str
        :returns: the requested document
        :rtype: dict
        :raises: TypeError
        """
        if not isinstance(key, str):
            raise TypeError("Expecting a str.")
        return self.document(key)

    def __contains__(self, key):
        """Return True if the document exists in this collection.

        :param key: the document key
        :type key: str
        :returns: True if the document exists, False otherwise
        :rtype: bool
        :raises: DocumentGetError
        """
        return self.contains(key)

    @property
    def count(self):
        """Return the number of documents present in this collection.

        :returns: the number of documents
        :rtype: int
        :raises: CollectionGetError
        """
        res = self.api.get(
            "/_api/collection/{}/count".format(self.name)
        )
        if res.status_code not in HTTP_OK:
            raise CollectionGetError(res)
        return res.obj["count"]

    @property
    def properties(self):
        """Return the properties of this collection.

        :returns: the collection's id, status, key_options etc.
        :rtype: dict
        :raises: CollectionGetError
        """
        res = self.api.get(
            "/_api/collection/{}/properties".format(self.name)
        )
        if res.status_code not in HTTP_OK:
            raise CollectionGetError(res)
        return {
            "id": res.obj["id"],
            "name": res.obj["name"],
            "is_edge": res.obj["type"] == 3,
            "status": COLLECTION_STATUSES.get(
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
        :raises: CollectionGetError
        """
        return self.properties["id"]

    @property
    def status(self):
        """Return the status of this collection.

        :returns: the collection status
        :rtype: str
        :raises: CollectionGetError
        """
        return self.properties["status"]

    @property
    def key_options(self):
        """Return this collection's key options.

        :returns: the key options of this collection
        :rtype: dict
        :raises: CollectionGetError
        """
        return self.properties["key_options"]

    @property
    def wait_for_sync(self):
        """Return True if this collection waits for changes to sync to disk.

        :returns: True if collection waits for sync, False otherwise
        :rtype: bool
        :raises: CollectionGetError
        """
        return self.properties["wait_for_sync"]

    @property
    def journal_size(self):
        """Return the journal size of this collection.

        :returns: the journal size of this collection
        :rtype: str
        :raises: CollectionGetError
        """
        return self.properties["journal_size"]

    @property
    def is_volatile(self):
        """Return True if this collection is kept in memory and not persistent.

        :returns: True if the collection is volatile, False otherwise
        :rtype: bool
        :raises: CollectionGetError
        """
        return self.properties["is_volatile"]

    @property
    def is_system(self):
        """Return True if this collection is a system Collection.

        :returns: True if system collection, False otherwise
        :rtype: bool
        :raises: CollectionGetError
        """
        return self.properties["is_system"]

    @property
    def is_edge(self):
        """Return True if this collection is a system Collection.

        :returns: True if edge collection, False otherwise
        :rtype: bool
        :raises: CollectionGetError
        """
        return self.properties["is_edge"]

    @property
    def do_compact(self):
        """Return True if this collection is compacted.

        :returns: True if collection is compacted, False otherwise
        :rtype: bool
        :raises: CollectionGetError
        """
        return self.properties["do_compact"]

    @property
    def figures(self):
        """Return the statistics of this collection.

        :returns: the statistics of this collection
        :rtype: dict
        :raises: CollectionGetError
        """
        res = self.api.get(
            "/_api/collection/{}/figures".format(self.name)
        )
        if res.status_code not in HTTP_OK:
            raise CollectionGetError(res)
        return uncamelify(res.obj["figures"])

    @property
    def revision(self):
        """Return the revision of this collection.

        :returns: the collection revision (etag)
        :rtype: str
        :raises: CollectionGetError
        """
        res = self.api.get(
            "/_api/collection/{}/revision".format(self.name)
        )
        if res.status_code not in HTTP_OK:
            raise CollectionGetError(res)
        return res.obj["revision"]

    def load(self):
        """Load this collection into memory.

        :returns: the status of the collection
        :rtype: str
        :raises: CollectionLoadError
        """
        res = self.api.put(
            "/_api/collection/{}/load".format(self.name)
        )
        if res.status_code not in HTTP_OK:
            raise CollectionLoadError(res)
        return COLLECTION_STATUSES.get(
            res.obj["status"],
            "corrupted ({})".format(res.obj["status"])
        )

    def unload(self):
        """Unload this collection from memory.

        :returns: the status of the collection
        :rtype: str
        :raises: CollectionUnloadError
        """
        res = self.api.put(
            "/_api/collection/{}/unload".format(self.name)
        )
        if res.status_code not in HTTP_OK:
            raise CollectionUnloadError(res)
        return COLLECTION_STATUSES.get(
            res.obj["status"],
            "corrupted ({})".format(res.obj["status"])
        )

    def rotate_journal(self):
        """Rotate the journal of this collection.

        :raises: CollectionRotateJournalError
        """
        res = self.api.put(
            "/_api/collection/{}/rotate".format(self.name)
        )
        if res.status_code not in HTTP_OK:
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
        res = self.api.get(
            "/_api/collection/{}/checksum".format(self.name),
            params={"withRevision": with_rev, "withData": with_data}
        )
        if res.status_code not in HTTP_OK:
            raise CollectionGetError(res)
        return res.obj["checksum"]

    def truncate(self):
        """Delete all documents from this collection.

        :raises: CollectionTruncateError
        """
        res = self.api.put(
            "/_api/collection/{}/truncate".format(self.name)
        )
        if res.status_code not in HTTP_OK:
            raise CollectionTruncateError(res)

    def contains(self, key):
        """Return True if the document exists in this collection.

        :param key: the document key
        :type key: str
        :returns: True if the document exists, else False
        :rtype: bool
        :raises: DocumentGetError
        """
        res = self.api.head(
            "/_api/{}/{}/{}".format(self.type, self.name, key)
        )
        if res.status_code == 200:
            return True
        elif res.status_code == 404:
            return False
        else:
            raise DocumentGetError(res)

    #############
    # Documents #
    #############

    def document(self, key, rev=None, match=True):
        """Return the document of the given key.

        If the document revision ``rev`` is specified, it is compared
        against the revision of the retrieved document. If ``match`` is set
        to True and the revisions do NOT match, or if ``match`` is set to
        False and the revisions DO match, ``DocumentRevisionError`` is thrown.

        :param key: the key of the document to retrieve
        :type key: str
        :param rev: the document revision is compared against this value
        :type rev: str or None
        :param match: whether or not the revision should match
        :type match: bool
        :returns: the requested document or None if not found
        :rtype: dict or None
        :raises: DocumentRevisionError, DocumentGetError
        """
        res = self.api.get(
            "/_api/{}/{}/{}".format(self.type, self.name, key),
            headers={
                "If-Match" if match else "If-None-Match": rev
            } if rev else {}
        )
        if res.status_code in {412, 304}:
            raise DocumentRevisionError(res)
        elif res.status_code == 404:
            return None
        elif res.status_code not in HTTP_OK:
            raise DocumentGetError(res)
        return res.obj

    def create_document(self, data, wait_for_sync=False, _batch=False):
        """Create a new document to this collection.

        If ``data`` contains the ``_key`` key, its value must be free.
        If this collection is an edge collection, ``data`` must contain the
        ``_from`` and ``_to`` keys with valid vertex IDs as their values.

        :param data: the body of the new document
        :type data: dict
        :param wait_for_sync: wait for create to sync to disk
        :type wait_for_sync: bool
        :returns: the id, rev and key of the new document
        :rtype: dict
        :raises: DocumentInvalidError, DocumentCreateError
        """
        if self.type is "edge":
            if "_to" not in data:
                raise DocumentInvalidError(
                    "the new document data is missing the '_to' key")
            if "_from" not in data:
                raise DocumentInvalidError(
                    "the new document data is missing the '_from' key")
        path = "/_api/{}".format(self.type)
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
        res = self.api.post(path=path, data=data, params=params)
        if res.status_code not in HTTP_OK:
            raise DocumentCreateError(res)
        return res.obj

    def update_document(self, key, data, rev=None, keep_none=True,
                        wait_for_sync=False, _batch=False):
        """Update the specified document in this collection.

        If ``keep_none`` is set to True, then attributes with values None
        are retained. Otherwise, they are deleted from the document.

        If ``data`` contains the ``_key`` key, it is ignored.

        If the ``_rev`` key is in ``data``, the revision of the target
        document must match against its value. Otherwise a DocumentRevision
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
        path = "/_api/{}/{}/{}".format(self.type, self.name, key)
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
        res = self.api.patch(path=path, data=data, params=params)
        if res.status_code == 412:
            raise DocumentRevisionError(res)
        if res.status_code not in HTTP_OK:
            raise DocumentUpdateError(res)
        del res.obj["error"]
        return res.obj

    def replace_document(self, key, data, rev=None, wait_for_sync=False,
                         _batch=False):
        """Replace the specified document in this collection.

        If ``data`` contains the ``_key`` key, it is ignored.

        If the ``_rev`` key is in ``data``, the revision of the target
        document must match against its value. Otherwise a DocumentRevision
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
        path = "/_api/{}/{}/{}".format(self.type, self.name, key)
        if _batch:
            return {
                "method": "put",
                "path": path,
                "data": data,
                "params": params,
            }
        res = self.api.put(path=path, params=params, data=data)
        if res.status_code == 412:
            raise DocumentRevisionError(res)
        elif res.status_code not in HTTP_OK:
            raise DocumentReplaceError(res)
        del res.obj["error"]
        return res.obj

    def delete_document(self, key, rev=None, wait_for_sync=False,
                        _batch=False):
        """Delete the specified document from this collection.

        :param key: the key of the document to be deleted
        :type key: str
        :param rev: the document revision must match this value
        :type rev: str or None
        :param wait_for_sync: wait for the delete to sync to disk
        :type wait_for_sync: bool
        :returns: the id, rev and key of the deleted document
        :rtype: dict
        :raises: DocumentRevisionError, DocumentDeleteError
        """
        params = {"waitForSync": wait_for_sync}
        if rev is not None:
            params["rev"] = rev
            params["policy"] = "error"
        path = "/_api/{}/{}/{}".format(self.type, self.name, key)
        if _batch:
            return {
                "method": "delete",
                "path": path,
                "params": params
            }
        res = self.api.delete(path=path, params=params)
        if res.status_code == 412:
            raise DocumentRevisionError(res)
        elif res.status_code not in {200, 202}:
            raise DocumentDeleteError(res)
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
        res = self.api.put(
            "/_api/simple/first",
            data={"collection": self.name, "count": count}
        )
        if res.status_code not in HTTP_OK:
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
        res = self.api.put(
            "/_api/simple/last",
            data={"collection": self.name, "count": count}
        )
        if res.status_code not in HTTP_OK:
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
        res = self.api.put("/_api/simple/all", data=data)
        if res.status_code not in HTTP_OK:
            raise SimpleQueryAllError(res)
        return arango_cursor(self.api, res)

    def any(self):
        """Return a random document from this collection.

        :returns: the random document
        :rtype: dict
        :raises: SimpleQueryAnyError
        """
        res = self.api.put(
            "/_api/simple/any",
            data={"collection": self.name}
        )
        if res.status_code not in HTTP_OK:
            raise SimpleQueryAnyError(res)
        return res.obj["document"]

    def get_first_example(self, example):
        """Return the first document matching the given example document body.

        :param example: the example document body
        :type example: dict
        :returns: the first matching document
        :rtype: dict or None
        :raises: SimpleQueryFirstExampleError
        """
        data = {"collection": self.name, "example": example}
        res = self.api.put("/_api/simple/first-example", data=data)
        if res.status_code == 404:
            return None
        elif res.status_code not in HTTP_OK:
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
        res = self.api.put("/_api/simple/by-example", data=data)
        if res.status_code not in HTTP_OK:
            raise SimpleQueryGetByExampleError(res)
        return arango_cursor(self.api, res)

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
        res = self.api.put("/_api/simple/update-by-example", data=data)
        if res.status_code not in HTTP_OK:
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
        res = self.api.put("/_api/simple/replace-by-example", data=data)
        if res.status_code not in HTTP_OK:
            raise SimpleQueryReplaceByExampleError(res)
        return res.obj["replaced"]

    def remove_by_example(self, example, limit=None, wait_for_sync=False):
        """Remove all documents matching the given example.

        :param example: the example document
        :type example: dict
        :param limit: maximum number of documents to return
        :type limit: int
        :param wait_for_sync: wait for the delete to sync to disk
        :type wait_for_sync: bool
        :returns: the number of documents deleted
        :rtype: int
        :raises: SimpleQueryDeleteByExampleError
        """
        data = {
            "collection": self.name,
            "example": example,
            "waitForSync": wait_for_sync,
        }
        if limit is not None:
            data["limit"] = limit
        res = self.api.put("/_api/simple/remove-by-example", data=data)
        if res.status_code not in HTTP_OK:
            raise SimpleQueryDeleteByExampleError(res)
        return res.obj["deleted"]

    def range(self, attribute, left, right, closed=True, skip=None,
              limit=None):
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
        res = self.api.put("/_api/simple/range", data=data)
        if res.status_code not in HTTP_OK:
            raise SimpleQueryRangeError(res)
        return arango_cursor(self.api, res)

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

        res = self.api.put("/_api/simple/near", data=data)
        if res.status_code not in HTTP_OK:
            raise SimpleQueryNearError(res)
        return arango_cursor(self.api, res)

    # TODO this endpoint does not seem to work
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

        res = self.api.put("/_api/simple/within", data=data)
        if res.status_code not in HTTP_OK:
            raise SimpleQueryWithinError(res)
        return arango_cursor(self.api, res)

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
        res = self.api.put("/_api/simple/fulltext", data=data)
        if res.status_code not in HTTP_OK:
            raise SimpleQueryFullTextError(res)
        return arango_cursor(self.api, res)

    def lookup_by_keys(self, keys):
        """Return all documents whose key is in ``keys``.

        :param keys: keys of documents to lookup
        :type keys: list
        :returns: the list of documents
        :rtype: list
        :raises: SimpleQueryLookupByKeysError
        """
        data = {
            "collection": self.name,
            "keys": keys,
        }
        res = self.api.put("/_api/simple/lookup-by-keys", data=data)
        if res.status_code not in HTTP_OK:
            raise SimpleQueryLookupByKeysError(res)
        return res.obj["documents"]

    def remove_by_keys(self, keys):
        """Remove all documents whose key is in ``keys``.

        :param keys: keys of documents to delete
        :type keys: list
        :returns: the number of documents deleted
        :rtype: dict
        :raises: SimpleQueryDeleteByKeysError
        """
        data = {
            "collection": self.name,
            "keys": keys,
        }
        res = self.api.put("/_api/simple/remove-by-keys", data=data)
        if res.status_code not in HTTP_OK:
            raise SimpleQueryDeleteByKeysError(res)
        return {
            "removed": res.obj["removed"],
            "ignored": res.obj["ignored"],
        }

    ###############
    # Bulk Import #
    ###############

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
        :raises: BulkImportError
        """
        res = self.api.post(
            "/_api/import",
            data="\r\n".join([json.dumps(d) for d in documents]),
            params={
                "type": "documents",
                "collection": self.name,
                "complete": complete,
                "details": details
            }
        )
        if res.status_code not in HTTP_OK:
            raise BulkImportError(res)
        del res.obj["error"]
        return res.obj

    ##########
    # Export #
    ##########

    # TODO look into this endpoint for better documentation and testing
    def export(self, flush=None, flush_wait=None, count=None, batch_size=None,
               limit=None, ttl=None, restrict=None):
        """"Export all documents from this collection using a cursor.

        :param flush: trigger a WAL flush operation prior to the export
        :type flush: bool or None
        :param flush_wait: the max wait time in sec for flush operation
        :type flush_wait: int or None
        :param count: whether the count is returned in an attribute of result
        :type count: bool or None
        :param batch_size: the max number of result documents in one roundtrip
        :type batch_size: int or None
        :param limit: the max number of documents to be included in the cursor
        :type limit: int or None
        :param ttl: time-to-live for the cursor on the server
        :type ttl: int or None
        :param restrict: object with attributes to be excluded/included
        :type restrict: dict
        :return: the generator of documents in this collection
        :rtype: generator
        :raises: CollectionExportError
        """
        params = {"collection": self.name}
        options = {}
        if flush is not None:
            options["flush"] = flush
        if flush_wait is not None:
            options["flushWait"] = flush_wait
        if count is not None:
            options["count"] = count
        if batch_size is not None:
            options["batchSize"] = batch_size
        if limit is not None:
            options["limit"] = limit
        if ttl is not None:
            options["ttl"] = ttl
        if restrict is not None:
            options["restrict"] = restrict
        data = {"options": options} if options else {}

        res = self.api.post("/_api/export", params=params, data=data)
        if res.status_code not in HTTP_OK:
            raise CollectionExportError(res)
        return arango_cursor(self.api, res)

    ###########
    # Indexes #
    ###########

    @property
    def indexes(self):
        """Return the details on the indexes of this collection.

        :returns: the index details
        :rtype: dict
        :raises: IndexListError
        """
        res = self.api.get(
            "/_api/index?collection={}".format(self.name)
        )
        if res.status_code not in HTTP_OK:
            raise IndexListError(res)

        indexes = {}
        for index_id, details in res.obj["identifiers"].items():
            del details["id"]
            indexes[index_id.split("/", 1)[1]] = uncamelify(details)
        return indexes

    def _create_index(self, data):
        """Helper method for creating new indexes."""
        res = self.api.post(
            "/_api/index?collection={}".format(self.name),
            data=data
        )
        if res.status_code not in HTTP_OK:
            raise IndexCreateError(res)
        return res.obj

    def create_hash_index(self, fields, unique=None, sparse=None):
        """Create a new hash index to this collection.

        :param fields: the attribute paths to index
        :type fields: list
        :param unique: whether or not the index is unique
        :type unique: bool or None
        :param sparse: whether to index attr values of null
        :type sparse: bool or None
        :raises: IndexCreateError
        """
        data = {"type": "hash", "fields": fields}
        if unique is not None:
            data["unique"] = unique
        if sparse is not None:
            data["sparse"] = sparse
        return self._create_index(data)

    def create_cap_constraint(self, size=None, byte_size=None):
        """Create a cap constraint to this collection.

        :param size: the number for documents allowed in this collection
        :type size: int or None
        :param byte_size: the max size of the active document data (> 16384)
        :type byte_size: int or None
        :raises: IndexCreateError
        """
        data = {"type": "cap"}
        if size is not None:
            data["size"] = size
        if byte_size is not None:
            data["byteSize"] = byte_size
        return self._create_index(data)

    def create_skiplist_index(self, fields, unique=None, sparse=None):
        """Create a new skiplist index to this collection.

        A skiplist index is used to find ranges of documents (e.g. time).

        :param fields: the attribute paths to index
        :type fields: list
        :param unique: whether or not the index is unique
        :type unique: bool or None
        :param sparse: whether to index attr values of null
        :type sparse: bool or None
        :raises: IndexCreateError
        """
        data = {"type": "skiplist", "fields": fields}
        if unique is not None:
            data["unique"] = unique
        if sparse is not None:
            data["sparse"] = sparse
        return self._create_index(data)

    def create_geo_index(self, fields, geo_json=None, unique=None,
                         ignore_null=None):
        """Create a geo index to this collection

        If ``fields`` is a list with ONE attribute path, then a geo-spatial
        index on all documents is created using the value at the path as the
        coordinates. The value must be a list with at least two doubles. The
        list must contain the latitude (first value) and the longitude (second
        value). All documents without the attribute paths or with invalid
        values are ignored.

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
        :raises: IndexCreateError
        """
        data = {"type": "geo", "fields": fields}
        if geo_json is not None:
            data["geoJson"] = geo_json
        if unique is not None:
            data["unique"] = unique
        if ignore_null is not None:
            data["ignore_null"] = ignore_null
        return self._create_index(data)

    def create_fulltext_index(self, fields, min_length=None):
        """Create a fulltext index to this collection.

        A fulltext index can be used to find words, or prefixes of words inside
        documents. A fulltext index can be set on one attribute only, and will
        index all words contained in documents with a textual value in this
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
        :raises: IndexCreateError
        """
        data = {"type": "fulltext", "fields": fields}
        if min_length is not None:
            data["minLength"] = min_length
        return self._create_index(data)

    def delete_index(self, index_id):
        """Delete an index from this collection.

        :param index_id: the ID of the index to delete
        :type index_id: str
        :raises: IndexDeleteError
        """
        res = self.api.delete(
            "/_api/index/{}/{}".format(self.name, index_id)
        )
        if res.status_code not in HTTP_OK:
            raise IndexDeleteError(res)
        return res.obj
