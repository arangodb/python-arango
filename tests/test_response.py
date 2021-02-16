from arango.response import Response


def test_response(conn):
    response = Response(
        method="get",
        url="test_url",
        headers={"foo": "bar"},
        status_text="baz",
        status_code=200,
        raw_body="true",
    )
    conn.prep_response(response)

    assert response.method == "get"
    assert response.url == "test_url"
    assert response.headers == {"foo": "bar"}
    assert response.status_code == 200
    assert response.status_text == "baz"
    assert response.raw_body == "true"
    assert response.body is True
    assert response.error_code is None
    assert response.error_message is None
    assert response.is_success is True

    test_body = '{"errorNum": 1, "errorMessage": "qux"}'
    response = Response(
        method="get",
        url="test_url",
        headers={"foo": "bar"},
        status_text="baz",
        status_code=200,
        raw_body=test_body,
    )
    conn.prep_response(response)

    assert response.method == "get"
    assert response.url == "test_url"
    assert response.headers == {"foo": "bar"}
    assert response.status_code == 200
    assert response.status_text == "baz"
    assert response.raw_body == test_body
    assert response.body == {"errorMessage": "qux", "errorNum": 1}
    assert response.error_code == 1
    assert response.error_message == "qux"
    assert response.is_success is False
