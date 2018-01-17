from arango.responses import Response


class LazyResponse(Response):  # pragma: no cover
    """Response which lazily loads all values from some future.

    :param future: The future instance which has the function result()"
    :type future: :method:result()
    :param response_mapper: the callable which maps the result to a standard
    dictionary of fields
    :type response_mapper: callable
    """

    # noinspection PyMissingConstructor
    def __init__(self, future, response_mapper):
        self._future = future
        self._response_mapper = response_mapper

    def __getattr__(self, item):
        if item in self.__slots__:
            future_result = self._future.result()
            Response.__init__(
                self,
                future_result,
                self._response_mapper
            )
            self.__getattr__ = None
            self._response_mapper = None
            self._future = None
            return getattr(self, item)
        else:
            raise AttributeError
