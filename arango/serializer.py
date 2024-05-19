__all__ = [
    "Serializer",
    "Deserializer",
    "JsonSerializer",
    "JsonDeserializer",
]

from json import dumps, loads
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Serializer(Generic[T]):
    """
    Serializer interface
    """

    def __call__(self, data: T) -> str:
        raise NotImplementedError


class Deserializer:
    """
    De-serializer interface
    """

    def __call__(self, data: str) -> Any:
        raise NotImplementedError


class JsonSerializer(Serializer[Any]):
    """
    Default JSON serializer
    """

    def __call__(self, data: Any) -> str:
        return dumps(data, separators=(",", ":"))


class JsonDeserializer(Deserializer):
    """
    Default JSON de-serializer
    """

    def __call__(self, data: str) -> Any:
        return loads(data)
