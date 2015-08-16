"""Session based client using requests."""

from requests import Session

from arango.response import Response
from arango.clients.base import BaseClient


class DefaultClient(BaseClient):
    """Session based HTTP (default) client for ArangoDB."""

    def __init__(self, init_data):
        """Initialize the session with the credentials.

        :param init_data: data for client initialization
        :type init_data: dict
        """
        self.session = Session()
        self.session.auth = init_data["auth"]

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
        )
        return Response(
            method="head",
            url=url,
            headers=res.headers,
            status_code=res.status_code,
            content=res.text,
            status_text=res.reason
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
        )
        return Response(
            method="get",
            url=url,
            headers=res.headers,
            status_code=res.status_code,
            content=res.text,
            status_text=res.reason
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
        )
        return Response(
            method="put",
            url=url,
            headers=res.headers,
            status_code=res.status_code,
            content=res.text,
            status_text=res.reason
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
            data="" if data is None else data,
            params={} if params is None else params,
            headers={} if headers is None else headers,
        )
        return Response(
            method="post",
            url=url,
            headers=res.headers,
            status_code=res.status_code,
            content=res.text,
            status_text=res.reason
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
        )
        return Response(
            method="patch",
            url=url,
            headers=res.headers,
            status_code=res.status_code,
            content=res.text,
            status_text=res.reason
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
            auth=auth,
        )
        return Response(
            method="delete",
            url=url,
            headers=res.headers,
            status_code=res.status_code,
            content=res.text,
            status_text=res.reason
        )

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
        res = self.session.options(
            url=url,
            data="" if data is None else data,
            params={} if params is None else params,
            headers={} if headers is None else headers,
        )
        return Response(
            method="options",
            url=url,
            headers=res.headers,
            status_code=res.status_code,
            content=res.text,
            status_text=res.reason
        )

    def close(self):
        """Close the HTTP session."""
        self.session.close()
