from __future__ import absolute_import, unicode_literals

__all__ = ['Request']


class Request(object):
    """HTTP request.

    :param method: HTTP method in lowercase (e.g. "post").
    :type method: str | unicode
    :param endpoint: API endpoint.
    :type endpoint: str | unicode
    :param headers: Request headers.
    :type headers: dict
    :param params: URL parameters.
    :type params: dict
    :param data: Request payload.
    :type data: str | unicode | bool | int | list | dict
    :param read: Names of collections read during transaction.
    :type read: str | unicode | [str | unicode]
    :param write: Name(s) of collections written to during transaction with
        shared access.
    :type write: str | unicode | [str | unicode]
    :param exclusive: Name(s) of collections written to during transaction
        with exclusive access.
    :type exclusive: str | unicode | [str | unicode]
    :param deserialize: Whether the response body can be deserialized.
    :type deserialize: bool

    :ivar method: HTTP method in lowercase (e.g. "post").
    :vartype method: str | unicode
    :ivar endpoint: API endpoint.
    :vartype endpoint: str | unicode
    :ivar headers: Request headers.
    :vartype headers: dict
    :ivar params: URL (query) parameters.
    :vartype params: dict
    :ivar data: Request payload.
    :vartype data: str | unicode | bool | int | list | dict
    :ivar read: Names of collections read during transaction.
    :vartype read: str | unicode | [str | unicode] | None
    :ivar write: Name(s) of collections written to during transaction with
        shared access.
    :vartype write: str | unicode | [str | unicode] | None
    :ivar exclusive: Name(s) of collections written to during transaction
        with exclusive access.
    :vartype exclusive: str | unicode | [str | unicode] | None
    :ivar deserialize: Whether the response body can be deserialized.
    :vartype deserialize: str | unicode | [str | unicode] | None
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
        'deserialize'
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
        self.headers = headers or {}

        # Insert default headers.
        self.headers['content-type'] = 'application/json'
        self.headers['charset'] = 'utf-8'

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
