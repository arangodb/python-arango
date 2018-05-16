from __future__ import absolute_import, unicode_literals

from requests.structures import CaseInsensitiveDict

from arango.response import Response


def test_response():
    response = Response(
        method='get',
        url='test_url',
        headers=CaseInsensitiveDict({'foo': 'bar'}),
        status_text='baz',
        status_code=200,
        raw_body='true',
    )
    assert response.method == 'get'
    assert response.url == 'test_url'
    assert response.headers == {'foo': 'bar'}
    assert response.status_code == 200
    assert response.status_text == 'baz'
    assert response.body is True
    assert response.raw_body == 'true'
    assert response.error_code is None
    assert response.error_message is None

    test_body = '{"errorNum": 1, "errorMessage": "qux"}'
    response = Response(
        method='get',
        url='test_url',
        headers=CaseInsensitiveDict({'foo': 'bar'}),
        status_text='baz',
        status_code=200,
        raw_body=test_body,
    )
    assert response.method == 'get'
    assert response.url == 'test_url'
    assert response.headers == {'foo': 'bar'}
    assert response.status_code == 200
    assert response.status_text == 'baz'
    assert response.body == {'errorNum': 1, 'errorMessage': 'qux'}
    assert response.raw_body == test_body
    assert response.error_code == 1
    assert response.error_message == 'qux'

    response = Response(
        method='get',
        url='test_url',
        headers=CaseInsensitiveDict({'foo': 'bar'}),
        status_text='baz',
        status_code=200,
        raw_body='invalid',
    )
    assert response.method == 'get'
    assert response.url == 'test_url'
    assert response.headers == {'foo': 'bar'}
    assert response.status_code == 200
    assert response.status_text == 'baz'
    assert response.body == 'invalid'
    assert response.raw_body == 'invalid'
    assert response.error_code is None
    assert response.error_message is None
