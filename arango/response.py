import json
import sys


class Response(object):
    """ArangoDB HTTP response.

    Overridden methods of :class:`arango.http_clients.base.BaseHTTPClient` must
    return instances of this.

    :param method: The HTTP method name (e.g. ``"post"``).
    :type method: str | unicode
    :param url: The request URL
        (e.g. ``"http://localhost:8529/_db/_system/_api/database"``)
    :type url: str | unicode
    :param headers: A dict-like mapping object containing the HTTP headers.
        Must allow case-insensitive key access.
    :type headers: collections.MutableMapping
    :param http_code: The HTTP status code.
    :type http_code: int
    :param http_text: The HTTP status text. This is used only for printing
        error messages, and has no specification to follow.
    :type http_text: str | unicode
    :param body: The HTTP response body.
    :type body: str | unicode | dict
    """

    __slots__ = (
        'method',
        'url',
        'headers',
        'status_code',
        'status_text',
        'raw_body',
        'body',
        'error_code',
        'error_message'
    )

    def __init__(self,
                 method=None,
                 url=None,
                 headers=None,
                 http_code=None,
                 http_text=None,
                 body=None):
        self.url = url
        self.method = method
        self.headers = headers
        self.status_code = http_code
        self.status_text = http_text
        self.raw_body = body
        try:
            self.body = json.loads(body)
        except (ValueError, TypeError):
            self.body = body
        if self.body and isinstance(self.body, dict):
            self.error_code = self.body.get('errorNum')
            self.error_message = self.body.get('errorMessage')
        else:
            self.error_code = None
            self.error_message = None

    def update_body(self, new_body):
        return Response(
            url=self.url,
            method=self.method,
            headers=self.headers,
            http_code=self.status_code,
            http_text=self.status_text,
            body=new_body
        )


class FutureResponse(Response):
    def __init__(self,
                 future):
        if sys.version_info[0] < 3 or sys.version_info[1] < 5:
            raise RuntimeError("Error: Async event loops not compatible with python versions < 3.5")
        self._future = future

    def __getattr__(self, item):
        if item in self.__slots__:
            result = self._future.result()
            response = result[0]
            text = result[1]
            super().__init__(method=response.method,
                             url=response.url,
                             headers=response.headers,
                             http_code=response.status,
                             http_text=response.reason,
                             body=text)
            self.__getattr__ = None
        else:
            raise AttributeError
