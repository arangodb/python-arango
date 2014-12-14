"""ArangoDB AQL Query."""

from arango.exceptions import *


class Query(object):
    """ArangoDB AQL and Simple queries.

    :param client: the http client
    """

    def __init__(self, client):
        self._client = client
        self.simple = SimpleQuery(client)

    def _read_cursor(self, res):
        """Continuously read from the cursor and yield the result."""
        for item in res.obj["result"]:
            yield item
        cursor_id = None
        while res.obj["hasMore"]:
            if cursor_id is None:
                cursor_id = res.obj["id"]
            res = self._client.put("/api/cursor/{}".format(cursor_id))
            if res.status_code != 200:
                raise ArangoQueryExecuteError(res)
            for item in res.obj["result"]:
                yield item
        if cursor_id is not None:
            res = self._client.delete("/api/cursor/{}".format(cursor_id))
            if res.status_code != 202:
                raise ArangoCursorDeleteError(res)

    ###############
    # AQL Queries #
    ###############

    def parse(self, query):
        """Validate the AQL query.

        :param query: the AQL query to validate
        :type query: str
        :returns: True
        :rtype: boolean
        :raises: ArangoQueryParseError
        """
        res = self._client.post("/_api/query", data={"query": query})
        if res.status_code != 200:
            raise ArangoQueryParseError(res)
        return True

    def execute(self, query, **kwargs):
        """Execute the AQL query and return the result.

        :param query: the AQL query to execute
        :type query: str
        :returns: the result from executing the query
        :rtype: types.GeneratorType
        :raises: ArangoQueryExecuteError, ArangoCursorDeleteError
        """
        data = {"query": query}
        data.update(kwargs)
        res = self._client.post("/_api/cursor", data=data)
        if res.status_code != 201:
            raise ArangoQueryExecuteError(res)
        return self._read_cursor(res)


