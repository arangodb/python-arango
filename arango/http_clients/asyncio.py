from __future__ import absolute_import, unicode_literals

# noinspection PyCompatibility
import asyncio
import threading

import aiohttp
import time

from arango.http_clients import BaseHTTPClient
from arango.responses import LazyResponse


# noinspection PyCompatibility
def start_event_loop(loop, request_queue, session_args):  # pragma: no cover
    """Start an event loop with an aiohttp session that pulls
     from the request_queue

    :param loop: An event loop
    :type loop: asyncio.BaseEventLoop
    :param request_queue: The queue of tuples containing
    :class:`arango.request.Request` and :class:`asyncio.Queue`
    :type request_queue: asyncio.Queue
    :param kwargs: the arguments to pass to the session instance
    :type kwargs: dict
    """
    asyncio.set_event_loop(loop)
    future = loop.create_task(session_create(request_queue, **session_args))
    loop.run_until_complete(future)


# noinspection PyCompatibility
async def session_create(request_queue, **kwargs):
    """Start an aiohttp session and pull from the job queue

    :param request_queue: The queue of :class:`arango.request.Request`
    :type request_queue: asyncio.Queue
    :param kwargs: the arguments to pass to the session instance
    :type kwargs: dict
    """

    async with aiohttp.ClientSession(**kwargs) as session:
        this_thread = threading.current_thread()
        while True:
            request, output_queue = await request_queue.get()
            if request is this_thread:
                return
            await output_queue.put(await session_send_request(request,
                                                              session))


# noinspection PyCompatibility
async def session_send_request(request, session):
    response = await session.request(
        method=request.method,
        **request.kwargs
    )
    text = await response.text()
    return response, text


# noinspection PyCompatibility
async def stop_event_loop(request_queue):  # pragma: no cover
    """Stop the request loop to allow it to exit."""
    await request_queue.put((threading.current_thread(), None))


# noinspection PyCompatibility
async def make_async_request(request, request_queue, event_loop):
    # pragma: no cover
    """Asynchronously make a request using `aiohttp` library

    :param request: the request to make
    :type request: arango.request.Request
    :param request_queue: the request queue to submit to
    :type request_queue: asyncio.Queue
    :return: :class:`asyncio.Future` containing a tuple containing the
    response to the request and its text.
    :rtype: asyncio.Future
    """

    return_queue = asyncio.Queue(maxsize=1, loop=event_loop)
    await request_queue.put((request, return_queue))
    return await return_queue.get()


class AsyncioHTTPClient(BaseHTTPClient):  # pragma: no cover
    """Asyncio based HTTP client for ArangoDB using the aiohttp_ library.

    .. _aiohttp: http://aiohttp.readthedocs.io/en/stable/
    """

    def __init__(self, **kwargs):
        """Initialize the client.

        :param kwargs: the arguments to pass to the aiohttp session
        :type kwargs: dict
        """
        self._event_loop = asyncio.new_event_loop()
        self._request_queue = asyncio.Queue(loop=self._event_loop)
        self._async_thread = threading.Thread(
            target=start_event_loop,
            args=(self._event_loop, self._request_queue, kwargs),
            daemon=True
        )
        self._async_thread.start()
        self._timeout = 100

    def stop_client_loop(self):
        future = asyncio.run_coroutine_threadsafe(
            stop_event_loop(self._request_queue),
            self._event_loop
        )
        asyncio.wait_for(future, self._timeout)
        while self._event_loop.is_running():
            time.sleep(.01)
        self._event_loop.close()
        self._async_thread.join()

    @staticmethod
    def response_mapper(response):
        res, text = response

        outputs = {}
        outputs['url'] = res.url
        outputs['method'] = res.method
        outputs['headers'] = res.headers
        outputs['status_code'] = res.status
        outputs['status_text'] = res.reason
        outputs['body'] = text

        return outputs

    def make_request(self, request, response_mapper=None):
        """Make an asynchronous request and return a lazy loading response.

        :param request: The request to make
        :type request: arango.request.Request
        :param response_mapper: Function that maps responses to a dictionary of
         parameters to create an :class:`arango.responses.Response`. If
         none, uses self.response_mapper.
        :type response_mapper: callable
        :return: The lazy loading response to this request
        :rtype: arango.responses.LazyResponse
        """

        if response_mapper is None:
            response_mapper = self.response_mapper

        if isinstance(request.auth, tuple):
            request.auth = aiohttp.BasicAuth(*request.auth)

        if isinstance(request.params, dict):
            for key, value in request.params.items():
                if isinstance(value, bool):
                    request.params[key] = int(value)

        future = asyncio.run_coroutine_threadsafe(
            make_async_request(request, self._request_queue, self._event_loop),
            self._event_loop
        )
        return LazyResponse(future, response_mapper)
