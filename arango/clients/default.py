"""Session based client using requests."""

from requests import Session

from arango.response import Response
from arango.clients.base import BaseHTTPClient


class DefaultHTTPClient(BaseHTTPClient):
    """Session based HTTP client for ArangoDB."""

    def __init__(self):
        """Initialize the session."""
        self.session = Session()

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
        res = self.session.head(
            url=url,
            params=params,
            headers=headers,
            auth=auth
        )
        return Response(
            method="head",
            url=url,
            headers=res.headers,
            status_code=res.status_code,
            status_text=res.reason,
            body=res.text
        )

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
        res = self.session.get(
            url=url,
            params=params,
            headers=headers,
            auth=auth
        )
        return Response(
            method="get",
            url=url,
            headers=res.headers,
            status_code=res.status_code,
            status_text=res.reason,
            body=res.text
        )

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
        res = self.session.put(
            url=url,
            data=data,
            params=params,
            headers=headers,
            auth=auth
        )
        return Response(
            method="put",
            url=url,
            headers=res.headers,
            status_code=res.status_code,
            status_text=res.reason,
            body=res.text
        )

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
        res = self.session.post(
            url=url,
            data=data,
            params=params,
            headers=headers,
            auth=auth
        )
        return Response(
            method="post",
            url=url,
            headers=res.headers,
            status_code=res.status_code,
            status_text=res.reason,
            body=res.text
        )

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
        res = self.session.patch(
            url=url,
            data=data,
            params=params,
            headers=headers,
            auth=auth
        )
        return Response(
            method="patch",
            url=url,
            headers=res.headers,
            status_code=res.status_code,
            status_text=res.reason,
            body=res.text
        )

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
        res = self.session.delete(
            url=url,
            params=params,
            headers=headers,
            auth=auth
        )
        return Response(
            method="delete",
            url=url,
            headers=res.headers,
            status_code=res.status_code,
            status_text=res.reason,
            body=res.text
        )

    def close(self):
        """Close the HTTP session."""
        self.session.close()
