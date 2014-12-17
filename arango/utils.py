"""Utility Functions."""

import re
import collections


def unicode_to_str(obj):
    """Convert any unicode in ``obj`` to str and return it.

    :param obj: the object to sanitize
    :type obj: object
    :returns: the sanitized object
    :rtype: object
    """
    if isinstance(obj, basestring):
        return str(obj)
    elif isinstance(obj, collections.Mapping):
        return dict(map(unicode_to_str, obj.items()))
    elif isinstance(obj, collections.Iterable):
        return type(obj)(map(unicode_to_str, obj))
    else:
        return obj

def camelify(obj):
    """Convert any string in ``obj`` from snake to camel case and return it.

    All strings are assumed to be in snake case.

    :param obj: the object to camelify
    :type obj: object
    :returns: the camelified object
    :rtype: object
    """
    if isinstance(obj, basestring):
        words = obj.split("_")
        return words[0] + "".join(word.title() for word in words[1:])
    elif isinstance(obj, collections.Mapping):
        return dict(map(camelify, obj.items()))
    elif isinstance(obj, collections.Iterable):
        return type(obj)(map(camelify, obj))
    else:
        return obj

def uncamelify(obj):
    """Convert the string in ``obj`` from camel to snake case and return it.

    All strings are assumed to be in camel case.

    :param obj: the object to uncamelify
    :type obj: object
    :returns: the uncamelified object
    :rtype: object
    """
    if isinstance(obj, basestring):
        return re.sub('(?!^)([A-Z]+)', r'_\1', obj).lower()
    elif isinstance(obj, collections.Mapping):
        return dict(map(uncamelify, obj.items()))
    elif isinstance(obj, collections.Iterable):
        return type(obj)(map(uncamelify, obj))
    else:
        return obj

def filter_keys(dictionary, filtered):
    """Return a new dictionary with the specified keys filtered."""
    return {k: v for k, v in dictionary.items() if k not in filtered}
