from __future__ import absolute_import, unicode_literals

import requests

from arango.responses import Response
from arango.http_clients import BaseHTTPClient


class DefaultHTTPClient(BaseHTTPClient):
    """Session based HTTP client for ArangoDB using the requests_ library.

    .. _requests: http://docs.python-requests.org/en/master/
    """

    def __init__(self, use_session=True, check_cert=True):
        """Initialize the client and the session if applicable."""
        if use_session:
            self._session = requests.Session()
        else:
            self._session = requests
        self._check_cert = check_cert

    def make_request(self, request, response_mapper=None):
        """Use the :class:arango.request.Request object to make an HTTP request

        :param request: The request to make
        :type request: arango.request.Request
        :param response_mapper: Function that maps responses to a dictionary of
         parameters to create an :class:`arango.responses.Response`. If
         none, uses self.response_mapper.
        :type response_mapper: callable
        :return: The response to this request
        :rtype: arango.responses.Response
        """

        if response_mapper is None:
            response_mapper = self.response_mapper

        method = request.method

        res = self._session.request(method, **request.kwargs)
        return Response(res, response_mapper)

    @staticmethod
    def response_mapper(response):
        outputs = {}

        outputs['url'] = response.url
        outputs['method'] = response.request.method
        outputs['headers'] = response.headers
        outputs['status_code'] = response.status_code
        outputs['status_text'] = response.reason
        outputs['body'] = response.text

        return outputs
