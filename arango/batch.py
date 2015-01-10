import re
import json
import logging
import inspect

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
                argspec = inspect.getargspec(func)[0]
            except TypeError, ValueError:
                raise BatchInvalidError(
                    "pos {}: malformed request".format(content_id)
                )
            if "batch" not in inspect.getargspec(func)[0]:
                raise BatchInvalidError(
                    "pos {}: ArangoDB method '{}' does not support "
                    "batch execution".format(func.__name__, content_id)
                )
            kwargs["batch"] = True
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
    if params:
        query = []
        for k, v in params.items():
            if not isinstance(v, basestring):
                v = json.dumps(v)
            query.append("{}={}".format(k, v))
        path += "?" + "&".join(query)
    request_string = "{} {} HTTP/1.1".format(method.upper(), path)
    if headers:
        for key, value in headers.iteritems():
            request_string += "\r\n{key}: {value}".format(
                key=key, value=value
            )
    if data:
        request_string += "\r\n\r\n{}".format(json.dumps(data))
    return request_string
