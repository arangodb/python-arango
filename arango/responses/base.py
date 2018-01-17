import json


class Response(object):
    """ArangoDB HTTP response.

    Overridden methods of :class:`arango.http_clients.base.BaseHTTPClient` must
    return instances of this.

    :param method: The HTTP method name (e.g. ``"post"``).
    :type method: str | unicode | None
    :param url: The request URL
        (e.g. ``"http://localhost:8529/_db/_system/_api/database"``)
    :type url: str | unicode | None
    :param headers: A dict-like mapping object containing the HTTP headers.
        Must allow case-insensitive key access.
    :type headers: collections.MutableMapping | None
    :param http_code: The HTTP status code.
    :type http_code: int | None
    :param http_text: The HTTP status text. This is used only for printing
        error messages, and has no specification to follow.
    :type http_text: str | unicode | None
    :param body: The HTTP response body.
    :type body: str | unicode | dict | None
    """

    __slots__ = (
        'method',
        'url',
        'headers',
        'status_code',
        'status_text',
        'body',
        'raw_body',
        'error_code',
        'error_message',
        'is_json'
    )

    def __init__(self,
                 response,
                 response_mapper):

        processed = response_mapper(response)
        self.method = processed.get('method', None)
        self.url = processed.get('url', None)
        self.headers = processed.get('headers', None)
        self.status_code = processed.get('status_code', None)
        self.status_text = processed.get('status_text', None)

        self.raw_body = None
        self.body = None
        self.error_code = None
        self.error_message = None

        self.update_body(processed.get('body', None))

    def update_body(self, body):
        self.raw_body = body

        try:
            self.body = json.loads(self.raw_body)
        except (ValueError, TypeError):
            self.body = self.raw_body
        if isinstance(self.body, dict):
            self.error_code = self.body.get('errorNum')
            self.error_message = self.body.get('errorMessage')
        else:
            self.error_code = None
            self.error_message = None
