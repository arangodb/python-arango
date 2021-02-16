__all__ = ["Result"]

from typing import TypeVar, Union

from arango.job import AsyncJob, BatchJob

T = TypeVar("T")

Result = Union[T, AsyncJob[T], BatchJob[T], None]
