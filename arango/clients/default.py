"""Default client using requests."""

import requests

from arango.response import ArangoResponse
from arango.clients.base import BaseArangoClient


class DefaultArangoClient(BaseArangoClient):

    def head(self, url, params=None, headers=None, auth=None):
        res = requests.head(
            url=url,
            params=params,
            headers=headers,
            auth=auth,
        )
        return ArangoResponse(res.status_code, res.text)

    def get(self, url, params=None, headers=None, auth=None):
        res = requests.get(
            url=url,
            params=params,
            headers=headers,
            auth=auth,
        )
        return ArangoResponse(res.status_code, res.text)

    def put(self, url, data=None, params=None, headers=None, auth=None):
        res = requests.put(
            url=url,
            data=data,
            params=params,
            headers=headers,
            auth=auth,
        )
        return ArangoResponse(res.status_code, res.text)

    def post(self, url, data=None, params=None, headers=None, auth=None):
        res = requests.post(
            url=url,
            data="" if data is None else data,
            params={} if params is None else params,
            headers={} if headers is None else headers,
            auth=auth
        )
        return ArangoResponse(res.status_code, res.text)

    def patch(self, url, data=None, params=None, headers=None, auth=None):
        res = requests.patch(
            url=url,
            data=data,
            params=params,
            headers=headers,
            auth=auth,
        )
        return ArangoResponse(res.status_code, res.text)

    def delete(self, url, params=None, headers=None, auth=None):
        res = requests.delete(
            url=url,
            params=params,
            headers=headers,
            auth=auth,
        )
        return ArangoResponse(res.status_code, res.text)
