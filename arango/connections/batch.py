from __future__ import absolute_import, unicode_literals

from uuid import uuid4

from arango.request import Request
from arango.jobs import BatchJob, BaseJob
from arango.utils.lock import Lock
from arango.connections import BaseConnection
from arango.utils import HTTP_OK
from arango.exceptions import BatchExecuteError
from arango.responses import BaseResponse


class BatchExecution(BaseConnection):
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
    :param submit_timeout: the timeout to use for acquiring the lock necessary
        to submit a batch.  Only relevant in multi-threaded contexts. In single
        threaded contexts, acquiring this lock will never fail.  A value of
        <= 0 means never timeout, a positive integer value indicates the number
        of seconds to wait.
    :type submit_timeout: int
    """

    def __init__(self, connection, return_result=True, commit_on_error=False,
                 submit_timeout=-1):
        super(BatchExecution, self).__init__(
            protocol=connection.protocol,
            host=connection.host,
            port=connection.port,
            username=connection.username,
            password=connection.password,
            http_client=connection.http_client,
            database=connection.database,
            enable_logging=connection.logging_enabled
        )
        self._id = uuid4().hex
        self._return_result = return_result
        self._commit_on_error = commit_on_error
        self._requests = []  # The queue for requests
        self._batch_jobs = []  # For tracking batch jobs

        # For ensuring additions to all queues in the same order
        self._lock = Lock()

        self._batch_submit_timeout = submit_timeout
        self._type = 'batch'

        self._parent = connection

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
        :rtype: str | unicode
        """
        return self._id

    def handle_request(self, request, handler, **kwargs):
        """Handle the incoming request and response handler.

        :param request: the API request queued as part of the current batch
            request scope, and executed only when the batch is committed via
            method :func:`arango.batch.BatchExecution.commit`
        :type request: arango.request.Request
        :param handler: the response handler
        :type handler: callable
        :returns: the :class:`arango.batch.BatchJob` or None
        :rtype: :class:`arango.batch.BatchJob` | None
        """

        batch_job = None

        with self._lock:
            self._requests.append(request)

            if self._return_result:
                batch_job = BatchJob(handler)
                self._batch_jobs.append(batch_job)

        return batch_job

    @staticmethod
    def response_mapper(response):
        return response

    def commit(self):
        """Execute the queued API requests in a single HTTP call.

        If `return_response` was set to ``True`` during initialization, the
        responses are saved within an :class:`arango.batch.BatchJob` object
        for later retrieval via its :func:`arango.batch.BatchJob.result`
        method

        :returns: list of :class:`arango.batch.BatchJob` or None
        :rtype: [arango.batch.BatchJob] | None

        :raises arango.exceptions.BatchExecuteError: if the batch request
            cannot be executed
        """

        lock_res = self._lock.acquire(timeout=self._batch_submit_timeout)

        if not lock_res:
            raise BatchExecuteError('Unable to reaccquire lock within time '
                                    'period. Some thread must be holding it.')

        try:
            if len(self._requests) == 0:
                return

            raw_data_list = []
            for content_id, one_request in enumerate(self._requests, start=1):
                raw_data_list.append('--XXXsubpartXXX\r\n')
                raw_data_list.append(
                    'Content-Type: application/x-arango-batchpart\r\n')
                raw_data_list.append(
                    'Content-Id: {}\r\n\r\n'.format(content_id))
                raw_data_list.append('{}\r\n'.format(one_request.stringify()))
            raw_data_list.append('--XXXsubpartXXX--\r\n\r\n')
            raw_data = ''.join(raw_data_list)

            batch_request = Request(
                method='post',
                endpoint='/_api/batch',
                headers={
                    'Content-Type': (
                        'multipart/form-data; boundary=XXXsubpartXXX'
                    )
                },
                data=raw_data
            )

            def handler(res):
                if res.status_code not in HTTP_OK:
                    raise BatchExecuteError(res)
                if not self._return_result:
                    return

                for index, raw_response in enumerate(
                        res.raw_body.split('--XXXsubpartXXX')[1:-1]
                ):
                    request = self._requests[index]
                    job = self._batch_jobs[index]
                    res_parts = raw_response.strip().split('\r\n')
                    raw_status, raw_body = res_parts[3], res_parts[-1]
                    _, status_code, status_text = raw_status.split(' ', 2)

                    response_dict = {
                        'method': request.method,
                        'url': self._url_prefix + request.url,
                        'headers': request.headers,
                        'status_code': int(status_code),
                        'status_text': status_text,
                        'body': raw_body
                    }

                    response = BaseResponse(response_dict,
                                            self.response_mapper)

                    if int(status_code) in HTTP_OK:
                        job.update('done', response)
                    else:
                        job.update('error', response)

            BaseConnection.handle_request(self, batch_request, handler,
                                          job_class=BaseJob)\
                .result(raise_errors=True)

            return self._batch_jobs
        finally:
            self._requests = []
            self._batch_jobs = []
            self._lock.release()

    def clear(self):
        """Clear the requests queue and discard pointers to batch jobs issued.

        :returns: the number of requests (and batch job pointers) discarded
        :rtype: int

        .. warning::
            This method will orphan any batch jobs that were issued
        """
        count = len(self._requests)
        self._requests = []
        self._batch_jobs = []
        return count
