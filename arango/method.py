
# TODO Future implementation to replace the hacky _batch arguments
class ArangoRequest(object):

    def __init__(self, api):
        self._api = api

    def request_info(self, *args, **kwargs):
        raise NotImplementedError

    def handle_response(self, res):
        raise NotImplementedError

    def javascript(self, *args, **kwargs):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        request = self.request_info(*args, **kwargs)
        method = getattr(self._api, request["method"])
        method_kwargs = {}
        for component in ["path", "params", "data", "headers"]:
            if component in request:
                method_kwargs[component] = request[component]
        endpoint = request["endpoint"]
        return handle_response(http_method(**method_kwargs))
