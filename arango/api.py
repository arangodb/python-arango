from __future__ import absolute_import, unicode_literals

from functools import wraps


class APIWrapper(object):
    """ArangoDB API wrapper base class.

    This class is meant to be used internally only.
    """

    def __getattribute__(self, attr):
        method = object.__getattribute__(self, attr)
        conn = object.__getattribute__(self, '_conn')

        if not getattr(method, 'api_method', False):
            return method

        @wraps(method)
        def wrapped_method(*args, **kwargs):
            request, handler = method(*args, **kwargs)
            return conn.handle_request(request, handler)
        return wrapped_method


def api_method(method):
    """Decorator used to mark ArangoDB API methods.

    Methods decorated by this should return two things:

    - An instance of :class:`arango.request.Request`
    - A handler that takes an instance of :class:`arango.response.Response`

    :param method: the method to wrap
    :type method: callable
    :returns: the wrapped method
    :rtype: callable
    """
    setattr(method, 'api_method', True)
    return method
