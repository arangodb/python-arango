import time

from arango.executor import (
    AsyncExecutor,
    BatchExecutor,
    TransactionExecutor
)
from arango.job import BatchJob, TransactionJob


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

    def __init__(self, connection):
        super(TestTransactionExecutor, self).__init__(
            connection=connection,
            timeout=0,
            sync=True,
            return_result=True,
            read=None,
            write=None
        )

    def execute(self, request, response_handler):
        if request.command is None:
            response = self._conn.send_request(request)
            return response_handler(response)

        self._committed = False
        self._queue.clear()

        job = TransactionJob(response_handler)
        self._queue[job.id] = (request, job)
        self.commit()
        return job.result()
