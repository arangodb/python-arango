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

def camelify(string):
    """Convert the string from snake to camel case and return it.

    The string is assumed to be in snake case completely.

    :param string: the string to camelify
    :type string: str
    :returns: the camelified string
    :rtype: str
    """
    words = string.split("_")
    return words[0] + "".join(word.title() for word in words[1:])

def uncamelify(string):
    """Convert the string from camel to snake case and return it.

    The string is assumed to be in camel case completely.

    :param string: the string to uncamelify
    :type string: str
    :returns: the uncamelified string
    :rtype: str
    """
    return re.sub('(?!^)([A-Z]+)', r'_\1', string).lower()

def filter_keys(dictionary, filtered):
    """Return a new dictionary with the specified keys filtered."""
    return {k: v for k, v in dictionary.items() if k not in filtered}
