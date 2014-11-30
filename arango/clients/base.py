"""Base class for HTTP clients."""

from abc import ABCMeta, abstractmethod


class BaseArangoClient(object):
    """Base ArangoDB HTTP client."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def head(self, url, params=None, headers=None, auth=None):
        """HTTP HEAD method.

        :param url: request URL
        :type url: str
        :param params: query parameters
        :type params: dict or None
        :param headers: request headers
        :type headers: dict or None
        :param auth: username and password
        :type auth: tuple or None
        :returns: ArangoDB http response
        :rtype: arango.response.ArangoResponse
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, url, params=None, headers=None, auth=None):
        """HTTP GET method.

        :param url: request URL
        :type url: str
        :param params: query parameters
        :type params: dict or None
        :param headers: request headers
        :type headers: dict or None
        :param auth: username and password
        :type auth: tuple or None
        :returns: ArangoDB http response
        :rtype: arango.response.ArangoResponse
        """
        raise NotImplementedError

    @abstractmethod
    def post(self, url, data=None, params=None, headers=None, auth=None):
        """HTTP POST method.

        :param url: request URL
        :type url: str
        :param data: JSON serializable object or str
        :type data: object
        :param params: query parameters
        :type params: dict or None
        :param headers: request headers
        :type headers: dict or None
        :param auth: username and password
        :type auth: tuple or None
        :returns: ArangoDB http response
        :rtype: arango.response.ArangoResponse
        """
        raise NotImplementedError

    @abstractmethod
    def put(self, url, data=None, params=None, headers=None, auth=None):
        """HTTP PUT method.

        :param url: request URL
        :type url: str
        :param data: JSON serializable object or str
        :type data: dict
        :param params: query parameters
        :type params: dict or None
        :param headers: request headers
        :type headers: dict or None
        :param auth: username and password
        :type auth: tuple or None
        :returns: ArangoDB http response
        :rtype: arango.response.ArangoResponse
        """
        raise NotImplementedError

    @abstractmethod
    def patch(self, url, data=None, params=None, headers=None, auth=None):
        """HTTP PATCH method.

        :param url: request URL
        :type url: str
        :param data: JSON serializable object or str
        :type data: dict
        :param params: query parameters
        :type params: dict or None
        :param headers: request headers
        :type headers: dict or None
        :param auth: username and password
        :type auth: tuple or None
        :returns: ArangoDB http response
        :rtype: arango.response.ArangoResponse
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, url, params=None, headers=None, auth=None):
        """HTTP DELETE method.

        :param url: request URL
        :type url: str
        :param params: query parameters
        :type params: dict or None
        :param headers: request headers
        :type headers: dict or None
        :param auth: username and password
        :type auth: tuple or None
        :returns: ArangoDB http response
        :rtype: arango.response.ArangoResponse
        """
        raise NotImplementedError
