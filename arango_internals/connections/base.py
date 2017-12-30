from __future__ import absolute_import, unicode_literals

import logging

from arango_internals.jobs import BaseJob, SynchronousResultJob
from arango_internals.http_clients import DefaultHTTPClient
from arango_internals.utils import sanitize, fix_params
from arango_internals.wrappers import AQL, Graph
from arango_internals.collections import Collection


class BaseConnection(object):
    """ArangoDB database connection.

    :param protocol: the internet transfer protocol (default: ``"http"``)
    :type protocol: str | unicode
    :param host: ArangoDB host (default: ``"localhost"``)
    :type host: str | unicode
    :param port: ArangoDB port (default: ``8529``)
    :type port: int | str | unicode
    :param database: the name of the target database (default: ``"_system"``)
    :type database: str | unicode
    :param username: ArangoDB username (default: ``"root"``)
    :type username: str | unicode
    :param password: ArangoDB password (default: ``""``)
    :type password: str | unicode
    :param http_client: the HTTP client
    :type http_client: arango.clients.base.BaseHTTPClient
    :param enable_logging: log all API requests with a logger named "arango"
    :type enable_logging: bool
    """

    def __init__(self,
                 protocol='http',
                 host='localhost',
                 port=8529,
                 database="_system",
                 username='root',
                 password='',
                 http_client=None,
                 enable_logging=True,
                 logger=None,
                 async_ready=False):

        if http_client is None:
            http_client = DefaultHTTPClient()

        if logger is None:
            logger = logging.getLogger('arango')

        self._protocol = protocol.strip('/')
        self._host = host.strip('/')
        self._port = port
        self._database = database
        self._url_prefix = '{protocol}://{host}:{port}/_db/{db}'.format(
            protocol=self._protocol,
            host=self._host,
            port=self._port,
            db=self._database
        )
        self._username = username
        self._password = password
        self._http = http_client
        self._enable_logging = enable_logging
        self._type = 'standard'
        self._logger = logger
        self._async_ready = async_ready

        if not async_ready:
            self._default_job = SynchronousResultJob
        else:
            self._default_job = BaseJob

        self._aql = AQL(self)
        self._parent = None

    def __repr__(self):
        return '<ArangoDB connection to database "{}">'.format(self._database)

    @property
    def underlying(self):
        if self._parent is None:
            return self
        else:
            return self._parent.underlying

    @property
    def protocol(self):
        """Return the internet transfer protocol.

        :returns: the internet transfer protocol
        :rtype: str | unicode
        """
        return self._protocol

    @property
    def host(self):
        """Return the ArangoDB host.

        :returns: the ArangoDB host
        :rtype: str | unicode
        """
        return self._host

    @property
    def port(self):
        """Return the ArangoDB port.

        :returns: the ArangoDB port
        :rtype: int
        """
        return self._port

    @property
    def username(self):
        """Return the ArangoDB username.

        :returns: the ArangoDB username
        :rtype: str | unicode
        """
        return self._username

    @property
    def password(self):
        """Return the ArangoDB user password.

        :returns: the ArangoDB user password
        :rtype: str | unicode
        """
        return self._password

    @property
    def database(self):
        """Return the name of the connected database.

        :returns: the name of the connected database
        :rtype: str | unicode
        """
        return self._database

    @property
    def http_client(self):
        """Return the HTTP client in use.

        :returns: the HTTP client in use
        :rtype: arango.http_clients.base.BaseHTTPClient
        """
        return self._http

    @property
    def logging_enabled(self):
        """Return ``True`` if logging is enabled, ``False`` otherwise.

        :returns: whether logging is enabled or not
        :rtype: bool
        """
        return self._enable_logging

    @property
    def type(self):
        """Return the connection type.

        :return: the connection type
        :rtype: str | unicode
        """
        return self._type

    @property
    def logger(self):
        return self._logger

    @property
    def async_ready(self):
        return self._async_ready

    def handle_request(self, request, handler, job_class=None,
                       **kwargs):
        """Handle a given request

        :param request: The request to make
        :type request: arango.request.Request
        :param handler: The response handler to use to process the response
        :type handler: callable
        :param job_class: the class of the :class:arango.jobs.BaseJob to
        output or None to use the default job for this connection
        :type job_class: class | None
        :param kwargs: keyword arguments to be passed to the
        :class:arango.jobs.BaseJob constructor
        :return: the job output
        :rtype: arango.jobs.BaseJob
        """
        if job_class is None:
            job_class = self._default_job

        endpoint = request.url
        request.url = self._url_prefix + request.url
        request.data = sanitize(request.data)
        request.params = fix_params(request.params)

        used_handler = handler

        if self._enable_logging:
            def new_handler(res):
                handled = handler(res)
                self._logger.debug('{} {} {}'.format(
                    request.method,
                    endpoint,
                    res.status_code))

                return handled

            used_handler = new_handler

        if request.auth is None:
            request.auth = (self._username, self._password)

        response = self._http.make_request(request)
        return job_class(used_handler, response, **kwargs)

    @property
    def aql(self):
        """Return the AQL object tailored for asynchronous execution.

        API requests via the returned query object are placed in a server-side
        in-memory task queue and executed asynchronously in a fire-and-forget
        style.

        :returns: ArangoDB query object
        :rtype: arango.query.AQL
        """
        return self._aql

    def collection(self, name):
        """Return a collection object tailored for asynchronous execution.

        API requests via the returned collection object are placed in a
        server-side in-memory task queue and executed asynchronously in
        a fire-and-forget style.

        :param name: the name of the collection
        :type name: str | unicode
        :returns: the collection object
        :rtype: arango.collections.Collection
        """
        return Collection(self, name)

    def graph(self, name):
        """Return a graph object tailored for asynchronous execution.

        API requests via the returned graph object are placed in a server-side
        in-memory task queue and executed asynchronously in a fire-and-forget
        style.

        :param name: the name of the graph
        :type name: str | unicode
        :returns: the graph object
        :rtype: arango.graph.Graph
        """
        return Graph(self, name)
