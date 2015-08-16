"""ArangoDB HTTP response."""

import json


class Response(object):
    """ArangoDB HTTP Response class.

    The clients in arango.clients MUST return an instance of this class.

    :param method: the HTTP method
    :type method: str
    :param url: the request URL
    :type url: str
    :param status_code: the HTTP status code
    :type status_code: int
    :param content: the HTTP response content
    :type content: basestring or str
    :param status_text: the HTTP status description if any
    :type status_text: str or None
    """

    def __init__(self, method, url, status_code, content, status_text=None):
        self.method = method
        self.url = url
        self.status_code = status_code
        self.status_text = status_text
        try:
            self.obj = json.loads(content) if content else None
        except ValueError:
            self.obj = None
