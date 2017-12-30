from arango_internals.jobs import BaseJob


class SynchronousResultJob(BaseJob):
    def __new__(cls, handler, response=None, job_id=None):
        job = BaseJob(handler, response=response, job_id=job_id)

        res = job.result(raise_errors=True)

        return res
