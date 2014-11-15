"""Utility Functions."""

import collections

def unicode_to_str(data):
    """Convert any unicode in ``data`` to str and return it."""
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(unicode_to_str, data.items()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(unicode_to_str, data))
    else:
        return data