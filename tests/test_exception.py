from __future__ import absolute_import, unicode_literals

import json

import pytest
from requests.structures import CaseInsensitiveDict

from arango.exceptions import (
    ArangoServerError,
    DocumentInsertError,
    DocumentParseError,
    ArangoClientError
)
from arango.request import Request
from arango.response import Response


def test_server_error(client, col, docs):
    document = docs[0]
    with pytest.raises(DocumentInsertError) as err:
        col.insert(document, return_new=False)
        col.insert(document, return_new=False)  # duplicate key error
    exc = err.value

    assert isinstance(exc, ArangoServerError)
    assert exc.source == 'server'
    assert exc.message == str(exc)
    assert exc.message.startswith('[HTTP 409][ERR 1210] unique constraint')
    assert exc.url.startswith(client.base_url)
    assert exc.error_code == 1210
    assert exc.http_method == 'post'
    assert exc.http_code == 409
    assert exc.http_headers['Server'] == 'ArangoDB'
    assert isinstance(exc.http_headers, CaseInsensitiveDict)

    resp = exc.response
    expected_body = {
        'code': exc.http_code,
        'error': True,
        'errorNum': exc.error_code,
        'errorMessage': exc.error_message
    }
    assert isinstance(resp, Response)
    assert resp.is_success is False
    assert resp.error_code == exc.error_code
    assert resp.body == expected_body
    assert resp.error_code == 1210
    assert resp.method == 'post'
    assert resp.status_code == 409
    assert resp.status_text == 'Conflict'
    assert json.loads(resp.raw_body) == expected_body
    assert resp.headers == exc.http_headers
    assert resp.url.startswith(client.base_url)

    req = exc.request
    assert isinstance(req, Request)
    assert req.headers['content-type'] == 'application/json'
    assert req.method == 'post'
    assert req.read is None
    assert req.write == col.name
    assert req.command is None
    assert req.params == {'returnNew': 0, 'silent': 0}
    assert req.data == json.dumps(document)
    assert req.endpoint.startswith('/_api/document/' + col.name)


def test_client_error(col):
    with pytest.raises(DocumentParseError) as err:
        col.get({'_id': 'invalid'})  # malformed document
    exc = err.value

    assert isinstance(exc, ArangoClientError)
    assert exc.source == 'client'
    assert exc.error_code is None
    assert exc.error_message is None
    assert exc.message == str(exc)
    assert exc.message.startswith('bad collection name')
    assert exc.url is None
    assert exc.http_method is None
    assert exc.http_code is None
    assert exc.http_headers is None
    assert exc.response is None
