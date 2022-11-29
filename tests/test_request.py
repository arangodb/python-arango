from arango.request import Request


def test_request_no_data() -> None:
    request = Request(
        method="post",
        endpoint="/_api/test",
        params={"bool": True},
        headers={"foo": "bar"},
    )
    assert request.method == "post"
    assert request.endpoint == "/_api/test"
    assert request.params == {"bool": "1"}
    # assert request.headers == {
    #     "charset": "utf-8",
    #     "content-type": "application/json",
    #     "foo": "bar",
    # }
    assert request.data is None


def test_request_string_data() -> None:
    request = Request(
        method="post",
        endpoint="/_api/test",
        params={"bool": True},
        headers={"foo": "bar"},
        data="test",
    )
    assert request.method == "post"
    assert request.endpoint == "/_api/test"
    assert request.params == {"bool": "1"}
    # assert request.headers == {
    #     "charset": "utf-8",
    #     "content-type": "application/json",
    #     "foo": "bar",
    # }
    assert request.data == "test"


def test_request_json_data() -> None:
    request = Request(
        method="post",
        endpoint="/_api/test",
        params={"bool": True},
        headers={"foo": "bar"},
        data={"baz": "qux"},
    )
    assert request.method == "post"
    assert request.endpoint == "/_api/test"
    assert request.params == {"bool": "1"}
    assert request.headers["charset"] == "utf-8"
    assert request.headers["content-type"] == "application/json"
    assert request.headers["foo"] == "bar"
    assert request.data == {"baz": "qux"}


def test_request_transaction_data() -> None:
    request = Request(
        method="post",
        endpoint="/_api/test",
        params={"bool": True},
        headers={"foo": "bar"},
        data={"baz": "qux"},
    )
    assert request.method == "post"
    assert request.endpoint == "/_api/test"
    assert request.params == {"bool": "1"}
    # assert request.headers == {
    #     "charset": "utf-8",
    #     "content-type": "application/json",
    #     "foo": "bar",
    # }
    assert request.data == {"baz": "qux"}
