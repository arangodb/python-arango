from __future__ import absolute_import, unicode_literals

import aiohttp

from arango.http_clients.base import BaseHTTPClient
from arango.response import FutureResponse
import asyncio
import sys
from threading import Thread


def start_background_loop(loop):
    asyncio.set_event_loop(loop)

    loop.run_forever()


async def execute_asyncio(method, url, params=None, headers=None, data=None, auth=None):
    """Asynchronously get a aiohttp.ClientResponse for the given parameters

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
    :returns: aiohttp HTTP response object
    :rtype: aiohttp.ClientResponse
    """

    response = await aiohttp.request(method, url, params=params, headers=headers, data=data, auth=auth)
    text = await response.text()
    return response, text


async def stop_loop():
    """
    Stops the running event loop from on the thread to allow it to exit

    :return: None
    """
    loop = asyncio.get_event_loop()
    loop.stop()


class AsyncioHTTPClient(BaseHTTPClient):
    """Asyncio based HTTP client for ArangoDB using the aiohttp library.

    .. _aiohttp: http://aiohttp.readthedocs.io/en/stable/
    """

    def __init__(self):
        """Initialize the client"""
        if sys.version_info[0] < 3 or sys.version_info[1] < 5:
            raise RuntimeError("Error: Async event loops not compatible with python versions < 3.5")

        self._loop = asyncio.new_event_loop()

        self._async_thread = Thread(target=start_background_loop, args=(self._loop, ), daemon=True)

        self._async_thread.start()

    def stop_client_loop(self):
        future = asyncio.run_coroutine_threadsafe(stop_loop(), self._loop)
        asyncio.wait_for(future, 100)
        self._async_thread.join()

    def returnFuture(self, method, url, params=None, headers=None, data=None, auth=None):
        """Get a FutureResponse for the given parameters

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
        :rtype: arango.response.FutureResponse
        """
        if isinstance(auth, tuple):
            auth = aiohttp.BasicAuth(*auth)

        if isinstance(params, dict):
            new_params = {}

            for key, value in params.items():
                if isinstance(value, bool):
                    new_params[key] = 1 if value else 0
                else:
                    new_params[key] = value

            params = new_params

        future = asyncio.run_coroutine_threadsafe(execute_asyncio(method, url, params, headers, data, auth), self._loop)
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
        return self.returnFuture(
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
        return self.returnFuture(
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
        return self.returnFuture(
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
        return self.returnFuture(
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
        return self.returnFuture(
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
        return self.returnFuture(
            method="DELETE",
            url=url,
            data=data,
            params=params,
            headers=headers,
            auth=auth
        )
