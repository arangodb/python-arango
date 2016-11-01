from abc import ABCMeta, abstractmethod


class BaseHTTPClient(object):  # pragma: no cover
    """Base class for ArangoDB clients.

    The methods must return an instance of :class:`arango.response.Response`.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def head(self, url, params=None, headers=None, auth=None):
        """Execute an HTTP **HEAD** method.

        :param url: request URL
        :type url: str | unicode
        :param params: request parameters
        :type params: dict
        :param headers: request headers
        :type headers: dict
        :param auth: username and password tuple
        :type auth: tuple
        :returns: ArangoDB HTTP response object
        :rtype: arango.response.Response
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, url, params=None, headers=None, auth=None):
        """Execute an HTTP **GET** method.

        :param url: request URL
        :type url: str | unicode
        :param params: request parameters
        :type params: dict
        :param headers: request headers
        :type headers: dict
        :param auth: username and password tuple
        :type auth: tuple
        :returns: ArangoDB HTTP response object
        :rtype: arango.response.Response
        """
        raise NotImplementedError

    @abstractmethod
    def put(self, url, data, params=None, headers=None, auth=None):
        """Execute an HTTP **PUT** method.

        :param url: request URL
        :type url: str | unicode
        :param data: request payload
        :type data: str | unicode | dict
        :param params: request parameters
        :type params: dict
        :param headers: request headers
        :type headers: dict
        :param auth: username and password tuple
        :type auth: tuple
        :returns: ArangoDB HTTP response object
        :rtype: arango.response.Response
        """
        raise NotImplementedError

    @abstractmethod
    def post(self, url, data, params=None, headers=None, auth=None):
        """Execute an HTTP **POST** method.

        :param url: request URL
        :type url: str | unicode
        :param data: request payload
        :type data: str | unicode | dict
        :param params: request parameters
        :type params: dict
        :param headers: request headers
        :type headers: dict
        :param auth: username and password tuple
        :type auth: tuple
        :returns: ArangoDB HTTP response object
        :rtype: arango.response.Response
        """
        raise NotImplementedError

    @abstractmethod
    def patch(self, url, data, params=None, headers=None, auth=None):
        """Execute an HTTP **PATCH** method.

        :param url: request URL
        :type url: str | unicode
        :param data: request payload
        :type data: str | unicode | dict
        :param params: request parameters
        :type params: dict
        :param headers: request headers
        :type headers: dict
        :param auth: username and password tuple
        :type auth: tuple
        :returns: ArangoDB HTTP response object
        :rtype: arango.response.Response
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, url, data=None, params=None, headers=None, auth=None):
        """Execute an HTTP **DELETE** method.

        :param url: request URL
        :type url: str | unicode
        :param data: request payload
        :type data: str | unicode | dict
        :param params: request parameters
        :type params: dict
        :param headers: request headers
        :type headers: dict
        :param auth: username and password tuple
        :type auth: tuple
        :returns: ArangoDB HTTP response object
        :rtype: arango.response.Response
        """
        raise NotImplementedError
