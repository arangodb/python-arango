__all__ = [
    "suppress_warning",
    "get_col_name",
    "get_doc_id",
    "is_none_or_int",
    "is_none_or_str",
]

import logging
from contextlib import contextmanager
from typing import Any, Iterator, Union

from arango.exceptions import DocumentParseError
from arango.typings import Json


@contextmanager
def suppress_warning(logger_name: str) -> Iterator[None]:
    """Suppress logger messages.

    :param logger_name: Full name of the logger.
    :type logger_name: str
    """
    logger = logging.getLogger(logger_name)
    original_log_level = logger.getEffectiveLevel()
    logger.setLevel(logging.CRITICAL)
    yield
    logger.setLevel(original_log_level)


def get_col_name(doc: Union[str, Json]) -> str:
    """Return the collection name from input.

    :param doc: Document ID or body with "_id" field.
    :type doc: str | dict
    :return: Collection name.
    :rtype: str
    :raise arango.exceptions.DocumentParseError: If document ID is missing.
    """
    try:
        doc_id: str = doc["_id"] if isinstance(doc, dict) else doc
    except KeyError:
        raise DocumentParseError('field "_id" required')
    else:
        return doc_id.split("/", 1)[0]


def get_doc_id(doc: Union[str, Json]) -> str:
    """Return the document ID from input.

    :param doc: Document ID or body with "_id" field.
    :type doc: str | dict
    :return: Document ID.
    :rtype: str
    :raise arango.exceptions.DocumentParseError: If document ID is missing.
    """
    try:
        doc_id: str = doc["_id"] if isinstance(doc, dict) else doc
    except KeyError:
        raise DocumentParseError('field "_id" required')
    else:
        return doc_id


def is_none_or_int(obj: Any) -> bool:
    """Check if obj is None or an integer.

    :param obj: Object to check.
    :type obj: object
    :return: True if object is None or an integer.
    :rtype: bool
    """
    return obj is None or (isinstance(obj, int) and obj >= 0)


def is_none_or_str(obj: Any) -> bool:
    """Check if obj is None or a string.

    :param obj: Object to check.
    :type obj: object
    :return: True if object is None or a string.
    :rtype: bool
    """
    return obj is None or isinstance(obj, str)
