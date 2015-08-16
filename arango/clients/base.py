"""Base class for ArangoDB HTTP clients."""

from abc import ABCMeta, abstractmethod


class BaseClient(object):
    """Base class for ArangoDB clients.

    The methods MUST return an ``arango.response.Response`` object.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def head(self, url, params=None, headers=None, auth=None):
        """HTTP HEAD method.

        :param url: request URL
        :type url: str
        :param params: request parameters
        :type params: dict or None
        :param headers: request headers
        :type headers: dict or None
        :param auth: username and password tuple
        :type auth: tuple or None
        :returns: ArangoDB http response object
        :rtype: arango.response.Response
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, url, params=None, headers=None, auth=None):
        """HTTP GET method.

        :param url: request URL
        :type url: str
        :param params: request parameters
        :type params: dict or None
        :param headers: request headers
        :type headers: dict or None
        :param auth: username and password tuple
        :type auth: tuple or None
        :returns: ArangoDB http response object
        :rtype: arango.response.Response
        """
        raise NotImplementedError

    @abstractmethod
    def post(self, url, data=None, params=None, headers=None, auth=None):
        """HTTP POST method.

        :param url: request URL
        :type url: str
        :param data: request payload
        :type data: str or dict or None
        :param params: request parameters
        :type params: dict or None
        :param headers: request headers
        :type headers: dict or None
        :param auth: username and password tuple
        :type auth: tuple or None
        :returns: ArangoDB http response object
        :rtype: arango.response.Response
        """
        raise NotImplementedError

    @abstractmethod
    def put(self, url, data=None, params=None, headers=None, auth=None):
        """HTTP PUT method.

        :param url: request URL
        :type url: str
        :param data: request payload
        :type data: str or dict or None
        :param params: request parameters
        :type params: dict or None
        :param headers: request headers
        :type headers: dict or None
        :param auth: username and password tuple
        :type auth: tuple or None
        :returns: ArangoDB http response object
        :rtype: arango.response.Response
        """
        raise NotImplementedError

    @abstractmethod
    def patch(self, url, data=None, params=None, headers=None, auth=None):
        """HTTP PATCH method.

        :param url: request URL
        :type url: str
        :param data: request payload
        :type data: str or dict or None
        :param params: request parameters
        :type params: dict or None
        :param headers: request headers
        :type headers: dict or None
        :param auth: username and password tuple
        :type auth: tuple or None
        :returns: ArangoDB http response object
        :rtype: arango.response.Response
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, url, params=None, headers=None, auth=None):
        """HTTP DELETE method.

        :param url: request URL
        :type url: str
        :param params: request parameters
        :type params: dict or None
        :param headers: request headers
        :type headers: dict or None
        :param auth: username and password tuple
        :type auth: tuple or None
        :returns: ArangoDB http response object
        :rtype: arango.response.Response
        """
        raise NotImplementedError

    @abstractmethod
    def options(self, url, data=None, params=None, headers=None, auth=None):
        """HTTP OPTIONS method.

        :param url: request URL
        :type url: str
        :param data: request payload
        :type data: str or dict or None
        :param params: request parameters
        :type params: dict or None
        :param headers: request headers
        :type headers: dict or None
        :param auth: username and password tuple
        :type auth: tuple or None
        :returns: ArangoDB http response object
        :rtype: arango.response.Response
        """
        raise NotImplementedError
