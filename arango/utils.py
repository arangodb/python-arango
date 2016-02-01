from __future__ import absolute_import, unicode_literals

from json import dumps

from six import string_types as string

# Set of HTTP OK status codes
HTTP_OK = {200, 201, 202, 203, 204, 205, 206}


def sanitize(data):
    if data is None:
        return None
    elif isinstance(data, string):
        return data
    else:
        return dumps(data)
