from __future__ import absolute_import, unicode_literals

from json import dumps

from six import moves


class Request(object):
    """ArangoDB API request object.

    .. note::
        This class is meant to be used internally only.
    """

    __slots__ = (
        'method',
        'url',
        'headers',
        'params',
        'data',
        'command',
        'auth'
    )

    def __init__(self,
                 method,
                 endpoint,
                 headers=None,
                 params=None,
                 data=None,
                 command=None,
                 auth=None):
        self.method = method
        self.url = endpoint
        self.headers = headers or {}
        self.params = params or {}
        self.data = data
        self.command = command
        self.auth = auth

    @property
    def kwargs(self):
        return {
            'url': self.url,
            'headers': self.headers,
            'params': self.params,
            'data': self.data,
            'auth': self.auth
        }

    def stringify(self):
        path = self.url
        if self.params is not None:
            path += '?' + moves.urllib.parse.urlencode(self.params)
        request_string = '{} {} HTTP/1.1'.format(self.method, path)
        if self.headers is not None:
            for key, value in self.headers.items():
                request_string += '\r\n{key}: {value}'.format(
                    key=key, value=value
                )
        if self.data is not None:
            request_string += '\r\n\r\n{}'.format(dumps(self.data))
        return request_string
