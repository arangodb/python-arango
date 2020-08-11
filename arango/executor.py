from __future__ import absolute_import, unicode_literals

__all__ = [
    'DefaultExecutor',
    'AsyncExecutor',
    'BatchExecutor',
    'TransactionExecutor'
]

from collections import OrderedDict
from uuid import uuid4

from six import moves

from arango.exceptions import (
    AsyncExecuteError,
    BatchStateError,
    BatchExecuteError,
    TransactionAbortError,
    TransactionCommitError,
    TransactionStatusError,
    TransactionInitError
)
from arango.job import (
    AsyncJob,
    BatchJob
)
from arango.request import Request
from arango.response import Response
from arango.utils import suppress_warning


class Executor(object):  # pragma: no cover
    """Base class for API executors.

    API executors dictate how API requests are executed depending on the
    execution context (i.e. "default", "async", "batch", "transaction").

    :param connection: HTTP connection.
    :type connection: arango.connection.Connection
    """
    context = None

    def __init__(self, connection):
        self._conn = connection

    def execute(self, request, response_handler):
        """Execute an API request.

        :param request: HTTP request.
        :type request: arango.request.Request
        :param response_handler: HTTP response handler.
        :type response_handler: callable
        :return: API execution result or job.
        :rtype: str | bool | int | list | dict | arango.job.Job
        """
        raise NotImplementedError


class DefaultExecutor(Executor):
    """Default API executor.

    :param connection: HTTP connection.
    :type connection: arango.connection.Connection
    """
    context = 'default'

    def __init__(self, connection):
        super(DefaultExecutor, self).__init__(connection)

    def execute(self, request, response_handler):
        """Execute an API request and return the result.

        :param request: HTTP request.
        :type request: arango.request.Request
        :param response_handler: HTTP response handler.
        :type response_handler: callable
        :return: API execution result.
        :rtype: str | bool | int | list | dict
        """
        resp = self._conn.send_request(request)
        return response_handler(resp)


class AsyncExecutor(Executor):
    """Async API Executor.

    :param connection: HTTP connection.
    :type connection: arango.connection.Connection
    :param return_result: If set to True, API executions return instances of
        :class:`arango.job.AsyncJob` and results can be retrieved from server
        once available. If set to False, API executions return None and no
        results are stored on server.
    :type return_result: bool
    """
    context = 'async'

    def __init__(self, connection, return_result):
        super(AsyncExecutor, self).__init__(connection)
        self._return_result = return_result

    def execute(self, request, response_handler):
        """Execute an API request asynchronously.

        :param request: HTTP request.
        :type request: arango.request.Request
        :param response_handler: HTTP response handler.
        :type response_handler: callable
        :return: Async job or None if **return_result** parameter was set to
            False during initialization.
        :rtype: arango.job.AsyncJob | None
        """
        if self._return_result:
            request.headers['x-arango-async'] = 'store'
        else:
            request.headers['x-arango-async'] = 'true'

        resp = self._conn.send_request(request)
        if not resp.is_success:
            raise AsyncExecuteError(resp, request)
        if not self._return_result:
            return None

        job_id = resp.headers['x-arango-async-id']
        return AsyncJob(self._conn, job_id, response_handler)


class BatchExecutor(Executor):
    """Batch API executor.

    :param connection: HTTP connection.
    :type connection: arango.connection.Connection
    :param return_result: If set to True, API executions return instances of
        :class:`arango.job.BatchJob` that are populated with results on commit.
        If set to False, API executions return None and no results are tracked
        client-side.
    :type return_result: bool
    """
    context = 'batch'

    def __init__(self, connection, return_result):
        super(BatchExecutor, self).__init__(connection)
        self._return_result = return_result
        self._queue = OrderedDict()
        self._committed = False

    # noinspection PyMethodMayBeStatic,PyUnresolvedReferences
    def _stringify_request(self, request):
        path = request.endpoint

        if request.params is not None:
            path += '?' + moves.urllib.parse.urlencode(request.params)
        buffer = ['{} {} HTTP/1.1'.format(request.method, path)]

        if request.headers is not None:
            for key, value in sorted(request.headers.items()):
                buffer.append('{}: {}'.format(key, value))

        if request.data is not None:
            serialized = self._conn.serialize(request.data)
            buffer.append('\r\n' + serialized)

        return '\r\n'.join(buffer)

    @property
    def jobs(self):
        """Return the queued batch jobs.

        :return: Batch jobs or None if **return_result** parameter was set to
            False during initialization.
        :rtype: [arango.job.BatchJob] | None
        """
        if not self._return_result:
            return None
        return [job for _, job in self._queue.values()]

    def execute(self, request, response_handler):
        """Place the request in the batch queue.

        :param request: HTTP request.
        :type request: arango.request.Request
        :param response_handler: HTTP response handler.
        :type response_handler: callable
        :return: Batch job or None if **return_result** parameter was set to
            False during initialization.
        :rtype: arango.job.BatchJob | None
        :raise arango.exceptions.BatchStateError: If batch was already
            committed.
        """
        if self._committed:
            raise BatchStateError('batch already committed')

        job = BatchJob(response_handler)
        self._queue[job.id] = (request, job)
        return job if self._return_result else None

    def commit(self):
        """Execute the queued requests in a single batch API request.

        If **return_result** parameter was set to True during initialization,
        :class:`arango.job.BatchJob` instances are populated with results.

        :return: Batch jobs or None if **return_result** parameter was set to
            False during initialization.
        :rtype: [arango.job.BatchJob] | None
        :raise arango.exceptions.BatchStateError: If batch state is invalid
            (e.g. batch was already committed or size of response from server
            did not match the expected).
        :raise arango.exceptions.BatchExecuteError: If commit fails.
        """
        if self._committed:
            raise BatchStateError('batch already committed')
        else:
            self._committed = True

        if len(self._queue) == 0:
            return self.jobs

        # Boundary used for multipart request
        boundary = uuid4().hex

        # Build the batch request payload
        buffer = []
        for req, job in self._queue.values():
            buffer.append('--{}'.format(boundary))
            buffer.append('Content-Type: application/x-arango-batchpart')
            buffer.append('Content-Id: {}'.format(job.id))
            buffer.append('\r\n' + self._stringify_request(req))
        buffer.append('--{}--'.format(boundary))

        request = Request(
            method='post',
            endpoint='/_api/batch',
            headers={
                'Content-Type':
                    'multipart/form-data; boundary={}'.format(boundary)
            },
            data='\r\n'.join(buffer),
        )
        with suppress_warning('requests.packages.urllib3.connectionpool'):
            resp = self._conn.send_request(request)

        if not resp.is_success:
            raise BatchExecuteError(resp, request)

        if not self._return_result:
            return None

        url_prefix = resp.url.strip('/_api/batch')
        raw_resps = resp.raw_body.split('--{}'.format(boundary))[1:-1]

        if len(self._queue) != len(raw_resps):
            raise BatchStateError(
                'expecting {} parts in batch response but got {}'
                .format(len(self._queue), len(raw_resps))
            )
        for raw_resp in raw_resps:
            # Parse and breakdown the batch response body
            resp_parts = raw_resp.strip().split('\r\n')
            raw_content_id = resp_parts[1]
            raw_body = resp_parts[-1]
            raw_status = resp_parts[3]
            job_id = raw_content_id.split(' ')[1]
            _, status_code, status_text = raw_status.split(' ', 2)

            # Update the corresponding batch job
            queued_req, queued_job = self._queue[job_id]

            queued_job._status = 'done'
            resp = Response(
                method=queued_req.method,
                url=url_prefix + queued_req.endpoint,
                headers={},
                status_code=int(status_code),
                status_text=status_text,
                raw_body=raw_body
            )
            queued_job._response = self._conn.prep_response(resp)

        return self.jobs


