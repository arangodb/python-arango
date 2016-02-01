import json


class Response(object):
    """ArangoDB HTTP response.

    Methods of :class:`arango.http_clients.base.BaseHTTPClient` must return
    an instance of this.

    :param method: the HTTP method
    :type method: str
    :param url: the request URL
    :type url: str
    :param http_code: the HTTP status code
    :type http_code: int
    :param http_text: the HTTP status text
    :type http_text: str
    :param body: the HTTP response body
    :type body: str | dict
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
