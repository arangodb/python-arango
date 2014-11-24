"""ArangoDB Request Client."""

import json
import requests
from arango.util import unicode_to_str


class ClientMixin(object):
    """A simple wrapper for requests."""

    def _head(self, path="", full_path=False, **kwargs):
        """Execute an HTTP HEAD method."""
        res = requests.head(
            path if full_path else self._url_prefix + path,
            **kwargs
        )
        return res

    def _get(self, path="", full_path=False, **kwargs):
        """Execute an HTTP GET method."""
        res = requests.get(
            path if full_path else self._url_prefix + path,
            **kwargs
        )
        res.obj = unicode_to_str(res.json()) if res.text else None
        return res

    def _put(self, path="", data=None, full_path=False, **kwargs):
        """Execute an HTTP PUT method."""
        res = requests.put(
            path if full_path else self._url_prefix + path,
            "" if data is None else json.dumps(data),
            **kwargs
        )
        res.obj = unicode_to_str(res.json()) if res.text else None
        return res

    def _post(self, path="", data=None, full_path=False, **kwargs):
        """Execute an HTTP POST method."""
        res = requests.post(
            path if full_path else self._url_prefix + path,
            "" if data is None else json.dumps(data),
            **kwargs
        )
        res.obj = unicode_to_str(res.json()) if res.text else None
        return res

    def _patch(self, path="", data=None, full_path=False, **kwargs):
        """Execute an HTTP POST method."""
        res = requests.patch(
            path if full_path else self._url_prefix + path,
            "" if data is None else json.dumps(data),
            **kwargs
        )
        res.obj = unicode_to_str(res.json()) if res.text else None
        return res

    def _delete(self, path="", full_path=False, **kwargs):
        """Execute an HTTP DELETE method."""
        res = requests.delete(
            path if full_path else self._url_prefix + path,
            **kwargs
        )
        res.obj = unicode_to_str(res.json()) if res.text else None
        return res
