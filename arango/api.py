from abc import ABCMeta


class APIWrapper:
    __metaclass__ = ABCMeta

    def __init__(self, connection):
        self._conn = connection

    def handle_request(self, request, handler):
        return self._conn.handle_request(request, handler)
