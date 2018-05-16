from __future__ import absolute_import, unicode_literals

__all__ = ['HTTPClient', 'DefaultHTTPClient']

from abc import ABCMeta, abstractmethod

import requests

from arango.response import Response


class HTTPClient(object):  # pragma: no cover
    """Abstract base class for HTTP clients."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def send_request(self,
                     method,
                     url,
                     headers=None,
                     params=None,
                     data=None,
                     auth=None):
        """Send an HTTP request.

        This method must be overridden by the user.

        :param method: HTTP method in lowercase (e.g. "post").
        :type method: str | unicode
        :param url: Request URL.
        :type url: str | unicode
        :param headers: Request headers.
        :type headers: dict
        :param params: URL (query) parameters.
        :type params: dict
        :param data: Request payload.
        :type data: str | unicode | bool | int | list | dict
        :param auth: Username and password.
        :type auth: tuple
        :returns: HTTP response.
        :rtype: arango.response.Response
        """
        raise NotImplementedError


class DefaultHTTPClient(HTTPClient):
    """Default HTTP client implementation."""

    def __init__(self):
        self._session = requests.Session()

    def send_request(self,
                     method,
                     url,
                     params=None,
                     data=None,
                     headers=None,
                     auth=None):
        """Send an HTTP request.

        :param method: HTTP method in lowercase (e.g. "post").
        :type method: str | unicode
        :param url: Request URL.
        :type url: str | unicode
        :param headers: Request headers.
        :type headers: dict
        :param params: URL (query) parameters.
        :type params: dict
        :param data: Request payload.
        :type data: str | unicode | bool | int | list | dict
        :param auth: Username and password.
        :type auth: tuple
        :returns: HTTP response.
        :rtype: arango.response.Response
        """
        raw_resp = self._session.request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            auth=auth,
        )
        return Response(
            method=raw_resp.request.method,
            url=raw_resp.url,
            headers=raw_resp.headers,
            status_code=raw_resp.status_code,
            status_text=raw_resp.reason,
            raw_body=raw_resp.text,
        )
