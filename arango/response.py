from __future__ import absolute_import, unicode_literals

__all__ = ['Response']

import json


class Response(object):
    """HTTP response.

    :param method: HTTP method in lowercase (e.g. "post").
    :type method: str | unicode
    :param url: API URL.
    :type url: str | unicode
    :param headers: Response headers.
    :type headers: requests.structures.CaseInsensitiveDict | dict
    :param status_code: Response status code.
    :type status_code: int
    :param status_text: Response status text.
    :type status_text: str | unicode
    :param raw_body: Raw response body.
    :type raw_body: str | unicode

    :ivar method: HTTP method in lowercase (e.g. "post").
    :vartype method: str | unicode
    :ivar url: API URL.
    :vartype url: str | unicode
    :ivar headers: Response headers.
    :vartype headers: requests.structures.CaseInsensitiveDict | dict
    :ivar status_code: Response status code.
    :vartype status_code: int
    :ivar status_text: Response status text.
    :vartype status_text: str | unicode
    :ivar body: JSON-deserialized response body.
    :vartype body: str | unicode | bool | int | list | dict
    :ivar raw_body: Raw response body.
    :vartype raw_body: str | unicode
    :ivar error_code: Error code from ArangoDB server.
    :vartype error_code: int
    :ivar error_message: Error message from ArangoDB server.
    :vartype error_message: str | unicode
    :ivar is_success: True if response status code was 2XX.
    :vartype is_success: bool
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
        'is_success',
    )

    def __init__(self,
                 method,
                 url,
                 headers,
                 status_code,
                 status_text,
                 raw_body):
        self.method = method.lower()
        self.url = url
        self.headers = headers
        self.status_code = status_code
        self.status_text = status_text
        self.raw_body = raw_body

        # De-serialize the response body.
        try:
            self.body = json.loads(raw_body)
        except (ValueError, TypeError):
            self.body = raw_body

        # Extract error code and message.
        if isinstance(self.body, dict):
            self.error_code = self.body.get('errorNum')
            self.error_message = self.body.get('errorMessage')
        else:
            self.error_code = None
            self.error_message = None

        http_ok = 200 <= status_code < 300
        self.is_success = http_ok and self.error_code is None
