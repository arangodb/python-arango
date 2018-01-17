from abc import ABCMeta


class APIWrapper:
    __metaclass__ = ABCMeta

    def __init__(self, connection):
        self._conn = connection

    def handle_request(self, request, handler, job_class=None,
                       use_underlying=False):
        if use_underlying:
            connection = self._conn.underlying
        else:
            connection = self._conn

        return connection.handle_request(request, handler, job_class=job_class)
