from __future__ import absolute_import, unicode_literals

import requests

from arango.response import Response
from arango.http_clients.base import BaseHTTPClient


class DefaultHTTPClient(BaseHTTPClient):
    """Session based HTTP client for ArangoDB using the requests_ library.

    .. _requests: http://docs.python-requests.org/en/master/
    """

    def __init__(self, use_session=True, check_cert=True):
        """Initialize the session."""
        if use_session:
            self._session = requests.Session()
        else:
            self._session = requests
        self._check_cert = check_cert

    def head(self, url, params=None, headers=None, auth=None):
        """Execute an HTTP **HEAD** method.

        :param url: request URL
        :type url: str
        :param params: request parameters
        :type params: dict
        :param headers: request headers
        :type headers: dict
        :param auth: username and password tuple
        :type auth: tuple
        :returns: ArangoDB HTTP response object
        :rtype: arango.response.Response
        """
        res = self._session.head(
            url=url,
            params=params,
            headers=headers,
            auth=auth,
            verify=self._check_cert
        )
        return Response(
            url=url,
            method="head",
            headers=res.headers,
            http_code=res.status_code,
            http_text=res.reason,
            body=res.text
        )

    def get(self, url, params=None, headers=None, auth=None):
        """Execute an HTTP **GET** method.

        :param url: request URL
        :type url: str
        :param params: request parameters
        :type params: dict
        :param headers: request headers
        :type headers: dict
        :param auth: username and password tuple
        :type auth: tuple
        :returns: ArangoDB HTTP response object
        :rtype: arango.response.Response
        """
        res = self._session.get(
            url=url,
            params=params,
            headers=headers,
            auth=auth,
            verify=self._check_cert
        )
        return Response(
            url=url,
            method="get",
            headers=res.headers,
            http_code=res.status_code,
            http_text=res.reason,
            body=res.text
        )

    def put(self, url, data, params=None, headers=None, auth=None):
        """Execute an HTTP **PUT** method.

        :param url: request URL
        :type url: str
        :param data: request payload
        :type data: str | dict
        :param params: request parameters
        :type params: dict
        :param headers: request headers
        :type headers: dict
        :param auth: username and password tuple
        :type auth: tuple
        :returns: ArangoDB HTTP response object
        :rtype: arango.response.Response
        """
        res = self._session.put(
            url=url,
            data=data,
            params=params,
            headers=headers,
            auth=auth,
            verify=self._check_cert
        )
        return Response(
            url=url,
            method="put",
            headers=res.headers,
            http_code=res.status_code,
            http_text=res.reason,
            body=res.text
        )

    def post(self, url, data, params=None, headers=None, auth=None):
        """Execute an HTTP **POST** method.

        :param url: request URL
        :type url: str
        :param data: request payload
        :type data: str | dict
        :param params: request parameters
        :type params: dict
        :param headers: request headers
        :type headers: dict
        :param auth: username and password tuple
        :type auth: tuple
        :returns: ArangoDB HTTP response object
        :rtype: arango.response.Response
        """
        res = self._session.post(
            url=url,
            data=data,
            params=params,
            headers=headers,
            auth=auth,
            verify=self._check_cert
        )
        return Response(
            url=url,
            method="post",
            headers=res.headers,
            http_code=res.status_code,
            http_text=res.reason,
            body=res.text
        )

    def patch(self, url, data, params=None, headers=None, auth=None):
        """Execute an HTTP **PATCH** method.

        :param url: request URL
        :type url: str
        :param data: request payload
        :type data: str | dict
        :param params: request parameters
        :type params: dict
        :param headers: request headers
        :type headers: dict
        :param auth: username and password tuple
        :type auth: tuple
        :returns: ArangoDB HTTP response object
        :rtype: arango.response.Response
        """
        res = self._session.patch(
            url=url,
            data=data,
            params=params,
            headers=headers,
            auth=auth,
            verify=self._check_cert
        )
        return Response(
            url=url,
            method="patch",
            headers=res.headers,
            http_code=res.status_code,
            http_text=res.reason,
            body=res.text
        )

    def delete(self, url, data=None, params=None, headers=None, auth=None):
        """Execute an HTTP **DELETE** method.

        :param url: request URL
        :type url: str
        :param data: request payload
        :type data: str | dict
        :param params: request parameters
        :type params: dict
        :param headers: request headers
        :type headers: dict
        :param auth: username and password tuple
        :type auth: tuple
        :returns: ArangoDB HTTP response object
        :rtype: arango.response.Response
        """
        res = self._session.delete(
            url=url,
            data=data,
            params=params,
            headers=headers,
            auth=auth,
            verify=self._check_cert
        )
        return Response(
            url=url,
            method="delete",
            headers=res.headers,
            http_code=res.status_code,
            http_text=res.reason,
            body=res.text
        )
