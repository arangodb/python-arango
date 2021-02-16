__all__ = ["Response"]

from typing import Any, MutableMapping, Optional


class Response:
    """HTTP response.

    :param method: HTTP method in lowercase (e.g. "post").
    :type method: str
    :param url: API URL.
    :type url: str
    :param headers: Response headers.
    :type headers: MutableMapping
    :param status_code: Response status code.
    :type status_code: int
    :param status_text: Response status text.
    :type status_text: str
    :param raw_body: Raw response body.
    :type raw_body: str

    :ivar method: HTTP method in lowercase (e.g. "post").
    :vartype method: str
    :ivar url: API URL.
    :vartype url: str
    :ivar headers: Response headers.
    :vartype headers: MutableMapping
    :ivar status_code: Response status code.
    :vartype status_code: int
    :ivar status_text: Response status text.
    :vartype status_text: str
    :ivar raw_body: Raw response body.
    :vartype raw_body: str
    :ivar body: JSON-deserialized response body.
    :vartype body: str | bool | int | float | list | dict | None
    :ivar error_code: Error code from ArangoDB server.
    :vartype error_code: int
    :ivar error_message: Error message from ArangoDB server.
    :vartype error_message: str
    :ivar is_success: True if response status code was 2XX.
    :vartype is_success: bool
    """

    __slots__ = (
        "method",
        "url",
        "headers",
        "status_code",
        "status_text",
        "body",
        "raw_body",
        "error_code",
        "error_message",
        "is_success",
    )

    def __init__(
        self,
        method: str,
        url: str,
        headers: MutableMapping[str, str],
        status_code: int,
        status_text: str,
        raw_body: str,
    ) -> None:
        self.method = method.lower()
        self.url = url
        self.headers = headers
        self.status_code = status_code
        self.status_text = status_text
        self.raw_body = raw_body

        # Populated later
        self.body: Any = None
        self.error_code: Optional[int] = None
        self.error_message: Optional[str] = None
        self.is_success: Optional[bool] = None
