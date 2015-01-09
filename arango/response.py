"""Base class for HTTP responses"""

import json


class ArangoResponse(object):
    """ArangoDB HTTP Response.

    :param status_code: HTTP status code
    :type status_code: int
    :param text: HTTP response text
    :type text: basestring
    """

    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text
        try:
            self.obj = json.loads(text) if text else None
        except ValueError:
            self.obj = text
