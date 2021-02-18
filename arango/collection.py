__all__ = ["StandardCollection", "VertexCollection", "EdgeCollection"]

from numbers import Number
from typing import List, Optional, Sequence, Tuple, Union

from arango.api import ApiGroup
from arango.connection import Connection
from arango.cursor import Cursor
from arango.exceptions import (
    ArangoServerError,
    CollectionChecksumError,
    CollectionConfigureError,
    CollectionLoadError,
    CollectionPropertiesError,
    CollectionRecalculateCountError,
    CollectionRenameError,
    CollectionResponsibleShardError,
    CollectionRevisionError,
    CollectionStatisticsError,
    CollectionTruncateError,
    CollectionUnloadError,
    DocumentCountError,
    DocumentDeleteError,
    DocumentGetError,
    DocumentIDsError,
    DocumentInError,
    DocumentInsertError,
    DocumentKeysError,
    DocumentParseError,
    DocumentReplaceError,
    DocumentRevisionError,
    DocumentUpdateError,
    EdgeListError,
    IndexCreateError,
    IndexDeleteError,
    IndexListError,
    IndexLoadError,
)
from arango.executor import ApiExecutor
from arango.formatter import format_collection, format_edge, format_index, format_vertex
from arango.request import Request
from arango.response import Response
from arango.result import Result
from arango.typings import Fields, Headers, Json, Params
from arango.utils import get_doc_id, is_none_or_int, is_none_or_str


