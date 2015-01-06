"""ArangoDB Cursor object."""

from arango.exceptions import *


class CursorFactory(object):

    def __init__(self, api):
        self._api = api

    def cursor(self, res):
        """Continuously read from the cursor and yield the result.

        :param res: ArangoDB response object
        :type res: arango.response.ArangoResponse
        """
        for item in res.obj["result"]:
            yield item
        cursor_id = None
        while res.obj["hasMore"]:
            if cursor_id is None:
                cursor_id = res.obj["id"]
            res = self._api.put("/_api/cursor/{}".format(cursor_id))
            if res.status_code != 200:
                raise ArangoQueryExecuteError(res)
            for item in res.obj["result"]:
                yield item
        if cursor_id is not None:
            res = self._api.delete("/api/cursor/{}".format(cursor_id))
            if res.status_code not in {404, 202}:
                raise ArangoCursorDeleteError(res)
