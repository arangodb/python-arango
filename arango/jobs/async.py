from arango.jobs import BaseJob
from arango.utils import HTTP_OK
from arango.exceptions import (
    AsyncJobCancelError,
    AsyncJobStatusError,
    AsyncJobResultError,
    AsyncJobClearError,
    AsyncExecuteError, ArangoError)
from arango import Request


class AsyncJob(BaseJob):
    """ArangoDB async job which holds the result of an API request.

    An async job tracks the status of a queued API request and its result.

    :param connection: ArangoDB database connection
    :type connection: arango.connection.Connection
    :param job_id: the ID of the async job
    :type job_id: str | unicode
    :param handler: the response handler
    :type handler: callable
    """

    def __init__(self, handler, response=None, connection=None,
                 return_result=True):
        BaseJob.__init__(self, handler, None,
                         job_id=None,
                         assign_id=False,
                         job_type='asynchronous')
        self._conn = connection
        self._initial_response = response
        self._result = None

        self._return_result = return_result

        if self._initial_response is None:
            raise ValueError('AsyncJob must be instantiated with a '
                             'response.')

        if self._conn is None:
            raise ValueError('AsyncJob must be instantiated with a '
                             'connection.')

        if not self._conn.async_ready:
            self.id

    @property
    def initial_response(self):
        if self._initial_response.status_code not in HTTP_OK:
            raise AsyncExecuteError(self._initial_response)
        return self._initial_response

    @property
    def id(self):
        """Return the UUID of the job.

        :return: the UUID of the job
        :rtype: str | unicode
        """
        if self._job_id is None:
            res = self.initial_response

            if self._return_result:
                self._job_id = res.headers['x-arango-async-id']

        return self._job_id

    def status(self):
        """Return the status of the async job from the server.

        :returns: the status of the async job, which can be ``"pending"`` (the
            job is still in the queue), ``"done"`` (the job finished or raised
            an exception), or `"cancelled"` (the job was cancelled before
            completion)
        :rtype: str | unicode
        :raises arango.exceptions.AsyncJobStatusError: if the status of the
            async job cannot be retrieved from the server
        """

        request = Request(
            method='get',
            endpoint='/_api/job/{}'.format(self.id)
        )

        def handler(res):
            if res.status_code == 204:
                self.update('pending')
            elif res.status_code in HTTP_OK:
                self.update('done')
            elif res.status_code == 404:
                raise AsyncJobStatusError(res,
                                          'Job {} missing'.format(self.id))
            else:
                raise AsyncJobStatusError(res)

            return self._status

        response = self._conn.underlying.handle_request(request, handler,
                                                        job_class=BaseJob)

        return response.result(raise_errors=True)

    def result(self, raise_errors=False):
        """Return the result of the async job if available.

        :returns: the result or the exception from the async job
        :rtype: object
        :raises arango.exceptions.AsyncJobResultError: if the result of the
            async job cannot be retrieved from the server

        .. note::
            An async job result will automatically be cleared from the server
            once fetched and will *not* be available in subsequent calls.
        """

        if not self._return_result:
            return None

        if self._result is None or \
                isinstance(self._result, BaseException):
            request = Request(
                method='put',
                endpoint='/_api/job/{}'.format(self.id)
            )

            def handler(res):
                if res.status_code == 204:
                    raise AsyncJobResultError(
                        'Job {} not done'.format(self.id))
                elif res.status_code in HTTP_OK:
                    self.update('done', res)
                elif res.status_code == 404:
                    raise AsyncJobResultError(res, 'Job {} missing'.format(
                        self.id))
                else:
                    raise AsyncJobResultError(res)

                if ('X-Arango-Async-Id' in res.headers
                        or 'x-arango-async-id' in res.headers):
                    return self._handler(res)

            try:
                self._result = self._conn.underlying.handle_request(
                    request,
                    handler,
                    job_class=BaseJob
                ).result(raise_errors=True)

            except ArangoError as err:
                self.update('error')
                self._result = err

            if raise_errors:
                if isinstance(self._result, BaseException):
                    raise self._result

        return self._result

    def cancel(self, ignore_missing=False):  # pragma: no cover
        """Cancel the async job if it is still pending.

        :param ignore_missing: ignore missing async jobs
        :type ignore_missing: bool
        :returns: ``True`` if the job was cancelled successfully, ``False`` if
            the job was not found but **ignore_missing** was set to ``True``
        :rtype: bool
        :raises arango.exceptions.AsyncJobCancelError: if the async job cannot
            be cancelled

        .. note::
            An async job cannot be cancelled once it is taken out of the queue
            (i.e. started, finished or cancelled).
        """

        request = Request(
            method='put',
            endpoint='/_api/job/{}/cancel'.format(self.id)
        )

        def handler(res):
            if res.status_code == 200:
                self.update('cancelled')
                return True
            elif res.status_code == 404:
                if ignore_missing:
                    return False
                raise AsyncJobCancelError(res,
                                          'Job {} missing'.format(self.id))
            else:
                raise AsyncJobCancelError(res)

        response = self._conn.underlying.handle_request(request, handler,
                                                        job_class=BaseJob)

        return response.result(raise_errors=True)

    def clear(self, ignore_missing=False):
        """Delete the result of the job from the server.

        :param ignore_missing: ignore missing async jobs
        :type ignore_missing: bool
        :returns: ``True`` if the result was deleted successfully, ``False``
            if the job was not found but **ignore_missing** was set to ``True``
        :rtype: bool
        :raises arango.exceptions.AsyncJobClearError: if the result of the
            async job cannot be delete from the server
        """

        request = Request(
            method='delete',
            endpoint='/_api/job/{}'.format(self.id)
        )

        def handler(res):
            if res.status_code in HTTP_OK:
                return True
            elif res.status_code == 404:
                if ignore_missing:
                    return False
                raise AsyncJobClearError(res,
                                         'Job {} missing'.format(self.id))
            else:
                raise AsyncJobClearError(res)

        response = self._conn.underlying.handle_request(request, handler,
                                                        job_class=BaseJob)

        return response.result(raise_errors=True)
