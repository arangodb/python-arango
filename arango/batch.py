from __future__ import absolute_import, unicode_literals

from uuid import uuid4

from arango.collections import Collection
from arango.connection import Connection
from arango.utils import HTTP_OK
from arango.exceptions import BatchExecuteError, ArangoError
from arango.graph import Graph
from arango.response import Response
from arango.aql import AQL


class BatchExecution(Connection):
    """ArangoDB batch request.

    API requests via this class are queued in memory and executed as a whole
    in a single HTTP call to ArangoDB server.

    :param connection: ArangoDB database connection
    :type connection: arango.connection.Connection
    :param return_result: if ``True``, a :class:`arango.batch.BatchJob`
        (which holds the result after the commit) is returned each time an API
        request is queued, otherwise ``None`` is returned
    :type return_result: bool
    :param commit_on_error: only applicable when *context managers* are used
        to execute the batch request: if ``True``, the requests queued
        so far are committed even if an exception is raised before existing
        out of the context (default: ``False``)
    :type commit_on_error: bool
    """

    def __init__(self, connection, return_result=True, commit_on_error=False):
        super(BatchExecution, self).__init__(
            protocol=connection.protocol,
            host=connection.host,
            port=connection.port,
            username=connection.username,
            password=connection.password,
            http_client=connection.http_client,
            database=connection.database,
            enable_logging=connection.has_logging
        )
        self._id = uuid4()
        self._return_result = return_result
        self._commit_on_error = commit_on_error
        self._requests = []    # The queue for requests
        self._handlers = []    # The queue for response handlers
        self._batch_jobs = []  # For tracking batch jobs
        self._aql = AQL(self)
        self._type = 'batch'

    def __repr__(self):
        return '<ArangoDB batch execution {}>'.format(self._id)

    def __enter__(self):
        return self

    def __exit__(self, exception, *_):
        if exception is None or self._commit_on_error:
            self.commit()

    @property
    def id(self):
        """Return the UUID of the batch request.

        :return: the UUID of the batch request
        :rtype: str
        """
        return self._id

    def handle_request(self, request, handler):
        """Handle the incoming request and response handler.

        :param request: the API request queued as part of the current batch
            request scope, and executed only when the batch is committed via
            method :func:`~arango.batch.BatchExecution.commit`
        :type request: arango.request.Request
        :param handler: the response handler
        :type handler: callable
        :returns: the batch job or None
        :rtype: arango.batch.BatchJob
        """
        self._requests.append(request)
        self._handlers.append(handler)

        if not self._return_result:
            return None
        batch_job = BatchJob()
        self._batch_jobs.append(batch_job)
        return batch_job

    def commit(self):
        """Execute the queued API requests in a single HTTP call.

        If `return_response` was set to ``True`` during initialization, the
        responses are saved within an :class:`arango.batch.BatchJob` object
        for later retrieval via its :func:`~arango.batch.BatchJob.result`
        method

        :raises arango.exceptions.BatchExecuteError: if the batch request
            cannot be executed
        """
        try:
            if not self._requests:
                return
            raw_data = ''
            for content_id, request in enumerate(self._requests, start=1):
                raw_data += '--XXXsubpartXXX\r\n'
                raw_data += 'Content-Type: application/x-arango-batchpart\r\n'
                raw_data += 'Content-Id: {}\r\n\r\n'.format(content_id)
                raw_data += '{}\r\n'.format(request.stringify())
            raw_data += '--XXXsubpartXXX--\r\n\r\n'

            res = self.post(
                endpoint='/_api/batch',
                headers={
                    'Content-Type': (
                        'multipart/form-data; boundary=XXXsubpartXXX'
                    )
                },
                data=raw_data,
            )
            if res.status_code not in HTTP_OK:
                raise BatchExecuteError(res)
            if not self._return_result:
                return

            for index, raw_response in enumerate(
                res.raw_body.split('--XXXsubpartXXX')[1:-1]
            ):
                request = self._requests[index]
                handler = self._handlers[index]
                job = self._batch_jobs[index]
                res_parts = raw_response.strip().split('\r\n')
                raw_status, raw_body = res_parts[3], res_parts[-1]
                _, status_code, status_text = raw_status.split(' ', 2)
                try:
                    result = handler(Response(
                        method=request.method,
                        url=self._url_prefix + request.endpoint,
                        headers=request.headers,
                        http_code=int(status_code),
                        http_text=status_text,
                        body=raw_body
                    ))
                except ArangoError as err:
                    job.update(status='error', result=err)
                else:
                    job.update(status='done', result=result)
        finally:
            self._requests = []
            self._handlers = []
            self._batch_jobs = []

    def clear(self):
        """Clear the API requests queue and discard any batch job pointers.

        :returns: the number of API requests and batch job pointers discarded
        :rtype: int

        .. warning::
            This method will orphan any batch jobs that were issues
        """
        count = len(self._requests)
        self._requests = []
        self._handlers = []
        self._batch_jobs = []
        return count

    @property
    def aql(self):
        """Return the AQL object tailored for batch execution.

        API requests via the returned object are placed in an in-memory queue
        and committed as a whole in a single HTTP call to the ArangoDB server.

        :returns: ArangoDB query object
        :rtype: arango.query.AQL
        """
        return self._aql

    def collection(self, name):
        """Return the collection object tailored for batch execution.

        API requests via the returned object are placed in an in-memory queue
        and committed as a whole in a single HTTP call to the ArangoDB server.

        :param name: the name of the collection
        :type name: str
        :returns: the collection object
        :rtype: arango.collections.Collection
        """
        return Collection(self, name)

    def graph(self, name):
        """Return the graph object tailored for batch execution.

        API requests via the returned object are placed in an in-memory queue
        and committed as a whole in a single HTTP call to the ArangoDB server.

        :param name: the name of the graph
        :type name: str
        :returns: the graph object
        :rtype: arango.graph.Graph
        """
        return Graph(self, name)


class BatchJob(object):
    """ArangoDB batch job which holds the result of an API request.

    A batch job tracks the status of a queued API request and its result.
    """

    def __init__(self):
        self._id = uuid4()
        self._status = 'pending'
        self._result = None

    def __repr__(self):
        return '<ArangoDB batch job {}>'.format(self._id)

    @property
    def id(self):
        """Return the UUID of the batch job.

        :return: the UUID of the batch job
        :rtype: str
        """
        return self._id

    def update(self, status, result=None):
        """Update the status and the result of the batch job.

        This method designed to be used internally only.

        :param status: the status of the job
        :type status: int
        :param result: the result of the job
        :type result: object
        """
        self._status = status
        self._result = result

    def status(self):
        """Return the status of the batch job.

        :returns: the batch job status, which can be ``"pending"`` (the job is
            still waiting to be committed), ``"done"`` (the job completed) or
            ``"error"`` (the job raised an exception)
        :rtype: str
        """
        return self._status

    def result(self):
        """Return the result of the job or raise its error.

        :returns: the result of the batch job if the job is successful
        :rtype: object
        :raises ArangoError: if the batch job failed
        """
        return self._result