class TransactionExecutor(Executor):
    """Executes transaction API requests.

    :param connection: HTTP connection.
    :type connection: arango.connection.Connection
    :param read: Name(s) of collections read during transaction. Read-only
        collections are added lazily but should be declared if possible to
        avoid deadlocks.
    :type read: str | [str]
    :param write: Name(s) of collections written to during transaction with
        shared access.
    :type write: str | [str]
    :param exclusive: Name(s) of collections written to during transaction
        with exclusive access.
    :type exclusive: str | [str]
    :param sync: Block until operation is synchronized to disk.
    :type sync: bool
    :param allow_implicit: Allow reading from undeclared collections.
    :type allow_implicit: bool
    :param lock_timeout: Timeout for waiting on collection locks. If not given,
        a default value is used. Setting it to 0 disables the timeout.
    :type lock_timeout: int
    :param max_size: Max transaction size in bytes.
    :type max_size: int
    """
    context = 'transaction'

    def __init__(self,
                 connection,
                 read=None,
                 write=None,
                 exclusive=None,
                 sync=None,
                 allow_implicit=None,
                 lock_timeout=None,
                 max_size=None):
        super(TransactionExecutor, self).__init__(connection)

        collections = {}
        if read is not None:
            collections['read'] = read
        if write is not None:
            collections['write'] = write
        if exclusive is not None:
            collections['exclusive'] = exclusive

        data = {'collections': collections}
        if sync is not None:
            data['waitForSync'] = sync
        if allow_implicit is not None:
            data['allowImplicit'] = allow_implicit
        if lock_timeout is not None:
            data['lockTimeout'] = lock_timeout
        if max_size is not None:
            data['maxTransactionSize'] = max_size

        request = Request(
            method='post',
            endpoint='/_api/transaction/begin',
            data=data
        )
        resp = self._conn.send_request(request)

        if not resp.is_success:
            raise TransactionInitError(resp, request)

        self._id = resp.body['result']['id']

    @property
    def id(self):
        """Return the transaction ID.

        :return: Transaction ID.
        :rtype: str
        """
        return self._id

    def execute(self, request, response_handler):
        """Execute API request in a transaction and return the result.

        :param request: HTTP request.
        :type request: arango.request.Request
        :param response_handler: HTTP response handler.
        :type response_handler: callable
        :return: API execution result.
        :rtype: str | bool | int | list | dict
        """
        request.headers['x-arango-trx-id'] = self._id
        resp = self._conn.send_request(request)
        return response_handler(resp)

    def status(self):
        """Return the transaction status.

        :return: Transaction status.
        :rtype: str
        :raise arango.exceptions.TransactionStatusError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_api/transaction/{}'.format(self._id),
        )
        resp = self._conn.send_request(request)

        if resp.is_success:
            return resp.body['result']['status']
        raise TransactionStatusError(resp, request)

    def commit(self):
        """Commit the transaction.

        :return: True if commit was successful.
        :rtype: bool
        :raise arango.exceptions.TransactionCommitError: If commit fails.
        """
        request = Request(
            method='put',
            endpoint='/_api/transaction/{}'.format(self._id),
        )
        resp = self._conn.send_request(request)

        if resp.is_success:
            return True
        raise TransactionCommitError(resp, request)

    def abort(self):
        """Abort the transaction.

        :return: True if the abort operation was successful.
        :rtype: bool
        :raise arango.exceptions.TransactionAbortError: If abort fails.
        """
        request = Request(
            method='delete',
            endpoint='/_api/transaction/{}'.format(self._id),
        )
        resp = self._conn.send_request(request)

        if resp.is_success:
            return True
        raise TransactionAbortError(resp, request)
