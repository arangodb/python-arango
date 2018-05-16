from __future__ import absolute_import, unicode_literals

__all__ = ['Request']

import json

from six import moves, string_types


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
    :param command: ArangoSh command.
    :type command: str | unicode
    :param read: Names of collections read during transaction.
    :type read: str | unicode | [str | unicode]
    :param write: Names of collections written to during transaction.
    :type write: str | unicode | [str | unicode]

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
    :ivar command: ArangoSh command.
    :vartype command: str | unicode | None
    :ivar read: Names of collections read during transaction.
    :vartype read: str | unicode | [str | unicode] | None
    :ivar write: Names of collections written to during transaction.
    :vartype write: str | unicode | [str | unicode] | None
    """

    __slots__ = (
        'method',
        'endpoint',
        'headers',
        'params',
        'data',
        'command',
        'read',
        'write'
    )

    def __init__(self,
                 method,
                 endpoint,
                 headers=None,
                 params=None,
                 data=None,
                 command=None,
                 read=None,
                 write=None):
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

        # Normalize the payload.
        if data is None:
            self.data = None
        elif isinstance(data, string_types):
            self.data = data
        else:
            self.data = json.dumps(data)

        # Set the transaction metadata.
        self.command = command
        self.read = read
        self.write = write

    def __str__(self):
        """Return the request details in string form."""
        path = self.endpoint
        if self.params is not None:
            path += '?' + moves.urllib.parse.urlencode(self.params)
        request_strings = ['{} {} HTTP/1.1'.format(self.method, path)]
        if self.headers is not None:
            for key, value in sorted(self.headers.items()):
                request_strings.append('{}: {}'.format(key, value))
        if self.data is not None:
            request_strings.append('\r\n{}'.format(self.data))
        return '\r\n'.join(request_strings)
