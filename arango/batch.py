import logging
import json
import re

from arango.exceptions import (
    ArangoBatchExecuteError
)


class Batch(object):

    def __init__(self, client):
        self._client = client

    def execute(self, parts):
        data = ""
        part_id = 1
        for part in parts:
            data += "--XXXsubpartXXX\r\n"
            data += "Content-Type: application/x-arango-batchpart\r\n"
            data += "Content-Id: {}\r\n\r\n".format(part_id)
            data += "{}\r\n".format(stringify_request(**part))
            part_id += 1
        data += "--XXXsubpartXXX--\r\n\r\n"

        res = self._client.post(
            "/_api/batch",
            headers={
              "Content-Type": "multipart/form-data; boundary=XXXsubpartXXX"
            },
            data=data,
            raw_data=True
        )
        if res.status_code != 200:
            raise ArangoBatchExecuteError(res)
        return res.obj

        #resp_body = resp.text.split("--{}--".format(self.MIME_BOUNDARY))[0]
        #part_resps = resp_body.split("--{}{}".format(self.MIME_BOUNDARY, EOL))[1:]


def stringify_request(method, path, headers=None, data=None):
    request_string = "{} {} HTTP/1.1".format(method, path)
    if headers:
        for key, value in headers.iteritems():
            request_string += "\r\n{key}: {value}".format(
                key=key, value=value
            )
    if data:
        request_string += "\r\n\r\n{}".format(json.dumps(data))
    return request_string