class Collection(ApiGroup):
    """Base class for collection API wrappers.

    :param connection: HTTP connection.
    :param executor: API executor.
    :param name: Collection name.
    """

    types = {2: "document", 3: "edge"}

    statuses = {
        1: "new",
        2: "unloaded",
        3: "loaded",
        4: "unloading",
        5: "deleted",
        6: "loading",
    }

    def __init__(
        self, connection: Connection, executor: ApiExecutor, name: str
    ) -> None:
        super().__init__(connection, executor)
        self._name = name
        self._id_prefix = name + "/"

    def __iter__(self) -> Result[Cursor]:
        return self.all()

    def __len__(self) -> Result[int]:
        return self.count()

    def __contains__(self, document: Union[str, Json]) -> Result[bool]:
        return self.has(document, check_rev=False)

    def _get_status_text(self, code: int) -> str:  # pragma: no cover
        """Return the collection status text.

        :param code: Collection status code.
        :type code: int
        :return: Collection status text or None if code is None.
        :rtype: str
        """
        return None if code is None else self.statuses[code]

    def _validate_id(self, doc_id: str) -> str:
        """Check the collection name in the document ID.

        :param doc_id: Document ID.
        :type doc_id: str
        :return: Verified document ID.
        :rtype: str
        :raise arango.exceptions.DocumentParseError: On bad collection name.
        """
        if not doc_id.startswith(self._id_prefix):
            raise DocumentParseError(f'bad collection name in document ID "{doc_id}"')
        return doc_id

    def _extract_id(self, body: Json) -> str:
        """Extract the document ID from document body.

        :param body: Document body.
        :type body: dict
        :return: Document ID.
        :rtype: str
        :raise arango.exceptions.DocumentParseError: On missing ID and key.
        """
        try:
            if "_id" in body:
                return self._validate_id(body["_id"])
            else:
                key: str = body["_key"]
                return self._id_prefix + key
        except KeyError:
            raise DocumentParseError('field "_key" or "_id" required')

    def _prep_from_body(self, document: Json, check_rev: bool) -> Tuple[str, Headers]:
        """Prepare document ID and request headers.

        :param document: Document body.
        :type document: dict
        :param check_rev: Whether to check the revision.
        :type check_rev: bool
        :return: Document ID and request headers.
        :rtype: (str, dict)
        """
        doc_id = self._extract_id(document)
        if not check_rev or "_rev" not in document:
            return doc_id, {}
        return doc_id, {"If-Match": document["_rev"]}

    def _prep_from_doc(
        self, document: Union[str, Json], rev: Optional[str], check_rev: bool
    ) -> Tuple[str, Union[str, Json], Json]:
        """Prepare document ID, body and request headers.

        :param document: Document ID, key or body.
        :type document: str | dict
        :param rev: Document revision or None.
        :type rev: str | None
        :param check_rev: Whether to check the revision.
        :type check_rev: bool
        :return: Document ID, body and request headers.
        :rtype: (str, str | body, dict)
        """
        if isinstance(document, dict):
            doc_id = self._extract_id(document)
            rev = rev or document.get("_rev")

            if not check_rev or rev is None:
                return doc_id, doc_id, {}
            else:
                return doc_id, doc_id, {"If-Match": rev}
        else:
            if "/" in document:
                doc_id = self._validate_id(document)
            else:
                doc_id = self._id_prefix + document

            if not check_rev or rev is None:
                return doc_id, doc_id, {}
            else:
                return doc_id, doc_id, {"If-Match": rev}

    def _ensure_key_in_body(self, body: Json) -> Json:
        """Return the document body with "_key" field populated.

        :param body: Document body.
        :type body: dict
        :return: Document body with "_key" field.
        :rtype: dict
        :raise arango.exceptions.DocumentParseError: On missing ID and key.
        """
        if "_key" in body:
            return body
        elif "_id" in body:
            doc_id = self._validate_id(body["_id"])
            body = body.copy()
            body["_key"] = doc_id[len(self._id_prefix) :]
            return body
        raise DocumentParseError('field "_key" or "_id" required')

    def _ensure_key_from_id(self, body: Json) -> Json:
        """Return the body with "_key" field if it has "_id" field.

        :param body: Document body.
        :type body: dict
        :return: Document body with "_key" field if it has "_id" field.
        :rtype: dict
        """
        if "_id" in body and "_key" not in body:
            doc_id = self._validate_id(body["_id"])
            body = body.copy()
            body["_key"] = doc_id[len(self._id_prefix) :]
        return body

    @property
    def name(self) -> str:
        """Return collection name.

        :return: Collection name.
        :rtype: str
        """
        return self._name

    def recalculate_count(self) -> Result[bool]:
        """Recalculate the document count.

        :return: True if recalculation was successful.
        :rtype: bool
        :raise arango.exceptions.CollectionRecalculateCountError: If operation fails.
        """
        request = Request(
            method="put",
            endpoint=f"/_api/collection/{self.name}/recalculateCount",
        )

        def response_handler(resp: Response) -> bool:
            if resp.is_success:
                return True
            raise CollectionRecalculateCountError(resp, request)

        return self._execute(request, response_handler)

    def responsible_shard(self, document: Json) -> Result[str]:  # pragma: no cover
        """Return the ID of the shard responsible for given **document**.

        If the document does not exist, return the shard that would be
        responsible.

        :return: Shard ID
        :rtype: str
        """
        request = Request(
            method="put",
            endpoint=f"/_api/collection/{self.name}/responsibleShard",
            data=document,
            read=self.name,
        )

        def response_handler(resp: Response) -> str:
            if resp.is_success:
                return str(resp.body["shardId"])
            raise CollectionResponsibleShardError(resp, request)

        return self._execute(request, response_handler)

    def rename(self, new_name: str) -> Result[bool]:
        """Rename the collection.

        Renames may not be reflected immediately in async execution, batch
        execution or transactions. It is recommended to initialize new API
        wrappers after a rename.

        :param new_name: New collection name.
        :type new_name: str
        :return: True if collection was renamed successfully.
        :rtype: bool
        :raise arango.exceptions.CollectionRenameError: If rename fails.
        """
        request = Request(
            method="put",
            endpoint=f"/_api/collection/{self.name}/rename",
            data={"name": new_name},
        )

        def response_handler(resp: Response) -> bool:
            if not resp.is_success:
                raise CollectionRenameError(resp, request)
            self._name = new_name
            self._id_prefix = new_name + "/"
            return True

        return self._execute(request, response_handler)

    def properties(self) -> Result[Json]:
        """Return collection properties.

        :return: Collection properties.
        :rtype: dict
        :raise arango.exceptions.CollectionPropertiesError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint=f"/_api/collection/{self.name}/properties",
            read=self.name,
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_collection(resp.body)
            raise CollectionPropertiesError(resp, request)

        return self._execute(request, response_handler)

    def configure(
        self, sync: Optional[bool] = None, schema: Optional[Json] = None
    ) -> Result[Json]:
        """Configure collection properties.

        :param sync: Block until operations are synchronized to disk.
        :type sync: bool | None
        :param schema: document schema for validation of objects.
        :type schema: dict
        :return: New collection properties.
        :rtype: dict
        :raise arango.exceptions.CollectionConfigureError: If operation fails.
        """
        data: Json = {}
        if sync is not None:
            data["waitForSync"] = sync
        if schema is not None:
            data["schema"] = schema

        request = Request(
            method="put",
            endpoint=f"/_api/collection/{self.name}/properties",
            data=data,
        )

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise CollectionConfigureError(resp, request)
            return format_collection(resp.body)

        return self._execute(request, response_handler)

    def statistics(self) -> Result[Json]:
        """Return collection statistics.

        :return: Collection statistics.
        :rtype: dict
        :raise arango.exceptions.CollectionStatisticsError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint=f"/_api/collection/{self.name}/figures",
            read=self.name,
        )

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise CollectionStatisticsError(resp, request)

            stats: Json = resp.body.get("figures", resp.body)
            if "documentReferences" in stats:  # pragma: no cover
                stats["document_refs"] = stats.pop("documentReferences")
            if "lastTick" in stats:  # pragma: no cover
                stats["last_tick"] = stats.pop("lastTick")
            if "waitingFor" in stats:  # pragma: no cover
                stats["waiting_for"] = stats.pop("waitingFor")
            if "documentsSize" in stats:  # pragma: no cover
                stats["documents_size"] = stats.pop("documentsSize")
            if "cacheInUse" in stats:  # pragma: no cover
                stats["cache_in_use"] = stats.pop("cacheInUse")
            if "cacheSize" in stats:  # pragma: no cover
                stats["cache_size"] = stats.pop("cacheSize")
            if "cacheUsage" in stats:  # pragma: no cover
                stats["cache_usage"] = stats.pop("cacheUsage")
            if "uncollectedLogfileEntries" in stats:  # pragma: no cover
                stats["uncollected_logfile_entries"] = stats.pop(
                    "uncollectedLogfileEntries"
                )
            return stats

        return self._execute(request, response_handler)

    def revision(self) -> Result[str]:
        """Return collection revision.

        :return: Collection revision.
        :rtype: str
        :raise arango.exceptions.CollectionRevisionError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint=f"/_api/collection/{self.name}/revision",
            read=self.name,
        )

        def response_handler(resp: Response) -> str:
            if resp.is_success:
                return str(resp.body["revision"])
            raise CollectionRevisionError(resp, request)

        return self._execute(request, response_handler)

    def checksum(self, with_rev: bool = False, with_data: bool = False) -> Result[str]:
        """Return collection checksum.

        :param with_rev: Include document revisions in checksum calculation.
        :type with_rev: bool
        :param with_data: Include document data in checksum calculation.
        :type with_data: bool
        :return: Collection checksum.
        :rtype: str
        :raise arango.exceptions.CollectionChecksumError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint=f"/_api/collection/{self.name}/checksum",
            params={"withRevision": with_rev, "withData": with_data},
        )

        def response_handler(resp: Response) -> str:
            if resp.is_success:
                return str(resp.body["checksum"])
            raise CollectionChecksumError(resp, request)

        return self._execute(request, response_handler)

    def load(self) -> Result[bool]:
        """Load the collection into memory.

        :return: True if collection was loaded successfully.
        :rtype: bool
        :raise arango.exceptions.CollectionLoadError: If operation fails.
        """
        request = Request(method="put", endpoint=f"/_api/collection/{self.name}/load")

        def response_handler(resp: Response) -> bool:
            if not resp.is_success:
                raise CollectionLoadError(resp, request)
            return True

        return self._execute(request, response_handler)

    def unload(self) -> Result[bool]:
        """Unload the collection from memory.

        :return: True if collection was unloaded successfully.
        :rtype: bool
        :raise arango.exceptions.CollectionUnloadError: If operation fails.
        """
        request = Request(method="put", endpoint=f"/_api/collection/{self.name}/unload")

        def response_handler(resp: Response) -> bool:
            if not resp.is_success:
                raise CollectionUnloadError(resp, request)
            return True

        return self._execute(request, response_handler)

    def truncate(self) -> Result[bool]:
        """Delete all documents in the collection.

        :return: True if collection was truncated successfully.
        :rtype: bool
        :raise arango.exceptions.CollectionTruncateError: If operation fails.
        """
        request = Request(
            method="put", endpoint=f"/_api/collection/{self.name}/truncate"
        )

        def response_handler(resp: Response) -> bool:
            if not resp.is_success:
                raise CollectionTruncateError(resp, request)
            return True

        return self._execute(request, response_handler)

    def count(self) -> Result[int]:
        """Return the total document count.

        :return: Total document count.
        :rtype: int
        :raise arango.exceptions.DocumentCountError: If retrieval fails.
        """
        request = Request(method="get", endpoint=f"/_api/collection/{self.name}/count")

        def response_handler(resp: Response) -> int:
            if resp.is_success:
                result: int = resp.body["count"]
                return result
            raise DocumentCountError(resp, request)

        return self._execute(request, response_handler)

    def has(
        self,
        document: Union[str, Json],
        rev: Optional[str] = None,
        check_rev: bool = True,
    ) -> Result[bool]:
        """Check if a document exists in the collection.

        :param document: Document ID, key or body. Document body must contain
            the "_id" or "_key" field.
        :type document: str | dict
        :param rev: Expected document revision. Overrides value of "_rev" field
            in **document** if present.
        :type rev: str | None
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :return: True if document exists, False otherwise.
        :rtype: bool
        :raise arango.exceptions.DocumentInError: If check fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        handle, body, headers = self._prep_from_doc(document, rev, check_rev)

        request = Request(
            method="get",
            endpoint=f"/_api/document/{handle}",
            headers=headers,
            read=self.name,
        )

        def response_handler(resp: Response) -> bool:
            if resp.error_code == 1202:
                return False
            if resp.status_code == 412:
                raise DocumentRevisionError(resp, request)
            if not resp.is_success:
                raise DocumentInError(resp, request)
            return bool(resp.body)

        return self._execute(request, response_handler)

    def ids(self) -> Result[Cursor]:
        """Return the IDs of all documents in the collection.

        :return: Document ID cursor.
        :rtype: arango.cursor.Cursor
        :raise arango.exceptions.DocumentIDsError: If retrieval fails.
        """
        request = Request(
            method="put",
            endpoint="/_api/simple/all-keys",
            data={"collection": self.name, "type": "id"},
            read=self.name,
        )

        def response_handler(resp: Response) -> Cursor:
            if not resp.is_success:
                raise DocumentIDsError(resp, request)
            return Cursor(self._conn, resp.body)

        return self._execute(request, response_handler)

    def keys(self) -> Result[Cursor]:
        """Return the keys of all documents in the collection.

        :return: Document key cursor.
        :rtype: arango.cursor.Cursor
        :raise arango.exceptions.DocumentKeysError: If retrieval fails.
        """
        request = Request(
            method="put",
            endpoint="/_api/simple/all-keys",
            data={"collection": self.name, "type": "key"},
            read=self.name,
        )

        def response_handler(resp: Response) -> Cursor:
            if not resp.is_success:
                raise DocumentKeysError(resp, request)
            return Cursor(self._conn, resp.body)

        return self._execute(request, response_handler)

    def all(
        self, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> Result[Cursor]:
        """Return all documents in the collection.

        :param skip: Number of documents to skip.
        :type skip: int | None
        :param limit: Max number of documents returned.
        :type limit: int | None
        :return: Document cursor.
        :rtype: arango.cursor.Cursor
        :raise arango.exceptions.DocumentGetError: If retrieval fails.
        """
        assert is_none_or_int(skip), "skip must be a non-negative int"
        assert is_none_or_int(limit), "limit must be a non-negative int"

        data: Json = {"collection": self.name}
        if skip is not None:
            data["skip"] = skip
        if limit is not None:
            data["limit"] = limit

        request = Request(
            method="put", endpoint="/_api/simple/all", data=data, read=self.name
        )

        def response_handler(resp: Response) -> Cursor:
            if not resp.is_success:
                raise DocumentGetError(resp, request)
            return Cursor(self._conn, resp.body)

        return self._execute(request, response_handler)

    def export(
        self,
        limit: Optional[int] = None,
        count: bool = False,
        batch_size: Optional[int] = None,
        flush: bool = False,
        flush_wait: Optional[int] = None,
        ttl: Optional[Number] = None,
        filter_fields: Optional[Sequence[str]] = None,
        filter_type: str = "include",
    ) -> Result[Cursor]:
        """Export all documents in the collection using a server cursor.

        :param flush: If set to True, flush the write-ahead log prior to the
            export. If set to False, documents in the write-ahead log during
            the export are not included in the result.
        :type flush: bool
        :param flush_wait: Max wait time in seconds for write-ahead log flush.
        :type flush_wait: int | None
        :param count: Include the document count in the server cursor.
        :type count: bool
        :param batch_size: Max number of documents in the batch fetched by
            the cursor in one round trip.
        :type batch_size: int | None
        :param limit: Max number of documents fetched by the cursor.
        :type limit: int | None
        :param ttl: Time-to-live for the cursor on the server.
        :type ttl: int | float | None
        :param filter_fields: Document fields to filter with.
        :type filter_fields: [str] | None
        :param filter_type: Allowed values are "include" or "exclude".
        :type filter_type: str
        :return: Document cursor.
        :rtype: arango.cursor.Cursor
        :raise arango.exceptions.DocumentGetError: If export fails.
        """
        data: Json = {"count": count, "flush": flush}
        if flush_wait is not None:
            data["flushWait"] = flush_wait
        if batch_size is not None:
            data["batchSize"] = batch_size
        if limit is not None:
            data["limit"] = limit
        if ttl is not None:
            data["ttl"] = ttl
        if filter_fields is not None:
            data["restrict"] = {"fields": filter_fields, "type": filter_type}
        request = Request(
            method="post",
            endpoint="/_api/export",
            params={"collection": self.name},
            data=data,
        )

        def response_handler(resp: Response) -> Cursor:
            if not resp.is_success:
                raise DocumentGetError(resp, request)
            return Cursor(self._conn, resp.body, "export")

        return self._execute(request, response_handler)

    def find(
        self, filters: Json, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> Result[Cursor]:
        """Return all documents that match the given filters.

        :param filters: Document filters.
        :type filters: dict
        :param skip: Number of documents to skip.
        :type skip: int | None
        :param limit: Max number of documents returned.
        :type limit: int | None
        :return: Document cursor.
        :rtype: arango.cursor.Cursor
        :raise arango.exceptions.DocumentGetError: If retrieval fails.
        """
        assert isinstance(filters, dict), "filters must be a dict"
        assert is_none_or_int(skip), "skip must be a non-negative int"
        assert is_none_or_int(limit), "limit must be a non-negative int"

        data: Json = {
            "collection": self.name,
            "example": filters,
            "skip": skip,
        }
        if limit is not None:
            data["limit"] = limit

        request = Request(
            method="put", endpoint="/_api/simple/by-example", data=data, read=self.name
        )

        def response_handler(resp: Response) -> Cursor:
            if not resp.is_success:
                raise DocumentGetError(resp, request)
            return Cursor(self._conn, resp.body)

        return self._execute(request, response_handler)

    def find_near(
        self, latitude: Number, longitude: Number, limit: Optional[int] = None
    ) -> Result[Cursor]:
        """Return documents near a given coordinate.

        Documents returned are sorted according to distance, with the nearest
        document being the first. If there are documents of equal distance,
        they are randomly chosen from the set until the limit is reached. A geo
        index must be defined in the collection to use this method.

        :param latitude: Latitude.
        :type latitude: int | float
        :param longitude: Longitude.
        :type longitude: int | float
        :param limit: Max number of documents returned.
        :type limit: int | None
        :returns: Document cursor.
        :rtype: arango.cursor.Cursor
        :raises arango.exceptions.DocumentGetError: If retrieval fails.
        """
        assert isinstance(latitude, Number), "latitude must be a number"
        assert isinstance(longitude, Number), "longitude must be a number"
        assert is_none_or_int(limit), "limit must be a non-negative int"

        query = """
        FOR doc IN NEAR(@collection, @latitude, @longitude{})
            RETURN doc
        """.format(
            "" if limit is None else ", @limit "
        )

        bind_vars = {
            "collection": self._name,
            "latitude": latitude,
            "longitude": longitude,
        }
        if limit is not None:
            bind_vars["limit"] = limit

        request = Request(
            method="post",
            endpoint="/_api/cursor",
            data={"query": query, "bindVars": bind_vars, "count": True},
            read=self.name,
        )

        def response_handler(resp: Response) -> Cursor:
            if not resp.is_success:
                raise DocumentGetError(resp, request)
            return Cursor(self._conn, resp.body)

        return self._execute(request, response_handler)

    def find_in_range(
        self,
        field: str,
        lower: int,
        upper: int,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Result[Cursor]:
        """Return documents within a given range in a random order.

        A skiplist index must be defined in the collection to use this method.

        :param field: Document field name.
        :type field: str
        :param lower: Lower bound (inclusive).
        :type lower: int
        :param upper: Upper bound (exclusive).
        :type upper: int
        :param skip: Number of documents to skip.
        :type skip: int | None
        :param limit: Max number of documents returned.
        :type limit: int | None
        :returns: Document cursor.
        :rtype: arango.cursor.Cursor
        :raises arango.exceptions.DocumentGetError: If retrieval fails.
        """
        assert is_none_or_int(skip), "skip must be a non-negative int"
        assert is_none_or_int(limit), "limit must be a non-negative int"

        bind_vars = {
            "@collection": self._name,
            "field": field,
            "lower": lower,
            "upper": upper,
            "skip": 0 if skip is None else skip,
            "limit": 2147483647 if limit is None else limit,  # 2 ^ 31 - 1
        }

        query = """
        FOR doc IN @@collection
            FILTER doc.@field >= @lower && doc.@field < @upper
            LIMIT @skip, @limit
            RETURN doc
        """

        request = Request(
            method="post",
            endpoint="/_api/cursor",
            data={"query": query, "bindVars": bind_vars, "count": True},
            read=self.name,
        )

        def response_handler(resp: Response) -> Cursor:
            if not resp.is_success:
                raise DocumentGetError(resp, request)
            return Cursor(self._conn, resp.body)

        return self._execute(request, response_handler)

    def find_in_radius(
        self,
        latitude: Number,
        longitude: Number,
        radius: Number,
        distance_field: Optional[str] = None,
    ) -> Result[Cursor]:
        """Return documents within a given radius around a coordinate.

        A geo index must be defined in the collection to use this method.

        :param latitude: Latitude.
        :type latitude: int | float
        :param longitude: Longitude.
        :type longitude: int | float
        :param radius: Max radius.
        :type radius: int | float
        :param distance_field: Document field used to indicate the distance to
            the given coordinate. This parameter is ignored in transactions.
        :type distance_field: str
        :returns: Document cursor.
        :rtype: arango.cursor.Cursor
        :raises arango.exceptions.DocumentGetError: If retrieval fails.
        """
        assert isinstance(latitude, Number), "latitude must be a number"
        assert isinstance(longitude, Number), "longitude must be a number"
        assert isinstance(radius, Number), "radius must be a number"
        assert is_none_or_str(distance_field), "distance_field must be a str"

        query = """
        FOR doc IN WITHIN(@@collection, @latitude, @longitude, @radius{})
            RETURN doc
        """.format(
            "" if distance_field is None else ", @distance"
        )

        bind_vars = {
            "@collection": self._name,
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius,
        }
        if distance_field is not None:
            bind_vars["distance"] = distance_field

        request = Request(
            method="post",
            endpoint="/_api/cursor",
            data={"query": query, "bindVars": bind_vars, "count": True},
            read=self.name,
        )

        def response_handler(resp: Response) -> Cursor:
            if not resp.is_success:
                raise DocumentGetError(resp, request)
            return Cursor(self._conn, resp.body)

        return self._execute(request, response_handler)

    def find_in_box(
        self,
        latitude1: Number,
        longitude1: Number,
        latitude2: Number,
        longitude2: Number,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        index: Optional[str] = None,
    ) -> Result[Cursor]:
        """Return all documents in an rectangular area.

        :param latitude1: First latitude.
        :type latitude1: int | float
        :param longitude1: First longitude.
        :type longitude1: int | float
        :param latitude2: Second latitude.
        :type latitude2: int | float
        :param longitude2: Second longitude
        :type longitude2: int | float
        :param skip: Number of documents to skip.
        :type skip: int | None
        :param limit: Max number of documents returned.
        :type limit: int | None
        :param index: ID of the geo index to use (without the collection
            prefix). This parameter is ignored in transactions.
        :type index: str | None
        :returns: Document cursor.
        :rtype: arango.cursor.Cursor
        :raises arango.exceptions.DocumentGetError: If retrieval fails.
        """
        assert isinstance(latitude1, Number), "latitude1 must be a number"
        assert isinstance(longitude1, Number), "longitude1 must be a number"
        assert isinstance(latitude2, Number), "latitude2 must be a number"
        assert isinstance(longitude2, Number), "longitude2 must be a number"
        assert is_none_or_int(skip), "skip must be a non-negative int"
        assert is_none_or_int(limit), "limit must be a non-negative int"

        data: Json = {
            "collection": self._name,
            "latitude1": latitude1,
            "longitude1": longitude1,
            "latitude2": latitude2,
            "longitude2": longitude2,
        }
        if skip is not None:
            data["skip"] = skip
        if limit is not None:
            data["limit"] = limit
        if index is not None:
            data["geo"] = self._name + "/" + index

        request = Request(
            method="put",
            endpoint="/_api/simple/within-rectangle",
            data=data,
            read=self.name,
        )

        def response_handler(resp: Response) -> Cursor:
            if not resp.is_success:
                raise DocumentGetError(resp, request)
            return Cursor(self._conn, resp.body)

        return self._execute(request, response_handler)

    def find_by_text(
        self, field: str, query: str, limit: Optional[int] = None
    ) -> Result[Cursor]:
        """Return documents that match the given fulltext query.

        :param field: Document field with fulltext index.
        :type field: str
        :param query: Fulltext query.
        :type query: str
        :param limit: Max number of documents returned.
        :type limit: int | None
        :returns: Document cursor.
        :rtype: arango.cursor.Cursor
        :raises arango.exceptions.DocumentGetError: If retrieval fails.
        """
        assert is_none_or_int(limit), "limit must be a non-negative int"

        bind_vars: Json = {
            "collection": self._name,
            "field": field,
            "query": query,
        }
        if limit is not None:
            bind_vars["limit"] = limit

        aql = """
        FOR doc IN FULLTEXT(@collection, @field, @query{})
            RETURN doc
        """.format(
            "" if limit is None else ", @limit"
        )

        request = Request(
            method="post",
            endpoint="/_api/cursor",
            data={"query": aql, "bindVars": bind_vars, "count": True},
            read=self.name,
        )

        def response_handler(resp: Response) -> Cursor:
            if not resp.is_success:
                raise DocumentGetError(resp, request)
            return Cursor(self._conn, resp.body)

        return self._execute(request, response_handler)

    def get_many(self, documents: Sequence[Union[str, Json]]) -> Result[List[Json]]:
        """Return multiple documents ignoring any missing ones.

        :param documents: List of document keys, IDs or bodies. Document bodies
            must contain the "_id" or "_key" fields.
        :type documents: [str | dict]
        :return: Documents. Missing ones are not included.
        :rtype: [dict]
        :raise arango.exceptions.DocumentGetError: If retrieval fails.
        """
        handles = [self._extract_id(d) if isinstance(d, dict) else d for d in documents]

        request = Request(
            method="put",
            endpoint="/_api/simple/lookup-by-keys",
            data={"collection": self.name, "keys": handles},
            read=self.name,
        )

        def response_handler(resp: Response) -> List[Json]:
            if not resp.is_success:
                raise DocumentGetError(resp, request)
            docs = resp.body["documents"]
            return [doc for doc in docs if "_id" in doc]

        return self._execute(request, response_handler)

    def random(self) -> Result[Json]:
        """Return a random document from the collection.

        :return: A random document.
        :rtype: dict
        :raise arango.exceptions.DocumentGetError: If retrieval fails.
        """
        request = Request(
            method="put",
            endpoint="/_api/simple/any",
            data={"collection": self.name},
            read=self.name,
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                result: Json = resp.body["document"]
                return result
            raise DocumentGetError(resp, request)

        return self._execute(request, response_handler)

    ####################
    # Index Management #
    ####################

    def indexes(self) -> Result[List[Json]]:
        """Return the collection indexes.

        :return: Collection indexes.
        :rtype: [dict]
        :raise arango.exceptions.IndexListError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint="/_api/index",
            params={"collection": self.name},
        )

        def response_handler(resp: Response) -> List[Json]:
            if not resp.is_success:
                raise IndexListError(resp, request)
            result = resp.body["indexes"]
            return [format_index(index) for index in result]

        return self._execute(request, response_handler)

    def _add_index(self, data: Json) -> Result[Json]:
        """Helper method for creating a new index.

        :param data: Index data.
        :type data: dict
        :return: New index details.
        :rtype: dict
        :raise arango.exceptions.IndexCreateError: If create fails.
        """
        request = Request(
            method="post",
            endpoint="/_api/index",
            data=data,
            params={"collection": self.name},
        )

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise IndexCreateError(resp, request)
            return format_index(resp.body)

        return self._execute(request, response_handler)

    def add_hash_index(
        self,
        fields: Sequence[str],
        unique: Optional[bool] = None,
        sparse: Optional[bool] = None,
        deduplicate: Optional[bool] = None,
        name: Optional[str] = None,
        in_background: Optional[bool] = None,
    ) -> Result[Json]:
        """Create a new hash index.

        :param fields: Document fields to index.
        :type fields: [str]
        :param unique: Whether the index is unique.
        :type unique: bool | None
        :param sparse: If set to True, documents with None in the field
            are also indexed. If set to False, they are skipped.
        :type sparse: bool | None
        :param deduplicate: If set to True, inserting duplicate index values
            from the same document triggers unique constraint errors.
        :type deduplicate: bool | None
        :param name: Optional name for the index.
        :type name: str | None
        :param in_background: Do not hold the collection lock.
        :type in_background: bool | None
        :return: New index details.
        :rtype: dict
        :raise arango.exceptions.IndexCreateError: If create fails.
        """
        data: Json = {"type": "hash", "fields": fields}

        if unique is not None:
            data["unique"] = unique
        if sparse is not None:
            data["sparse"] = sparse
        if deduplicate is not None:
            data["deduplicate"] = deduplicate
        if name is not None:
            data["name"] = name
        if in_background is not None:
            data["inBackground"] = in_background

        return self._add_index(data)

    def add_skiplist_index(
        self,
        fields: Sequence[str],
        unique: Optional[bool] = None,
        sparse: Optional[bool] = None,
        deduplicate: Optional[bool] = None,
        name: Optional[str] = None,
        in_background: Optional[bool] = None,
    ) -> Result[Json]:
        """Create a new skiplist index.

        :param fields: Document fields to index.
        :type fields: [str]
        :param unique: Whether the index is unique.
        :type unique: bool | None
        :param sparse: If set to True, documents with None in the field
            are also indexed. If set to False, they are skipped.
        :type sparse: bool | None
        :param deduplicate: If set to True, inserting duplicate index values
            from the same document triggers unique constraint errors.
        :type deduplicate: bool | None
        :param name: Optional name for the index.
        :type name: str | None
        :param in_background: Do not hold the collection lock.
        :type in_background: bool | None
        :return: New index details.
        :rtype: dict
        :raise arango.exceptions.IndexCreateError: If create fails.
        """
        data: Json = {"type": "skiplist", "fields": fields}

        if unique is not None:
            data["unique"] = unique
        if sparse is not None:
            data["sparse"] = sparse
        if deduplicate is not None:
            data["deduplicate"] = deduplicate
        if name is not None:
            data["name"] = name
        if in_background is not None:
            data["inBackground"] = in_background

        return self._add_index(data)

    def add_geo_index(
        self,
        fields: Fields,
        ordered: Optional[bool] = None,
        name: Optional[str] = None,
        in_background: Optional[bool] = None,
    ) -> Result[Json]:
        """Create a new geo-spatial index.

        :param fields: A single document field or a list of document fields. If
            a single field is given, the field must have values that are lists
            with at least two floats. Documents with missing fields or invalid
            values are excluded.
        :type fields: str | [str]
        :param ordered: Whether the order is longitude, then latitude.
        :type ordered: bool | None
        :param name: Optional name for the index.
        :type name: str | None
        :param in_background: Do not hold the collection lock.
        :type in_background: bool | None
        :return: New index details.
        :rtype: dict
        :raise arango.exceptions.IndexCreateError: If create fails.
        """
        data: Json = {"type": "geo", "fields": fields}

        if ordered is not None:
            data["geoJson"] = ordered
        if name is not None:
            data["name"] = name
        if in_background is not None:
            data["inBackground"] = in_background

        return self._add_index(data)

    def add_fulltext_index(
        self,
        fields: Sequence[str],
        min_length: Optional[int] = None,
        name: Optional[str] = None,
        in_background: Optional[bool] = None,
    ) -> Result[Json]:
        """Create a new fulltext index.

        :param fields: Document fields to index.
        :type fields: [str]
        :param min_length: Minimum number of characters to index.
        :type min_length: int | None
        :param name: Optional name for the index.
        :type name: str | None
        :param in_background: Do not hold the collection lock.
        :type in_background: bool | None
        :return: New index details.
        :rtype: dict
        :raise arango.exceptions.IndexCreateError: If create fails.
        """
        data: Json = {"type": "fulltext", "fields": fields}

        if min_length is not None:
            data["minLength"] = min_length
        if name is not None:
            data["name"] = name
        if in_background is not None:
            data["inBackground"] = in_background

        return self._add_index(data)

    def add_persistent_index(
        self,
        fields: Sequence[str],
        unique: Optional[bool] = None,
        sparse: Optional[bool] = None,
        name: Optional[str] = None,
        in_background: Optional[bool] = None,
    ) -> Result[Json]:
        """Create a new persistent index.

        Unique persistent indexes on non-sharded keys are not supported in a
        cluster.

        :param fields: Document fields to index.
        :type fields: [str]
        :param unique: Whether the index is unique.
        :type unique: bool | None
        :param sparse: Exclude documents that do not contain at least one of
            the indexed fields, or documents that have a value of None in any
            of the indexed fields.
        :type sparse: bool | None
        :param name: Optional name for the index.
        :type name: str | None
        :param in_background: Do not hold the collection lock.
        :type in_background: bool | None
        :return: New index details.
        :rtype: dict
        :raise arango.exceptions.IndexCreateError: If create fails.
        """
        data: Json = {"type": "persistent", "fields": fields}

        if unique is not None:
            data["unique"] = unique
        if sparse is not None:
            data["sparse"] = sparse
        if name is not None:
            data["name"] = name
        if in_background is not None:
            data["inBackground"] = in_background

        return self._add_index(data)

    def add_ttl_index(
        self,
        fields: Sequence[str],
        expiry_time: int,
        name: Optional[str] = None,
        in_background: Optional[bool] = None,
    ) -> Result[Json]:
        """Create a new TTL (time-to-live) index.

        :param fields: Document field to index.
        :type fields: [str]
        :param expiry_time: Time of expiry in seconds after document creation.
        :type expiry_time: int
        :param name: Optional name for the index.
        :type name: str | None
        :param in_background: Do not hold the collection lock.
        :type in_background: bool | None
        :return: New index details.
        :rtype: dict
        :raise arango.exceptions.IndexCreateError: If create fails.
        """
        data: Json = {"type": "ttl", "fields": fields, "expireAfter": expiry_time}

        if name is not None:
            data["name"] = name
        if in_background is not None:
            data["inBackground"] = in_background

        return self._add_index(data)

    def delete_index(self, index_id: str, ignore_missing: bool = False) -> Result[bool]:
        """Delete an index.

        :param index_id: Index ID.
        :type index_id: str
        :param ignore_missing: Do not raise an exception on missing index.
        :type ignore_missing: bool
        :return: True if index was deleted successfully, False if index was
            not found and **ignore_missing** was set to True.
        :rtype: bool
        :raise arango.exceptions.IndexDeleteError: If delete fails.
        """
        request = Request(
            method="delete", endpoint=f"/_api/index/{self.name}/{index_id}"
        )

        def response_handler(resp: Response) -> bool:
            if resp.error_code == 1212 and ignore_missing:
                return False
            if not resp.is_success:
                raise IndexDeleteError(resp, request)
            return True

        return self._execute(request, response_handler)

    def load_indexes(self) -> Result[bool]:
        """Cache all indexes in the collection into memory.

        :return: True if index was loaded successfully.
        :rtype: bool
        :raise arango.exceptions.IndexLoadError: If operation fails.
        """
        request = Request(
            method="put",
            endpoint=f"/_api/collection/{self.name}/loadIndexesIntoMemory",
        )

        def response_handler(resp: Response) -> bool:
            if not resp.is_success:
                raise IndexLoadError(resp, request)
            return True

        return self._execute(request, response_handler)

    def insert_many(
        self,
        documents: Sequence[Json],
        return_new: bool = False,
        sync: Optional[bool] = None,
        silent: bool = False,
        overwrite: bool = False,
        return_old: bool = False,
    ) -> Result[Union[bool, List[Union[Json, ArangoServerError]]]]:
        """Insert multiple documents.

        .. note::

            If inserting a document fails, the exception is not raised but
            returned as an object in the result list. It is up to you to
            inspect the list to determine which documents were inserted
            successfully (returns document metadata) and which were not
            (returns exception object).

        .. note::

            In edge/vertex collections, this method does NOT provide the
            transactional guarantees and validations that single insert
            operation does for graphs. If these properties are required, see
            :func:`arango.database.StandardDatabase.begin_batch_execution`
            for an alternative approach.

        :param documents: List of new documents to insert. If they contain the
            "_key" or "_id" fields, the values are used as the keys of the new
            documents (auto-generated otherwise). Any "_rev" field is ignored.
        :type documents: [dict]
        :param return_new: Include bodies of the new documents in the returned
            metadata. Ignored if parameter **silent** is set to True
        :type return_new: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :param overwrite: If set to True, operation does not fail on duplicate
            keys and the existing documents are replaced.
        :type overwrite: bool
        :param return_old: Include body of the old documents if replaced.
            Applies only when value of **overwrite** is set to True.
        :type return_old: bool
        :return: List of document metadata (e.g. document keys, revisions) and
            any exception, or True if parameter **silent** was set to True.
        :rtype: [dict | ArangoServerError] | bool
        :raise arango.exceptions.DocumentInsertError: If insert fails.
        """
        documents = [self._ensure_key_from_id(doc) for doc in documents]

        params: Params = {
            "returnNew": return_new,
            "silent": silent,
            "overwrite": overwrite,
            "returnOld": return_old,
        }
        if sync is not None:
            params["waitForSync"] = sync

        request = Request(
            method="post",
            endpoint=f"/_api/document/{self.name}",
            data=documents,
            params=params,
        )

        def response_handler(
            resp: Response,
        ) -> Union[bool, List[Union[Json, ArangoServerError]]]:
            if not resp.is_success:
                raise DocumentInsertError(resp, request)
            if silent is True:
                return True

            results: List[Union[Json, ArangoServerError]] = []
            for body in resp.body:
                if "_id" in body:
                    if "_oldRev" in body:
                        body["_old_rev"] = body.pop("_oldRev")
                    results.append(body)
                else:
                    sub_resp = self._conn.prep_bulk_err_response(resp, body)
                    results.append(DocumentInsertError(sub_resp, request))

            return results

        return self._execute(request, response_handler)

    def update_many(
        self,
        documents: Sequence[Json],
        check_rev: bool = True,
        merge: bool = True,
        keep_none: bool = True,
        return_new: bool = False,
        return_old: bool = False,
        sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, List[Union[Json, ArangoServerError]]]]:
        """Update multiple documents.

        .. note::

            If updating a document fails, the exception is not raised but
            returned as an object in the result list. It is up to you to
            inspect the list to determine which documents were updated
            successfully (returns document metadata) and which were not
            (returns exception object).

        .. note::

            In edge/vertex collections, this method does NOT provide the
            transactional guarantees and validations that single update
            operation does for graphs. If these properties are required, see
            :func:`arango.database.StandardDatabase.begin_batch_execution`
            for an alternative approach.

        :param documents: Partial or full documents with the updated values.
            They must contain the "_id" or "_key" fields.
        :type documents: [dict]
        :param check_rev: If set to True, revisions of **documents** (if given)
            are compared against the revisions of target documents.
        :type check_rev: bool
        :param merge: If set to True, sub-dictionaries are merged instead of
            the new ones overwriting the old ones.
        :type merge: bool | None
        :param keep_none: If set to True, fields with value None are retained
            in the document. Otherwise, they are removed completely.
        :type keep_none: bool | None
        :param return_new: Include body of the new document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_new: bool
        :param return_old: Include body of the old document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_old: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: List of document metadata (e.g. document keys, revisions) and
            any exceptions, or True if parameter **silent** was set to True.
        :rtype: [dict | ArangoError] | bool
        :raise arango.exceptions.DocumentUpdateError: If update fails.
        """
        params: Params = {
            "keepNull": keep_none,
            "mergeObjects": merge,
            "returnNew": return_new,
            "returnOld": return_old,
            "ignoreRevs": not check_rev,
            "overwrite": not check_rev,
            "silent": silent,
        }
        if sync is not None:
            params["waitForSync"] = sync

        documents = [self._ensure_key_in_body(doc) for doc in documents]

        request = Request(
            method="patch",
            endpoint=f"/_api/document/{self.name}",
            data=documents,
            params=params,
            write=self.name,
        )

        def response_handler(
            resp: Response,
        ) -> Union[bool, List[Union[Json, ArangoServerError]]]:
            if not resp.is_success:
                raise DocumentUpdateError(resp, request)
            if silent is True:
                return True

            results = []
            for body in resp.body:
                if "_id" in body:
                    body["_old_rev"] = body.pop("_oldRev")
                    results.append(body)
                else:
                    sub_resp = self._conn.prep_bulk_err_response(resp, body)

                    error: ArangoServerError
                    if sub_resp.error_code == 1200:
                        error = DocumentRevisionError(sub_resp, request)
                    else:  # pragma: no cover
                        error = DocumentUpdateError(sub_resp, request)

                    results.append(error)

            return results

        return self._execute(request, response_handler)

    def update_match(
        self,
        filters: Json,
        body: Json,
        limit: Optional[int] = None,
        keep_none: bool = True,
        sync: Optional[bool] = None,
        merge: bool = True,
    ) -> Result[int]:
        """Update matching documents.

        .. note::

            In edge/vertex collections, this method does NOT provide the
            transactional guarantees and validations that single update
            operation does for graphs. If these properties are required, see
            :func:`arango.database.StandardDatabase.begin_batch_execution`
            for an alternative approach.

        :param filters: Document filters.
        :type filters: dict
        :param body: Full or partial document body with the updates.
        :type body: dict
        :param limit: Max number of documents to update. If the limit is lower
            than the number of matched documents, random documents are
            chosen. This parameter is not supported on sharded collections.
        :type limit: int | None
        :param keep_none: If set to True, fields with value None are retained
            in the document. Otherwise, they are removed completely.
        :type keep_none: bool | None
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param merge: If set to True, sub-dictionaries are merged instead of
            the new ones overwriting the old ones.
        :type merge: bool | None
        :return: Number of documents updated.
        :rtype: int
        :raise arango.exceptions.DocumentUpdateError: If update fails.
        """
        data: Json = {
            "collection": self.name,
            "example": filters,
            "newValue": body,
            "keepNull": keep_none,
            "mergeObjects": merge,
        }
        if limit is not None:
            data["limit"] = limit
        if sync is not None:
            data["waitForSync"] = sync

        request = Request(
            method="put",
            endpoint="/_api/simple/update-by-example",
            data=data,
            write=self.name,
        )

        def response_handler(resp: Response) -> int:
            if resp.is_success:
                result: int = resp.body["updated"]
                return result
            raise DocumentUpdateError(resp, request)

        return self._execute(request, response_handler)

    def replace_many(
        self,
        documents: Sequence[Json],
        check_rev: bool = True,
        return_new: bool = False,
        return_old: bool = False,
        sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, List[Union[Json, ArangoServerError]]]]:
        """Replace multiple documents.

        .. note::

            If replacing a document fails, the exception is not raised but
            returned as an object in the result list. It is up to you to
            inspect the list to determine which documents were replaced
            successfully (returns document metadata) and which were not
            (returns exception object).

        .. note::

            In edge/vertex collections, this method does NOT provide the
            transactional guarantees and validations that single replace
            operation does for graphs. If these properties are required, see
            :func:`arango.database.StandardDatabase.begin_batch_execution`
            for an alternative approach.

        :param documents: New documents to replace the old ones with. They must
            contain the "_id" or "_key" fields. Edge documents must also have
            "_from" and "_to" fields.
        :type documents: [dict]
        :param check_rev: If set to True, revisions of **documents** (if given)
            are compared against the revisions of target documents.
        :type check_rev: bool
        :param return_new: Include body of the new document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_new: bool
        :param return_old: Include body of the old document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_old: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: List of document metadata (e.g. document keys, revisions) and
            any exceptions, or True if parameter **silent** was set to True.
        :rtype: [dict | ArangoServerError] | bool
        :raise arango.exceptions.DocumentReplaceError: If replace fails.
        """
        params: Params = {
            "returnNew": return_new,
            "returnOld": return_old,
            "ignoreRevs": not check_rev,
            "overwrite": not check_rev,
            "silent": silent,
        }
        if sync is not None:
            params["waitForSync"] = sync

        documents = [self._ensure_key_in_body(doc) for doc in documents]

        request = Request(
            method="put",
            endpoint=f"/_api/document/{self.name}",
            params=params,
            data=documents,
            write=self.name,
        )

        def response_handler(
            resp: Response,
        ) -> Union[bool, List[Union[Json, ArangoServerError]]]:
            if not resp.is_success:
                raise DocumentReplaceError(resp, request)
            if silent is True:
                return True

            results: List[Union[Json, ArangoServerError]] = []
            for body in resp.body:
                if "_id" in body:
                    body["_old_rev"] = body.pop("_oldRev")
                    results.append(body)
                else:
                    sub_resp = self._conn.prep_bulk_err_response(resp, body)

                    error: ArangoServerError
                    if sub_resp.error_code == 1200:
                        error = DocumentRevisionError(sub_resp, request)
                    else:  # pragma: no cover
                        error = DocumentReplaceError(sub_resp, request)

                    results.append(error)

            return results

        return self._execute(request, response_handler)

    def replace_match(
        self,
        filters: Json,
        body: Json,
        limit: Optional[int] = None,
        sync: Optional[bool] = None,
    ) -> Result[int]:
        """Replace matching documents.

        .. note::

            In edge/vertex collections, this method does NOT provide the
            transactional guarantees and validations that single replace
            operation does for graphs. If these properties are required, see
            :func:`arango.database.StandardDatabase.begin_batch_execution`
            for an alternative approach.

        :param filters: Document filters.
        :type filters: dict
        :param body: New document body.
        :type body: dict
        :param limit: Max number of documents to replace. If the limit is lower
            than the number of matched documents, random documents are chosen.
        :type limit: int | None
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :return: Number of documents replaced.
        :rtype: int
        :raise arango.exceptions.DocumentReplaceError: If replace fails.
        """
        data: Json = {"collection": self.name, "example": filters, "newValue": body}
        if limit is not None:
            data["limit"] = limit
        if sync is not None:
            data["waitForSync"] = sync

        request = Request(
            method="put",
            endpoint="/_api/simple/replace-by-example",
            data=data,
            write=self.name,
        )

        def response_handler(resp: Response) -> int:
            if not resp.is_success:
                raise DocumentReplaceError(resp, request)
            result: int = resp.body["replaced"]
            return result

        return self._execute(request, response_handler)

    def delete_many(
        self,
        documents: Sequence[Json],
        return_old: bool = False,
        check_rev: bool = True,
        sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, List[Union[Json, ArangoServerError]]]]:
        """Delete multiple documents.

        .. note::

            If deleting a document fails, the exception is not raised but
            returned as an object in the result list. It is up to you to
            inspect the list to determine which documents were deleted
            successfully (returns document metadata) and which were not
            (returns exception object).

        .. note::

            In edge/vertex collections, this method does NOT provide the
            transactional guarantees and validations that single delete
            operation does for graphs. If these properties are required, see
            :func:`arango.database.StandardDatabase.begin_batch_execution`
            for an alternative approach.

        :param documents: Document IDs, keys or bodies. Document bodies must
            contain the "_id" or "_key" fields.
        :type documents: [str | dict]
        :param return_old: Include bodies of the old documents in the result.
        :type return_old: bool
        :param check_rev: If set to True, revisions of **documents** (if given)
            are compared against the revisions of target documents.
        :type check_rev: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: List of document metadata (e.g. document keys, revisions) and
            any exceptions, or True if parameter **silent** was set to True.
        :rtype: [dict | ArangoServerError] | bool
        :raise arango.exceptions.DocumentDeleteError: If delete fails.
        """
        params: Params = {
            "returnOld": return_old,
            "ignoreRevs": not check_rev,
            "overwrite": not check_rev,
            "silent": silent,
        }
        if sync is not None:
            params["waitForSync"] = sync

        documents = [
            self._ensure_key_in_body(doc) if isinstance(doc, dict) else doc
            for doc in documents
        ]

        request = Request(
            method="delete",
            endpoint=f"/_api/document/{self.name}",
            params=params,
            data=documents,
            write=self.name,
        )

        def response_handler(
            resp: Response,
        ) -> Union[bool, List[Union[Json, ArangoServerError]]]:
            if not resp.is_success:
                raise DocumentDeleteError(resp, request)
            if silent is True:
                return True

            results: List[Union[Json, ArangoServerError]] = []
            for body in resp.body:
                if "_id" in body:
                    results.append(body)
                else:
                    sub_resp = self._conn.prep_bulk_err_response(resp, body)

                    error: ArangoServerError
                    if sub_resp.error_code == 1200:
                        error = DocumentRevisionError(sub_resp, request)
                    else:
                        error = DocumentDeleteError(sub_resp, request)
                    results.append(error)

            return results

        return self._execute(request, response_handler)

    def delete_match(
        self, filters: Json, limit: Optional[int] = None, sync: Optional[bool] = None
    ) -> Result[int]:
        """Delete matching documents.

        .. note::

            In edge/vertex collections, this method does NOT provide the
            transactional guarantees and validations that single delete
            operation does for graphs. If these properties are required, see
            :func:`arango.database.StandardDatabase.begin_batch_execution`
            for an alternative approach.

        :param filters: Document filters.
        :type filters: dict
        :param limit: Max number of documents to delete. If the limit is lower
            than the number of matched documents, random documents are chosen.
        :type limit: int | None
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :return: Number of documents deleted.
        :rtype: int
        :raise arango.exceptions.DocumentDeleteError: If delete fails.
        """
        data: Json = {"collection": self.name, "example": filters}
        if sync is not None:
            data["waitForSync"] = sync
        if limit is not None and limit != 0:
            data["limit"] = limit

        request = Request(
            method="put",
            endpoint="/_api/simple/remove-by-example",
            data=data,
            write=self.name,
        )

        def response_handler(resp: Response) -> int:
            if resp.is_success:
                result: int = resp.body["deleted"]
                return result
            raise DocumentDeleteError(resp, request)

        return self._execute(request, response_handler)

    def import_bulk(
        self,
        documents: Sequence[Json],
        halt_on_error: bool = True,
        details: bool = True,
        from_prefix: Optional[str] = None,
        to_prefix: Optional[str] = None,
        overwrite: Optional[bool] = None,
        on_duplicate: Optional[str] = None,
        sync: Optional[bool] = None,
    ) -> Result[Json]:
        """Insert multiple documents into the collection.

        .. note::

            This method is faster than :func:`arango.collection.Collection.insert_many`
            but does not return as many details.

        .. note::

            In edge/vertex collections, this method does NOT provide the
            transactional guarantees and validations that single insert
            operation does for graphs. If these properties are required, see
            :func:`arango.database.StandardDatabase.begin_batch_execution`
            for an alternative approach.

        :param documents: List of new documents to insert. If they contain the
            "_key" or "_id" fields, the values are used as the keys of the new
            documents (auto-generated otherwise). Any "_rev" field is ignored.
        :type documents: [dict]
        :param halt_on_error: Halt the entire import on an error.
        :type halt_on_error: bool
        :param details: If set to True, the returned result will include an
            additional list of detailed error messages.
        :type details: bool
        :param from_prefix: String prefix prepended to the value of "_from"
            field in each edge document inserted. For example, prefix "foo"
            prepended to "_from": "bar" will result in "_from": "foo/bar".
            Applies only to edge collections.
        :type from_prefix: str
        :param to_prefix: String prefix prepended to the value of "_to" field
            in edge document inserted. For example, prefix "foo" prepended to
            "_to": "bar" will result in "_to": "foo/bar". Applies only to edge
            collections.
        :type to_prefix: str
        :param overwrite: If set to True, all existing documents are removed
            prior to the import. Indexes are still preserved.
        :type overwrite: bool
        :param on_duplicate: Action to take on unique key constraint violations
            (for documents with "_key" fields). Allowed values are "error" (do
            not import the new documents and count them as errors), "update"
            (update the existing documents while preserving any fields missing
            in the new ones), "replace" (replace the existing documents with
            new ones), and  "ignore" (do not import the new documents and count
            them as ignored, as opposed to counting them as errors). Options
            "update" and "replace" may fail on secondary unique key constraint
            violations.
        :type on_duplicate: str
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :return: Result of the bulk import.
        :rtype: dict
        :raise arango.exceptions.DocumentInsertError: If import fails.
        """
        documents = [self._ensure_key_from_id(doc) for doc in documents]

        params: Params = {"type": "array", "collection": self.name}
        if halt_on_error is not None:
            params["complete"] = halt_on_error
        if details is not None:
            params["details"] = details
        if from_prefix is not None:  # pragma: no cover
            params["fromPrefix"] = from_prefix
        if to_prefix is not None:  # pragma: no cover
            params["toPrefix"] = to_prefix
        if overwrite is not None:
            params["overwrite"] = overwrite
        if on_duplicate is not None:
            params["onDuplicate"] = on_duplicate
        if sync is not None:
            params["waitForSync"] = sync

        request = Request(
            method="post",
            endpoint="/_api/import",
            data=documents,
            params=params,
            write=self.name,
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                result: Json = resp.body
                return result
            raise DocumentInsertError(resp, request)

        return self._execute(request, response_handler)


class StandardCollection(Collection):
    """Standard ArangoDB collection API wrapper."""

    def __repr__(self) -> str:
        return f"<StandardCollection {self.name}>"

    def __getitem__(self, key: Union[str, Json]) -> Result[Optional[Json]]:
        return self.get(key)

    def get(
        self,
        document: Union[str, Json],
        rev: Optional[str] = None,
        check_rev: bool = True,
    ) -> Result[Optional[Json]]:
        """Return a document.

        :param document: Document ID, key or body. Document body must contain
            the "_id" or "_key" field.
        :type document: str | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **document** if present.
        :type rev: str | None
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :return: Document, or None if not found.
        :rtype: dict | None
        :raise arango.exceptions.DocumentGetError: If retrieval fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        handle, body, headers = self._prep_from_doc(document, rev, check_rev)

        request = Request(
            method="get",
            endpoint=f"/_api/document/{handle}",
            headers=headers,
            read=self.name,
        )

        def response_handler(resp: Response) -> Optional[Json]:
            if resp.error_code == 1202:
                return None
            if resp.status_code == 412:
                raise DocumentRevisionError(resp, request)
            if not resp.is_success:
                raise DocumentGetError(resp, request)

            result: Json = resp.body
            return result

        return self._execute(request, response_handler)

    def insert(
        self,
        document: Json,
        return_new: bool = False,
        sync: Optional[bool] = None,
        silent: bool = False,
        overwrite: bool = False,
        return_old: bool = False,
        overwrite_mode: Optional[str] = None,
        keep_none: Optional[bool] = None,
        merge: Optional[bool] = None,
    ) -> Result[Union[bool, Json]]:
        """Insert a new document.

        :param document: Document to insert. If it contains the "_key" or "_id"
            field, the value is used as the key of the new document (otherwise
            it is auto-generated). Any "_rev" field is ignored.
        :type document: dict
        :param return_new: Include body of the new document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_new: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :param overwrite: If set to True, operation does not fail on duplicate
            key and existing document is overwritten (replace-insert).
        :type overwrite: bool
        :param return_old: Include body of the old document if overwritten.
            Ignored if parameter **silent** is set to True.
        :type return_old: bool
        :param overwrite_mode: Overwrite behavior used when the document key
            exists already. Allowed values are "replace" (replace-insert) or
            "update" (update-insert). Implicitly sets the value of parameter
            **overwrite**.
        :type overwrite_mode: str | None
        :param keep_none: If set to True, fields with value None are retained
            in the document. Otherwise, they are removed completely. Applies
            only when **overwrite_mode** is set to "update" (update-insert).
        :type keep_none: bool | None
        :param merge: If set to True (default), sub-dictionaries are merged
            instead of the new one overwriting the old one. Applies only when
            **overwrite_mode** is set to "update" (update-insert).
        :type merge: bool | None
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentInsertError: If insert fails.
        """
        document = self._ensure_key_from_id(document)

        params: Params = {
            "returnNew": return_new,
            "silent": silent,
            "overwrite": overwrite,
            "returnOld": return_old,
        }
        if sync is not None:
            params["waitForSync"] = sync
        if overwrite_mode is not None:
            params["overwriteMode"] = overwrite_mode
        if keep_none is not None:
            params["keepNull"] = keep_none
        if merge is not None:
            params["mergeObjects"] = merge

        request = Request(
            method="post",
            endpoint=f"/_api/document/{self.name}",
            data=document,
            params=params,
            write=self.name,
        )

        def response_handler(resp: Response) -> Union[bool, Json]:
            if not resp.is_success:
                raise DocumentInsertError(resp, request)

            if silent:
                return True

            result: Json = resp.body
            if "_oldRev" in result:
                result["_old_rev"] = result.pop("_oldRev")
            return result

        return self._execute(request, response_handler)

    def update(
        self,
        document: Json,
        check_rev: bool = True,
        merge: bool = True,
        keep_none: bool = True,
        return_new: bool = False,
        return_old: bool = False,
        sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Update a document.

        :param document: Partial or full document with the updated values. It
            must contain the "_id" or "_key" field.
        :type document: dict
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :param merge: If set to True, sub-dictionaries are merged instead of
            the new one overwriting the old one.
        :type merge: bool | None
        :param keep_none: If set to True, fields with value None are retained
            in the document. Otherwise, they are removed completely.
        :type keep_none: bool | None
        :param return_new: Include body of the new document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_new: bool
        :param return_old: Include body of the old document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_old: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentUpdateError: If update fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        params: Params = {
            "keepNull": keep_none,
            "mergeObjects": merge,
            "returnNew": return_new,
            "returnOld": return_old,
            "ignoreRevs": not check_rev,
            "overwrite": not check_rev,
            "silent": silent,
        }
        if sync is not None:
            params["waitForSync"] = sync

        request = Request(
            method="patch",
            endpoint=f"/_api/document/{self._extract_id(document)}",
            data=document,
            params=params,
            write=self.name,
        )

        def response_handler(resp: Response) -> Union[bool, Json]:
            if resp.status_code == 412:
                raise DocumentRevisionError(resp, request)
            elif not resp.is_success:
                raise DocumentUpdateError(resp, request)
            if silent is True:
                return True

            result: Json = resp.body
            result["_old_rev"] = result.pop("_oldRev")
            return result

        return self._execute(request, response_handler)

    def replace(
        self,
        document: Json,
        check_rev: bool = True,
        return_new: bool = False,
        return_old: bool = False,
        sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Replace a document.

        :param document: New document to replace the old one with. It must
            contain the "_id" or "_key" field. Edge document must also have
            "_from" and "_to" fields.
        :type document: dict
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :param return_new: Include body of the new document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_new: bool
        :param return_old: Include body of the old document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_old: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentReplaceError: If replace fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        params: Params = {
            "returnNew": return_new,
            "returnOld": return_old,
            "ignoreRevs": not check_rev,
            "overwrite": not check_rev,
            "silent": silent,
        }
        if sync is not None:
            params["waitForSync"] = sync

        request = Request(
            method="put",
            endpoint=f"/_api/document/{self._extract_id(document)}",
            params=params,
            data=document,
            write=self.name,
        )

        def response_handler(resp: Response) -> Union[bool, Json]:
            if resp.status_code == 412:
                raise DocumentRevisionError(resp, request)
            if not resp.is_success:
                raise DocumentReplaceError(resp, request)

            if silent is True:
                return True

            result: Json = resp.body
            if "_oldRev" in result:
                result["_old_rev"] = result.pop("_oldRev")
            return result

        return self._execute(request, response_handler)

    def delete(
        self,
        document: Union[str, Json],
        rev: Optional[str] = None,
        check_rev: bool = True,
        ignore_missing: bool = False,
        return_old: bool = False,
        sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Delete a document.

        :param document: Document ID, key or body. Document body must contain
            the "_id" or "_key" field.
        :type document: str | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **document** if present.
        :type rev: str | None
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :param ignore_missing: Do not raise an exception on missing document.
            This parameter has no effect in transactions where an exception is
            always raised on failures.
        :type ignore_missing: bool
        :param return_old: Include body of the old document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_old: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :return: Document metadata (e.g. document key, revision), or True if
            parameter **silent** was set to True, or False if document was not
            found and **ignore_missing** was set to True (does not apply in
            transactions).
        :rtype: bool | dict
        :raise arango.exceptions.DocumentDeleteError: If delete fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        handle, body, headers = self._prep_from_doc(document, rev, check_rev)

        params: Params = {
            "returnOld": return_old,
            "ignoreRevs": not check_rev,
            "overwrite": not check_rev,
            "silent": silent,
        }
        if sync is not None:
            params["waitForSync"] = sync

        request = Request(
            method="delete",
            endpoint=f"/_api/document/{handle}",
            params=params,
            headers=headers,
            write=self.name,
        )

        def response_handler(resp: Response) -> Union[bool, Json]:
            if resp.error_code == 1202 and ignore_missing:
                return False
            if resp.status_code == 412:
                raise DocumentRevisionError(resp, request)
            if not resp.is_success:
                raise DocumentDeleteError(resp, request)
            return True if silent else resp.body

        return self._execute(request, response_handler)


class VertexCollection(Collection):
    """Vertex collection API wrapper.

    :param connection: HTTP connection.
    :param executor: API executor.
    :param graph: Graph name.
    :param name: Vertex collection name.
    """

    def __init__(
        self, connection: Connection, executor: ApiExecutor, graph: str, name: str
    ) -> None:
        super().__init__(connection, executor, name)
        self._graph = graph

    def __repr__(self) -> str:
        return f"<VertexCollection {self.name}>"

    def __getitem__(self, key: Union[str, Json]) -> Result[Optional[Json]]:
        return self.get(key)

    @property
    def graph(self) -> str:
        """Return the graph name.

        :return: Graph name.
        :rtype: str
        """
        return self._graph

    def get(
        self,
        vertex: Union[str, Json],
        rev: Optional[str] = None,
        check_rev: bool = True,
    ) -> Result[Optional[Json]]:
        """Return a vertex document.

        :param vertex: Vertex document ID, key or body. Document body must
            contain the "_id" or "_key" field.
        :type vertex: str | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **vertex** if present.
        :type rev: str | None
        :param check_rev: If set to True, revision of **vertex** (if given) is
            compared against the revision of target vertex document.
        :type check_rev: bool
        :return: Vertex document or None if not found.
        :rtype: dict | None
        :raise arango.exceptions.DocumentGetError: If retrieval fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        handle, body, headers = self._prep_from_doc(vertex, rev, check_rev)

        request = Request(
            method="get",
            endpoint=f"/_api/gharial/{self._graph}/vertex/{handle}",
            headers=headers,
            read=self.name,
        )

        def response_handler(resp: Response) -> Optional[Json]:
            if resp.error_code == 1202:
                return None
            if resp.status_code == 412:
                raise DocumentRevisionError(resp, request)
            if not resp.is_success:
                raise DocumentGetError(resp, request)
            result: Json = resp.body["vertex"]
            return result

        return self._execute(request, response_handler)

    def insert(
        self,
        vertex: Json,
        sync: Optional[bool] = None,
        silent: bool = False,
        return_new: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Insert a new vertex document.

        :param vertex: New vertex document to insert. If it has "_key" or "_id"
            field, its value is used as key of the new vertex (otherwise it is
            auto-generated). Any "_rev" field is ignored.
        :type vertex: dict
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :param return_new: Include body of the new document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_new: bool
        :return: Document metadata (e.g. document key, revision), or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentInsertError: If insert fails.
        """
        vertex = self._ensure_key_from_id(vertex)

        params: Params = {"silent": silent, "returnNew": return_new}
        if sync is not None:
            params["waitForSync"] = sync

        request = Request(
            method="post",
            endpoint=f"/_api/gharial/{self._graph}/vertex/{self.name}",
            data=vertex,
            params=params,
            write=self.name,
        )

        def response_handler(resp: Response) -> Union[bool, Json]:
            if not resp.is_success:
                raise DocumentInsertError(resp, request)
            if silent:
                return True
            return format_vertex(resp.body)

        return self._execute(request, response_handler)

    def update(
        self,
        vertex: Json,
        check_rev: bool = True,
        keep_none: bool = True,
        sync: Optional[bool] = None,
        silent: bool = False,
        return_old: bool = False,
        return_new: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Update a vertex document.

        :param vertex: Partial or full vertex document with updated values. It
            must contain the "_key" or "_id" field.
        :type vertex: dict
        :param check_rev: If set to True, revision of **vertex** (if given) is
            compared against the revision of target vertex document.
        :type check_rev: bool
        :param keep_none: If set to True, fields with value None are retained
            in the document. If set to False, they are removed completely.
        :type keep_none: bool | None
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :param return_old: Include body of the old document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_old: bool
        :param return_new: Include body of the new document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_new: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentUpdateError: If update fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        vertex_id, headers = self._prep_from_body(vertex, check_rev)

        params: Params = {
            "keepNull": keep_none,
            "overwrite": not check_rev,
            "silent": silent,
            "returnNew": return_new,
            "returnOld": return_old,
        }
        if sync is not None:
            params["waitForSync"] = sync

        request = Request(
            method="patch",
            endpoint=f"/_api/gharial/{self._graph}/vertex/{vertex_id}",
            headers=headers,
            params=params,
            data=vertex,
            write=self.name,
        )

        def response_handler(resp: Response) -> Union[bool, Json]:
            if resp.status_code == 412:  # pragma: no cover
                raise DocumentRevisionError(resp, request)
            elif not resp.is_success:
                raise DocumentUpdateError(resp, request)
            if silent is True:
                return True
            return format_vertex(resp.body)

        return self._execute(request, response_handler)

    def replace(
        self,
        vertex: Json,
        check_rev: bool = True,
        sync: Optional[bool] = None,
        silent: bool = False,
        return_old: bool = False,
        return_new: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Replace a vertex document.

        :param vertex: New vertex document to replace the old one with. It must
            contain the "_key" or "_id" field.
        :type vertex: dict
        :param check_rev: If set to True, revision of **vertex** (if given) is
            compared against the revision of target vertex document.
        :type check_rev: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :param return_old: Include body of the old document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_old: bool
        :param return_new: Include body of the new document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_new: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentReplaceError: If replace fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        vertex_id, headers = self._prep_from_body(vertex, check_rev)

        params: Params = {
            "silent": silent,
            "returnNew": return_new,
            "returnOld": return_old,
        }
        if sync is not None:
            params["waitForSync"] = sync

        request = Request(
            method="put",
            endpoint=f"/_api/gharial/{self._graph}/vertex/{vertex_id}",
            headers=headers,
            params=params,
            data=vertex,
            write=self.name,
        )

        def response_handler(resp: Response) -> Union[bool, Json]:
            if resp.status_code == 412:  # pragma: no cover
                raise DocumentRevisionError(resp, request)
            elif not resp.is_success:
                raise DocumentReplaceError(resp, request)
            if silent is True:
                return True
            return format_vertex(resp.body)

        return self._execute(request, response_handler)

    def delete(
        self,
        vertex: Union[str, Json],
        rev: Optional[str] = None,
        check_rev: bool = True,
        ignore_missing: bool = False,
        sync: Optional[bool] = None,
        return_old: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Delete a vertex document. All connected edges are also deleted.

        :param vertex: Vertex document ID, key or body. Document body must
            contain the "_id" or "_key" field.
        :type vertex: str | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **vertex** if present.
        :type rev: str | None
        :param check_rev: If set to True, revision of **vertex** (if given) is
            compared against the revision of target vertex document.
        :type check_rev: bool
        :param ignore_missing: Do not raise an exception on missing document.
            This parameter has no effect in transactions where an exception is
            always raised on failures.
        :type ignore_missing: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param return_old: Return body of the old document in the result.
        :type return_old: bool
        :return: True if vertex was deleted successfully, False if vertex was
            not found and **ignore_missing** was set to True (does not apply in
            transactions). Old document is returned if **return_old** is set to
            True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentDeleteError: If delete fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        handle, _, headers = self._prep_from_doc(vertex, rev, check_rev)

        params: Params = {"returnOld": return_old}
        if sync is not None:
            params["waitForSync"] = sync

        request = Request(
            method="delete",
            endpoint=f"/_api/gharial/{self._graph}/vertex/{handle}",
            params=params,
            headers=headers,
            write=self.name,
        )

        def response_handler(resp: Response) -> Union[bool, Json]:
            if resp.error_code == 1202 and ignore_missing:
                return False
            if resp.status_code == 412:  # pragma: no cover
                raise DocumentRevisionError(resp, request)
            if not resp.is_success:
                raise DocumentDeleteError(resp, request)

            result: Json = resp.body
            return {"old": result["old"]} if return_old else True

        return self._execute(request, response_handler)


class EdgeCollection(Collection):
    """ArangoDB edge collection API wrapper.

    :param connection: HTTP connection.
    :param executor: API executor.
    :param graph: Graph name.
    :param name: Edge collection name.
    """

    def __init__(
        self, connection: Connection, executor: ApiExecutor, graph: str, name: str
    ) -> None:
        super().__init__(connection, executor, name)
        self._graph = graph

    def __repr__(self) -> str:
        return f"<EdgeCollection {self.name}>"

    def __getitem__(self, key: Union[str, Json]) -> Result[Optional[Json]]:
        return self.get(key)

    @property
    def graph(self) -> str:
        """Return the graph name.

        :return: Graph name.
        :rtype: str
        """
        return self._graph

    def get(
        self, edge: Union[str, Json], rev: Optional[str] = None, check_rev: bool = True
    ) -> Result[Optional[Json]]:
        """Return an edge document.

        :param edge: Edge document ID, key or body. Document body must contain
            the "_id" or "_key" field.
        :type edge: str | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **edge** if present.
        :type rev: str | None
        :param check_rev: If set to True, revision of **edge** (if given) is
            compared against the revision of target edge document.
        :type check_rev: bool
        :return: Edge document or None if not found.
        :rtype: dict | None
        :raise arango.exceptions.DocumentGetError: If retrieval fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        handle, body, headers = self._prep_from_doc(edge, rev, check_rev)

        request = Request(
            method="get",
            endpoint=f"/_api/gharial/{self._graph}/edge/{handle}",
            headers=headers,
            read=self.name,
        )

        def response_handler(resp: Response) -> Optional[Json]:
            if resp.error_code == 1202:
                return None
            if resp.status_code == 412:  # pragma: no cover
                raise DocumentRevisionError(resp, request)
            if not resp.is_success:
                raise DocumentGetError(resp, request)

            result: Json = resp.body["edge"]
            return result

        return self._execute(request, response_handler)

    def insert(
        self,
        edge: Json,
        sync: Optional[bool] = None,
        silent: bool = False,
        return_new: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Insert a new edge document.

        :param edge: New edge document to insert. It must contain "_from" and
            "_to" fields. If it has "_key" or "_id" field, its value is used
            as key of the new edge document (otherwise it is auto-generated).
            Any "_rev" field is ignored.
        :type edge: dict
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :param return_new: Include body of the new document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_new: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentInsertError: If insert fails.
        """
        edge = self._ensure_key_from_id(edge)

        params: Params = {"silent": silent, "returnNew": return_new}
        if sync is not None:
            params["waitForSync"] = sync

        request = Request(
            method="post",
            endpoint=f"/_api/gharial/{self._graph}/edge/{self.name}",
            data=edge,
            params=params,
            write=self.name,
        )

        def response_handler(resp: Response) -> Union[bool, Json]:
            if not resp.is_success:
                raise DocumentInsertError(resp, request)
            if silent:
                return True
            return format_edge(resp.body)

        return self._execute(request, response_handler)

    def update(
        self,
        edge: Json,
        check_rev: bool = True,
        keep_none: bool = True,
        sync: Optional[bool] = None,
        silent: bool = False,
        return_old: bool = False,
        return_new: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Update an edge document.

        :param edge: Partial or full edge document with updated values. It must
            contain the "_key" or "_id" field.
        :type edge: dict
        :param check_rev: If set to True, revision of **edge** (if given) is
            compared against the revision of target edge document.
        :type check_rev: bool
        :param keep_none: If set to True, fields with value None are retained
            in the document. If set to False, they are removed completely.
        :type keep_none: bool | None
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :param return_old: Include body of the old document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_old: bool
        :param return_new: Include body of the new document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_new: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentUpdateError: If update fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        edge_id, headers = self._prep_from_body(edge, check_rev)

        params: Params = {
            "keepNull": keep_none,
            "overwrite": not check_rev,
            "silent": silent,
            "returnNew": return_new,
            "returnOld": return_old,
        }
        if sync is not None:
            params["waitForSync"] = sync

        request = Request(
            method="patch",
            endpoint=f"/_api/gharial/{self._graph}/edge/{edge_id}",
            headers=headers,
            params=params,
            data=edge,
            write=self.name,
        )

        def response_handler(resp: Response) -> Union[bool, Json]:
            if resp.status_code == 412:  # pragma: no cover
                raise DocumentRevisionError(resp, request)
            if not resp.is_success:
                raise DocumentUpdateError(resp, request)
            if silent is True:
                return True
            return format_edge(resp.body)

        return self._execute(request, response_handler)

    def replace(
        self,
        edge: Json,
        check_rev: bool = True,
        sync: Optional[bool] = None,
        silent: bool = False,
        return_old: bool = False,
        return_new: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Replace an edge document.

        :param edge: New edge document to replace the old one with. It must
            contain the "_key" or "_id" field. It must also contain the "_from"
            and "_to" fields.
        :type edge: dict
        :param check_rev: If set to True, revision of **edge** (if given) is
            compared against the revision of target edge document.
        :type check_rev: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :param return_old: Include body of the old document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_old: bool
        :param return_new: Include body of the new document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_new: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentReplaceError: If replace fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        edge_id, headers = self._prep_from_body(edge, check_rev)

        params: Params = {
            "silent": silent,
            "returnNew": return_new,
            "returnOld": return_old,
        }
        if sync is not None:
            params["waitForSync"] = sync

        request = Request(
            method="put",
            endpoint=f"/_api/gharial/{self._graph}/edge/{edge_id}",
            headers=headers,
            params=params,
            data=edge,
            write=self.name,
        )

        def response_handler(resp: Response) -> Union[bool, Json]:
            if resp.status_code == 412:  # pragma: no cover
                raise DocumentRevisionError(resp, request)
            if not resp.is_success:
                raise DocumentReplaceError(resp, request)
            if silent is True:
                return True
            return format_edge(resp.body)

        return self._execute(request, response_handler)

    def delete(
        self,
        edge: Union[str, Json],
        rev: Optional[str] = None,
        check_rev: bool = True,
        ignore_missing: bool = False,
        sync: Optional[bool] = None,
        return_old: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Delete an edge document.

        :param edge: Edge document ID, key or body. Document body must contain
            the "_id" or "_key" field.
        :type edge: str | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **edge** if present.
        :type rev: str | None
        :param check_rev: If set to True, revision of **edge** (if given) is
            compared against the revision of target edge document.
        :type check_rev: bool
        :param ignore_missing: Do not raise an exception on missing document.
            This parameter has no effect in transactions where an exception is
            always raised on failures.
        :type ignore_missing: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param return_old: Return body of the old document in the result.
        :type return_old: bool
        :return: True if edge was deleted successfully, False if edge was not
            found and **ignore_missing** was set to True (does not  apply in
            transactions).
        :rtype: bool
        :raise arango.exceptions.DocumentDeleteError: If delete fails.
        :raise arango.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        handle, _, headers = self._prep_from_doc(edge, rev, check_rev)

        params: Params = {"returnOld": return_old}
        if sync is not None:
            params["waitForSync"] = sync

        request = Request(
            method="delete",
            endpoint=f"/_api/gharial/{self._graph}/edge/{handle}",
            params=params,
            headers=headers,
            write=self.name,
        )

        def response_handler(resp: Response) -> Union[bool, Json]:
            if resp.error_code == 1202 and ignore_missing:
                return False
            if resp.status_code == 412:  # pragma: no cover
                raise DocumentRevisionError(resp, request)
            if not resp.is_success:
                raise DocumentDeleteError(resp, request)

            result: Json = resp.body
            return {"old": result["old"]} if return_old else True

        return self._execute(request, response_handler)

    def link(
        self,
        from_vertex: Union[str, Json],
        to_vertex: Union[str, Json],
        data: Optional[Json] = None,
        sync: Optional[bool] = None,
        silent: bool = False,
        return_new: bool = False,
    ) -> Result[Union[bool, Json]]:
        """Insert a new edge document linking the given vertices.

        :param from_vertex: "From" vertex document ID or body with "_id" field.
        :type from_vertex: str | dict
        :param to_vertex: "To" vertex document ID or body with "_id" field.
        :type to_vertex: str | dict
        :param data: Any extra data for the new edge document. If it has "_key"
            or "_id" field, its value is used as key of the new edge document
            (otherwise it is auto-generated).
        :type data: dict | None
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool | None
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :param return_new: Include body of the new document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_new: bool
        :return: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise arango.exceptions.DocumentInsertError: If insert fails.
        """
        edge = {"_from": get_doc_id(from_vertex), "_to": get_doc_id(to_vertex)}
        if data is not None:
            edge.update(self._ensure_key_from_id(data))
        return self.insert(edge, sync=sync, silent=silent, return_new=return_new)

    def edges(
        self, vertex: Union[str, Json], direction: Optional[str] = None
    ) -> Result[Json]:
        """Return the edge documents coming in and/or out of the vertex.

        :param vertex: Vertex document ID or body with "_id" field.
        :type vertex: str | dict
        :param direction: The direction of the edges. Allowed values are "in"
            and "out". If not set, edges in both directions are returned.
        :type direction: str
        :return: List of edges and statistics.
        :rtype: dict
        :raise arango.exceptions.EdgeListError: If retrieval fails.
        """
        params: Params = {"vertex": get_doc_id(vertex)}
        if direction is not None:
            params["direction"] = direction

        request = Request(
            method="get",
            endpoint=f"/_api/edges/{self.name}",
            params=params,
            read=self.name,
        )

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise EdgeListError(resp, request)
            stats = resp.body["stats"]
            return {
                "edges": resp.body["edges"],
                "stats": {
                    "filtered": stats["filtered"],
                    "scanned_index": stats["scannedIndex"],
                },
            }

        return self._execute(request, response_handler)
