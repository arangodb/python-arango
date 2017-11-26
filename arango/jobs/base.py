from uuid import uuid4

from arango.exceptions import JobResultError, ArangoError


class BaseJob(object):
    """ArangoDB job which holds the result of an API request.

    A job tracks the status of an API request and its result.
    """

    def __init__(self, handler, response=None, job_id=None, job_type="base"):
        if job_id is None:
            job_id = uuid4().hex

        self._handler = handler
        self._job_id = job_id
        self._status = 'pending'
        self._response = response
        self._result = None
        self._job_type = job_type

    def __repr__(self):
        return '<ArangoDB {} job {}>'.format(self._job_type, self._job_id)

    @property
    def id(self):
        """Return the UUID of the job.

        :return: the UUID of the job
        :rtype: str | unicode
        """
        return self._job_id

    def update(self, status, response=None):
        """Update the status and the response of the job.

        This method designed to be used internally only.

        :param status: the status of the job
        :type status: str
        :param response: the response to the job
        :type response: arango.responses.base.BaseResponse
        """

        self._status = status

        if response is not None:
            self._response = response

    def status(self):
        """Return the status of the job.

        :returns: the batch job status, which can be ``"pending"`` (the job is
            still waiting to be committed), ``"done"`` (the job completed) or
            ``"error"`` (the job raised an exception)
        :rtype: str | unicode
        """
        return self._status

    def result(self, raise_errors=False):
        """Return the result of the job or its error.

        :param raise_errors: whether to raise this result if it is an error
        :type raise_errors: bool
        :returns: the result of the batch job if the job is successful
        :rtype: object
        """
        if self._response is None:
            raise JobResultError("Job with type {} does not have a response "
                                 "assigned to it.".format(self._job_type))

        if self._result is None:
            try:
                self._result = self._handler(self._response)
            except ArangoError as err:
                self.update('error')
                self._result = err

                if raise_errors:
                    raise err

        return self._result
