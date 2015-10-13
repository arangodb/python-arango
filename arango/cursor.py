"""ArangoDB Cursor."""

from arango.constants import HTTP_OK
from arango.exceptions import (
    CursorGetNextError,
    CursorDeleteError,
)


def cursor(api, response):
    """Continuously read from the server cursor and yield the result.

    :param api: ArangoDB API wrapper object
    :type api: arango.api.API
    :param response: ArangoDB response object
    :type response: arango.response.Response
    :raises: CursorExecuteError, CursorDeleteError
    """
    for item in response.body["result"]:
        yield item
    cursor_id = None
    while response.body["hasMore"]:
        if cursor_id is None:
            cursor_id = response.body["id"]
        response = api.put("/_api/cursor/{}".format(cursor_id))
        if response.status_code not in HTTP_OK:
            raise CursorGetNextError(response)
        for item in response.body["result"]:
            yield item
    if cursor_id is not None:
        response = api.delete("/api/cursor/{}".format(cursor_id))
        if response.status_code not in {404, 202}:
            raise CursorDeleteError(response)
