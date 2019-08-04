import time

from arango.executor import (
    AsyncExecutor,
    BatchExecutor,
    TransactionExecutor,
)
from arango.job import BatchJob


class TestAsyncExecutor(AsyncExecutor):

    def __init__(self, connection):
        super(TestAsyncExecutor, self).__init__(
            connection=connection,
            return_result=True
        )

    def execute(self, request, response_handler):
        job = AsyncExecutor.execute(self, request, response_handler)
        while job.status() != 'done':
            time.sleep(.01)
        return job.result()


class TestBatchExecutor(BatchExecutor):

    def __init__(self, connection):
        super(TestBatchExecutor, self).__init__(
            connection=connection,
            return_result=True
        )

    def execute(self, request, response_handler):
        self._committed = False
        self._queue.clear()

        job = BatchJob(response_handler)
        self._queue[job.id] = (request, job)
        self.commit()
        return job.result()


class TestTransactionExecutor(TransactionExecutor):

    # noinspection PyMissingConstructor
    def __init__(self, connection):
        self._conn = connection

    def execute(self, request, response_handler):
        if request.read is request.write is request.exclusive is None:
            resp = self._conn.send_request(request)
            return response_handler(resp)

        super(TestTransactionExecutor, self).__init__(
            connection=self._conn,
            sync=True,
            allow_implicit=False,
            lock_timeout=0,
            read=request.read,
            write=request.write,
            exclusive=request.exclusive
        )
        result = TransactionExecutor.execute(self, request, response_handler)
        self.commit()
        return result
