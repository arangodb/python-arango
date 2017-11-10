from __future__ import absolute_import, unicode_literals

from json import dumps

from six import string_types


def sanitize(data):
    if data is None:
        return None
    elif isinstance(data, string_types):
        return data
    else:
        return dumps(data)


def fix_params(params):
    if params is None:
        return params

    outparams = {}

    for param, value in params.items():
        if isinstance(value, bool):
            value = int(value)

        outparams[param] = value

    return outparams
