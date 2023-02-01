import time

from arango.executor import AsyncApiExecutor, BatchApiExecutor, TransactionApiExecutor
from arango.job import BatchJob


class TestAsyncApiExecutor(AsyncApiExecutor):
    def __init__(self, connection) -> None:
        super().__init__(connection=connection, return_result=True)

    def execute(self, request, response_handler):
        job = AsyncApiExecutor.execute(self, request, response_handler)
        while job.status() != "done":
            time.sleep(0.01)
        return job.result()


class TestBatchExecutor(BatchApiExecutor):
    def __init__(self, connection) -> None:
        super().__init__(connection=connection, return_result=True)

    def execute(self, request, response_handler):
        self._committed = False
        self._queue.clear()

        job = BatchJob(response_handler)
        self._queue[job.id] = (request, job)
        self.commit()
        return job.result()


class TestTransactionApiExecutor(TransactionApiExecutor):
    # noinspection PyMissingConstructor
    def __init__(self, connection) -> None:
        self._conn = connection

    def execute(self, request, response_handler):
        if request.read is request.write is request.exclusive is None:
            resp = self._conn.send_request(request)
            return response_handler(resp)

        super().__init__(
            connection=self._conn,
            sync=True,
            allow_implicit=False,
            lock_timeout=0,
            read=request.read,
            write=request.write,
            exclusive=request.exclusive,
        )
        result = super().execute(request, response_handler)
        self.commit()
        return result