class SimpleQuery(object):

    def __init__(self, client):
        self._client = client

    def first(self, col_name, count=1):
        """Return the first ``count`` number of documents.

        :param col_name: the name of the collection
        :type col_name: str
        :param count: the number of documents to return
        :type count: int
        :returns: the list of documents
        :rtype: list
        :raises: ArangoSimpleQueryFirstError
        """
        data = {"collection": col_name, "count": count}
        res = self._client.put("/_api/simple/first", data=data)
        if res.status_code != 200:
            raise ArangoSimpleQueryFirstError(res)
        return res.obj["result"]

    def last(self, col_name, count=1):
        """Return the last ``count`` number of documents.

        :param col_name: the name of the collection
        :type col_name: str
        :param count: the number of documents to return
        :type count: int
        :returns: the list of documents
        :rtype: list
        :raises: ArangoSimpleQueryLastError
        """
        data = {"collection": col_name, "count": count}
        res = self._client.put("/_api/simple/last", data=data)
        if res.status_code != 200:
            raise ArangoSimpleQueryLastError(res)
        return res.obj["result"]

    def all(self, col_name, skip=None, limit=None):
        """Return all documents of a collection.

        ``skip`` is applied before ``limit`` if both are provided.

        :param col_name: the name of the collection
        :type col_name: str
        :param skip: the number of documents to skip
        :type skip: int
        :param limit: maximum number of documents to return
        :type limit: int
        :returns: the list of all documents
        :rtype: list
        :raises: ArangoSimpleQueryAllError
        """
        data = {"collection": col_name}
        if skip is not None:
            data["skip"] = skip
        if limit is not None:
            data["limit"] = limit
        res = self._client.put("/_api/simple/all", data=data)
        if res.status_code != 201:
            raise ArangoSimpleQueryAllError(res)
        return list(self._read_cursor(res))

    def any(self, col_name):
        """Return a random document from the specified collection.

        :param col_name: the name of the collection
        :type col_name: str
        :returns: the randomly chosen document
        :rtype: dict
        :raises: ArangoSimpleQueryAnyError
        """
        res = self._client.put(
            "/_api/simple/any",
            data={"collection": col_name}
        )
        if res.status_code != 200:
            raise ArangoSimpleQueryAnyError(res)
        return res.obj["document"]

    def get_by_example(self, col_name, example, skip=None, limit=None):
        """Return all documents matching the given example.

        ``skip`` is applied before ``limit`` if both are provided.

        :param col_name: the name of the collection
        :type col_name: str
        :param example: the example document
        :type example: dict
        :param skip: the number of documents to skip
        :type skip: int
        :param limit: maximum number of documents to return
        :type limit: int
        :returns: the list of documents
        :rtype: list
        :raises: ArangoSimpleQueryGetByExampleError
        """
        data = {"collection": col_name, "example": example}
        if skip is not None:
            data["skip"] = skip
        if limit is not None:
            data["limit"] = limit
        res = self._client.put("/_api/simple/by-example", data=data)
        if res.status_code != 201:
            raise ArangoSimpleQueryGetByExampleError(res)
        return list(self._read_cursor(res))

    def get_first_example(self, col_name, example):
        """Return the first document matching the given example.

        :param col_name: the name of the collection
        :type col_name: str
        :param example: the example document
        :type example: dict
        :returns: the first document
        :rtype: dict
        :raises: ArangoSimpleQueryFirstExampleError
        """
        data = {"collection": col_name, "example": example}
        res = self._client.put("/_api/simple/first-example", data=data)
        if res.status_code == 404:
            return
        elif res.status_code != 200:
            raise ArangoSimpleQueryFirstExampleError(res)
        return res.obj["document"]

    def replace_by_example(self, col_name, example, new_value,
                           limit=None, wait_for_sync=False):
        """Replace all documents matching the given example.

        ``skip`` is applied before ``limit`` if both are provided.

        :param col_name: the name of the collection
        :type col_name: str
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
        :raises: ArangoSimpleQueryError
        """
        data = {
            "collection": col_name,
            "example": example,
            "newValue": new_value,
            "waitForSync": wait_for_sync,
        }
        if limit is not None:
            data["limit"] = limit
        res = self._client.put(
            "/_api/simple/replace-by-example",
            data=data
        )
        if res.status_code != 200:
            raise ArangoSimpleQueryReplaceByExampleError(res)
        return res.obj["replaced"]

    def update_by_example(self, col_name, example, new_value,
                          keep_none=True, limit=None,
                          wait_for_sync=False):
        """Update all documents matching the given example.

        ``skip`` is applied before ``limit`` if both are provided.

        :param col_name: the name of the collection
        :type col_name: str
        :param example: the example document
        :type example: dict
        :param new_value: the new document to patch with
        :type new_value: dict
        :param keep_none: whether or not to keep the None values
        :type keep_none: bool
        :param limit: maximum number of documents to return
        :type limit: int
        :param wait_for_sync: wait for the update to sync to disk
        :type wait_for_sync: bool
        :returns: the number of documents updated
        :rtype: int
        :raises: ArangoSimpleQueryUpdateByExampleError
        """
        data = {
            "collection": col_name,
            "example": example,
            "newValue": new_value,
            "keepNull": keep_none,
            "waitForSync": wait_for_sync,
        }
        if limit is not None:
            data["limit"] = limit
        res = self._client.put(
            "/_api/simple/update-by-example",
            data=data
        )
        if res.status_code != 200:
            raise ArangoSimpleQueryUpdateByExampleError(res)
        return res.obj["updated"]

    def delete_by_example(self, col_name, example, limit=None,
                          wait_for_sync=False):
        """Delete all documents matching the given example.

        ``skip`` is applied before ``limit`` if both are provided.

        :param col_name: the name of the collection
        :type col_name: str
        :param example: the example document
        :type example: dict
        :param limit: maximum number of documents to return
        :type limit: int
        :param wait_for_sync: wait for the delete to sync to disk
        :type wait_for_sync: bool
        :returns: the number of documents deleted
        :rtype: int
        :raises: ArangoSimpleQueryDeleteByExampleError
        """
        data = {
            "collection": col_name,
            "example": example,
            "waitForSync": wait_for_sync,
        }
        if limit is not None:
            data["limit"] = limit
        res = self._client.put(
            "/_api/simple/remove-by-example",
            data=data
        )
        if res.status_code != 200:
            raise ArangoSimpleQueryDeleteByExampleError(res)
        return res.obj["deleted"]



    def range(self, col_name, attribute, left, right, closed=True, skip=None,
              limit=None):
        """Return all the documents within a given range.

        In order to execute this query a skip-list index must be present on the
        queried attribute.

        :param col_name: the name of the collection
        :type col_name: str
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
        :raises: ArangoSimpleQueryRangeError
        """
        data = {
            "collection": col_name,
            "attribute": attribute,
            "left": left,
            "right": right,
            "closed": closed
        }
        if skip is not None:
            data["skip"] = skip
        if limit is not None:
            data["limit"] = limit
        res = self._client.put("/_api/simple/range", data=data)
        if res.status_code != 201:
            raise ArangoSimpleQueryRangeError(res)
        return list(self._read_cursor(res))

    def near(self, col_name, latitude, longitude, distance=None, skip=None,
             limit=None, geo=None):
        """Return all the documents near the given coordinate.

        By default number of documents returned is 100. The returned list is
        sorted based on the distance, with the nearest document being the first
        in the list. Documents of equal dinstance are ordered randomly.

        In order to execute this query a geo index must be defined for the
        collection. If there are more than one geo-spatial index, the ``geo``
        argument can be used to select a particular index.

        if ``distance`` is given, return the distance (in meters) to the
        coordinate in a new attribute whose key is the value of the argument.

        :param col_name: the name of the collection
        :type col_name: str
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
        :raises: ArangoSimpleQueryNearError
        """
        data = {arg: val for arg, val in locals() if val is not None}
        res = self._client.put("/_api/simple/near", data=data)
        if res.status_code != 201:
            raise ArangoSimpleQueryError(res)
        return list(self._read_cursor(res))

    def within(self, col_name, latitude, longitude, radius, distance=None,
               skip=None, limit=None, geo=None):
        """Return all documents within the radius around the coordinate.

        The returned list is sorted by distance from the coordinate. In order
        to execute this query a geo index must be defined for the collection.
        If there are more than one geo-spatial index, the ``geo`` argument can
        be used to select a particular index.

        if ``distance`` is given, return the distance (in meters) to the
        coordinate in a new attribute whose key is the value of the argument.

        :param col_name: the name of the collection
        :type col_name: str
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
        :raises: ArangoSimpleQueryWithinError
        """
        data = {arg: val for arg, val in locals() if val is not None}
        res = self._client.put("/_api/simple/within", data=data)
        if res.status_code != 201:
            return ArangoSimpleQueryWithinError(res)
        return list(self._read_cursor(res))

    def fulltext(self, col_name, attribute, query, skip=None, limit=None,
                 index=None):
        """Return all documents that match the specified fulltext ``query``.

        In order to execute this query a fulltext index must be define for the
        collection and the specified attribute.

        :param col_name: the name of the collection
        :type col_name: str
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
        :raises: ArangoSimpleQueryFullTextError
        """
        data = {arg: val for arg, val in locals() if val is not None}
        res = self._client.put("/_api/simple/fulltext", data=data)
        if res.status_code != 201:
            return ArangoSimpleQueryFullTextError(res)
        return list(self._read_cursor(res))


