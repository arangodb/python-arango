from __future__ import absolute_import, unicode_literals

__all__ = ['Request']


class Request(object):
    """HTTP request.

    :param method: HTTP method in lowercase (e.g. "post").
    :type method: str
    :param endpoint: API endpoint.
    :type endpoint: str
    :param headers: Request headers.
    :type headers: dict
    :param params: URL parameters.
    :type params: dict
    :param data: Request payload.
    :type data: str | bool | int | list | dict |
        requests_toolbelt.MultipartEncoder
    :param read: Names of collections read during transaction.
    :type read: str | [str]
    :param write: Name(s) of collections written to during transaction with
        shared access.
    :type write: str | [str]
    :param exclusive: Name(s) of collections written to during transaction
        with exclusive access.
    :type exclusive: str | [str]
    :param deserialize: Whether the response body can be deserialized.
    :type deserialize: bool
    :ivar method: HTTP method in lowercase (e.g. "post").
    :vartype method: str
    :ivar endpoint: API endpoint.
    :vartype endpoint: str
    :ivar headers: Request headers.
    :vartype headers: dict
    :ivar params: URL (query) parameters.
    :vartype params: dict
    :ivar data: Request payload.
    :vartype data: str | bool | int | list | dict
    :ivar read: Names of collections read during transaction.
    :vartype read: str | [str] | None
    :ivar write: Name(s) of collections written to during transaction with
        shared access.
    :vartype write: str | [str] | None
    :ivar exclusive: Name(s) of collections written to during transaction
        with exclusive access.
    :vartype exclusive: str | [str] | None
    :ivar deserialize: Whether the response body can be deserialized.
    :vartype deserialize: bool
    """

    __slots__ = (
        'method',
        'endpoint',
        'headers',
        'params',
        'data',
        'read',
        'write',
        'exclusive',
        'deserialize',
        'files'
    )

    def __init__(self,
                 method,
                 endpoint,
                 headers=None,
                 params=None,
                 data=None,
                 read=None,
                 write=None,
                 exclusive=None,
                 deserialize=True):
        self.method = method
        self.endpoint = endpoint
        self.headers = {
            'content-type': 'application/json',
            'charset': 'utf-8'
        }
        if headers is not None:
            for field in headers:
                self.headers[field.lower()] = headers[field]

        # Sanitize URL params.
        if params is not None:
            for key, val in params.items():
                if isinstance(val, bool):
                    params[key] = int(val)

        self.params = params
        self.data = data
        self.read = read
        self.write = write
        self.exclusive = exclusive
        self.deserialize = deserialize
