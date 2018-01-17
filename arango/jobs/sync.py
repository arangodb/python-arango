from arango.jobs import BaseJob


class SynchronousResultJob(BaseJob):
    def __new__(cls, handler, response=None):
        job = BaseJob(handler, response=response)

        res = job.result(raise_errors=True)

        return res
