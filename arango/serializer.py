__all__ = [
    "Serializer",
    "Deserializer",
    "JsonSerializer",
    "JsonDeserializer",
]

from json import dumps, loads
from typing import Generic, Sequence, TypeVar, Union

from arango.typings import DataTypes, Json

T = TypeVar("T")


class Serializer(Generic[T]):
    """
    Serializer interface.
    For the use of bulk operations, it must also support List[T].
    """

    def __call__(self, obj: Union[T, Sequence[T]]) -> str:
        raise NotImplementedError


class Deserializer(Generic[T]):
    """
    De-serializer interface
    """

    def __call__(self, s: str) -> T:
        raise NotImplementedError


class JsonSerializer(Serializer[Json]):
    """
    Default JSON serializer
    """

    def __call__(self, obj: Union[Json, Sequence[Json]]) -> str:
        return dumps(obj, separators=(",", ":"))


class JsonDeserializer(Deserializer[DataTypes]):
    """
    Default JSON de-serializer
    """

    def __call__(self, s: str) -> DataTypes:
        return loads(s)
