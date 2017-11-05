import pytest
import arango.response


def test_response_error():
    with pytest.raises(AttributeError):
        future = arango.response.FutureResponse(None)
        x = future.bad_attr
