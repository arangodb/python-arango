"""ArangoDB AQL Query."""

from arango.exceptions import (
    ArangoQueryParseError,
    ArangoQueryExecuteError,
    ArangoCursorDeleteError,
)


class QueryMixin(object):
    """Mix-in class for handling AQL queries."""

    def __init__(self, client):
        self._conn = client

    def parse_query(self, query):
        """Validate the AQL query.

        :param query: the AQL query to validate.
        :type query: str
        :raises: ArangoQueryParseError
        """
        res = self._conn.post("/_api/query", data={"query": query})
        if res.status_code != 200:
            raise ArangoQueryParseError(res)

    def execute_query(self, query, **kwargs):
        """Execute the AQL query and return the result.

        :param query: the AQL query to execute.
        :type query: str
        :returns: iterator
        :raises: ArangoQueryExecuteError, ArangoCursorDeleteError
        """
        data = {"query": query}
        data.update(kwargs)
        res = self._conn.post("/_api/cursor", data=data)
        if res.status_code != 201:
            raise ArangoQueryExecuteError(res)
        for item in res.obj["result"]:
            yield item
        cursor_id = None
        while res.obj["hasMore"]:
            if cursor_id is None:
                cursor_id = res.obj["id"]
            res = self._put("/api/cursor/{}".format(cursor_id))
            if res.status_code != 200:
                raise ArangoQueryExecuteError(res)
            for item in res.obj["result"]:
                yield item
        if cursor_id is not None:
            res = self._delete("/api/cursor/{}".format(cursor_id))
            if res.status_code != 202:
                raise ArangoCursorDeleteError(res)