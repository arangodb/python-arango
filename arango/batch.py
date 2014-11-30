import json
import inspect
from urllib import urlencode

from arango.exceptions import (
    BatchInvalidError,
    BatchExecuteError
)


class BatchHandler(object):

    def __init__(self, api):
        self._api = api

    def execute_batch(self, requests):
        data = ""
        for content_id, request in enumerate(requests, start=1):
            try:
                func, args, kwargs = request
            except (TypeError, ValueError):
                raise BatchInvalidError(
                    "pos {}: malformed request".format(content_id)
                )
            if "_batch" not in inspect.getargspec(func)[0]:
                raise BatchInvalidError(
                    "pos {}: ArangoDB method '{}' does not support "
                    "batch execution".format(content_id, func.__name__)
                )
            kwargs["_batch"] = True
            res = func(*args, **kwargs)
            data += "--XXXsubpartXXX\r\n"
            data += "Content-Type: application/x-arango-batchpart\r\n"
            data += "Content-Id: {}\r\n\r\n".format(content_id)
            data += "{}\r\n".format(stringify_request(**res))
        data += "--XXXsubpartXXX--\r\n\r\n"
        res = self._api.post(
            "/_api/batch",
            headers={
                "Content-Type": "multipart/form-data; boundary=XXXsubpartXXX"
            },
            data=data,
        )
        if res.status_code != 200:
            raise BatchExecuteError(res)
        return [
            json.loads(string) for string in res.obj.split("\r\n") if
            string.startswith("{") and string.endswith("}")
        ]


def stringify_request(method, path, params=None, headers=None, data=None):
    path = path + "?" + urlencode(params) if params else path
    request_string = "{} {} HTTP/1.1".format(method, path)
    if headers:
        for key, value in headers.iteritems():
            request_string += "\r\n{key}: {value}".format(
                key=key, value=value
            )
    if data:
        request_string += "\r\n\r\n{}".format(json.dumps(data))
    return request_string
