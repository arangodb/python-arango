"""Request Client for ArangoDB."""

import json
import requests
from arango.util import unicode_to_str


class ArangoClient(object):
    """A simple wrapper for requests."""

    def _get(self, path="", **kwargs):
        """Execute an HTTP GET method."""
        res = requests.get(self._url_prefix + path, **kwargs)
        res.obj = unicode_to_str(res.json())
        return res

    def _put(self, path="", data=None, **kwargs):
        """Execute an HTTP PUT method."""
        res = requests.put(
            self._url_prefix + path,
            "" if data is None else json.dumps(data),
            **kwargs
        )
        res.obj = unicode_to_str(res.json())
        return res

    def _post(self, path="", data=None, **kwargs):
        """Execute an HTTP POST method."""
        res = requests.post(
            self._url_prefix + path,
            "" if data is None else json.dumps(data),
            **kwargs
        )
        res.obj = unicode_to_str(res.json())
        return res

    def _delete(self, path=""):
        """Execute an HTTP DELETE method."""
        res = requests.delete(self._url_prefix + path)
        res.obj = unicode_to_str(res.json())
        return res
