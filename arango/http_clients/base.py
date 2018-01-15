from abc import ABCMeta, abstractmethod


class BaseHTTPClient(object):  # pragma: no cover
    """Base class for ArangoDB clients.

    The methods must return an instance of :class:`arango.response.Response`.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def make_request(self, request, response_mapper=None):
        """Use the :class:arango.request.Request object to make an HTTP request

        :param request: The request to make
        :type request: arango.request.Request
        :param response_mapper: Function that maps responses to a dictionary of
         parameters to create an :class:`arango.responses.Response`. If
         none, uses self.response_mapper.
        :type response_mapper: callable
        :return: The response to this request
        :rtype: arango.responses.BaseResponse
        """

        raise NotImplementedError
