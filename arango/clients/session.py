"""Session based client using requests.  This is much faster than default."""

import requests

from arango.response import ArangoResponse
from arango.clients.base import BaseArangoClient


class SessionArangoClient(BaseArangoClient):
    def __init__(self):
        self.s = requests.Session()

    def head(self, url, params=None, headers=None, auth=None):
        res = self.s.head(
            url=url,
            params=params,
            headers=headers,
            auth=auth,
        )
        return ArangoResponse(res.status_code, res.text)

    def get(self, url, params=None, headers=None, auth=None):
        res = self.s.get(
            url=url,
            params=params,
            headers=headers,
            auth=auth,
        )
        return ArangoResponse(res.status_code, res.text)

    def put(self, url, data=None, params=None, headers=None, auth=None):
        res = self.s.put(
            url=url,
            data=data,
            params=params,
            headers=headers,
            auth=auth,
        )
        return ArangoResponse(res.status_code, res.text)

    def post(self, url, data=None, params=None, headers=None, auth=None):
        res = self.s.post(
            url=url,
            data="" if data is None else data,
            params={} if params is None else params,
            headers={} if headers is None else headers,
            auth=auth
        )
        return ArangoResponse(res.status_code, res.text)

    def patch(self, url, data=None, params=None, headers=None, auth=None):
        res = self.s.patch(
            url=url,
            data=data,
            params=params,
            headers=headers,
            auth=auth,
        )
        return ArangoResponse(res.status_code, res.text)

    def delete(self, url, params=None, headers=None, auth=None):
        res = self.s.delete(
            url=url,
            params=params,
            headers=headers,
            auth=auth,
        )
        return ArangoResponse(res.status_code, res.text)

    def close(self):
        self.s.close()
