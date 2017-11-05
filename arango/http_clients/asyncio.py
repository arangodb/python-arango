from __future__ import absolute_import, unicode_literals

# noinspection PyCompatibility
import asyncio
import threading

import aiohttp

from arango.http_clients.base import BaseHTTPClient
from arango.response import Response


class FutureResponse(Response):  # pragma: no cover
    """Response for :class:`arango.http_clients.asyncio.AsyncioHTTPClient`.

    :param future: The future instance.
    :type future: concurrent.futures.Future
    """

    # noinspection PyMissingConstructor
    def __init__(self, future):
        self._future = future

    def __getattr__(self, item):
        if item in self.__slots__:
            response, text = self._future.result()
            Response.__init__(
                self,
                method=response.method,
                url=response.url,
                headers=response.headers,
                http_code=response.status,
                http_text=response.reason,
                body=text
            )
            self.__getattr__ = None
        else:
            raise AttributeError


def start_event_loop(loop):  # pragma: no cover
    """Set the event loop and start it."""
    asyncio.set_event_loop(loop)
    loop.run_forever()


# noinspection PyCompatibility
async def stop_event_loop():  # pragma: no cover
    """Stop the event to allow it to exit."""
    asyncio.get_event_loop().stop()


# noinspection PyCompatibility
async def make_async_request(method,
                             url,
                             params=None,
                             headers=None,
                             data=None,
                             auth=None):  # pragma: no cover
    """Asynchronously make a request using `aiohttp` library.

    :param method: HTTP method (e.g. ``"HEAD"``)
    :type method: str | unicode
    :param url: request method string
    :type url: str | unicode
    :param url: request URL
    :type url: str | unicode
    :param params: request parameters
    :type params: dict
    :param headers: request headers
    :type headers: dict
    :param data: request payload
    :type data: str | unicode | dict
    :param auth: username and password tuple
    :type auth: tuple
    :returns: ArangoDB HTTP response object and body
    :rtype: aiohttp.ClientResponse
    """
    async with aiohttp.ClientSession() as session:
        response = await session.request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            data=data,
            auth=auth
        )
        text = await response.text()
        return response, text


class AsyncioHTTPClient(BaseHTTPClient):  # pragma: no cover
    """Asyncio based HTTP client for ArangoDB using the aiohttp_ library.

    .. _aiohttp: http://aiohttp.readthedocs.io/en/stable/
    """

    def __init__(self):
        """Initialize the client."""
        self._event_loop = asyncio.new_event_loop()
        self._async_thread = threading.Thread(
            target=start_event_loop,
            args=(self._event_loop,),
            daemon=True
        )
        self._async_thread.start()
        self._timeout = 100

    def stop_client_loop(self):
        future = asyncio.run_coroutine_threadsafe(
            stop_event_loop(), self._event_loop
        )
        asyncio.wait_for(future, self._timeout)
        self._async_thread.join()

    def make_request(self,
                     method,
                     url,
                     params=None,
                     headers=None,
                     data=None,
                     auth=None):
        """Make an asynchronous request and return a future response.

        :param method: HTTP method (e.g. ``"HEAD"``)
        :type method: str | unicode
        :param url: request method string
        :type url: str | unicode
        :param url: request URL
        :type url: str | unicode
        :param params: request parameters
        :type params: dict
        :param headers: request headers
        :type headers: dict
        :param data: request payload
        :type data: str | unicode | dict
        :param auth: username and password tuple
        :type auth: tuple
        :returns: ArangoDB HTTP response object
        :rtype: arango.http_clients.asyncio.FutureResponse
        """
        if isinstance(auth, tuple):
            auth = aiohttp.BasicAuth(*auth)

        if isinstance(params, dict):
            for key, value in params.items():
                if isinstance(value, bool):
                    params[key] = int(value)

        future = asyncio.run_coroutine_threadsafe(
            make_async_request(method, url, params, headers, data, auth),
            self._event_loop
        )
        return FutureResponse(future)

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
        :rtype: arango.response.FutureResponse
        """
        return self.make_request(
            method="HEAD",
            url=url,
            params=params,
            headers=headers,
            auth=auth
        )

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
        :rtype: arango.response.FutureResponse
        """
        return self.make_request(
            method="GET",
            url=url,
            params=params,
            headers=headers,
            auth=auth
        )

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
        :rtype: arango.response.FutureResponse
        """
        return self.make_request(
            method="PUT",
            url=url,
            data=data,
            params=params,
            headers=headers,
            auth=auth
        )

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
        :rtype: arango.response.FutureResponse
        """
        return self.make_request(
            method="POST",
            url=url,
            data=data,
            params=params,
            headers=headers,
            auth=auth
        )

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
        :rtype: arango.response.FutureResponse
        """
        return self.make_request(
            method="PATCH",
            url=url,
            data=data,
            params=params,
            headers=headers,
            auth=auth
        )

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
        :rtype: arango.response.FutureResponse
        """
        return self.make_request(
            method="DELETE",
            url=url,
            data=data,
            params=params,
            headers=headers,
            auth=auth
        )
