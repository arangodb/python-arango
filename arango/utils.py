from __future__ import absolute_import, unicode_literals

import logging
from contextlib import contextmanager

from arango.exceptions import DocumentParseError


@contextmanager
def suppress_warning(logger_name):
    """Suppress logger messages.

    :param logger_name: Full name of the logger.
    :type logger_name: str | unicode
    """
    logger = logging.getLogger(logger_name)
    original_log_level = logger.getEffectiveLevel()
    logger.setLevel(logging.CRITICAL)
    yield
    logger.setLevel(original_log_level)


def get_col_name(doc):
    """Return the collection name from input.

    :param doc: Document ID or body with "_id" field.
    :type doc: str | unicode | dict
    :return: Collection name.
    :rtype: [str | unicode]
    :raise arango.exceptions.DocumentParseError: If document ID is missing.
    """
    try:
        doc_id = doc['_id'] if isinstance(doc, dict) else doc
    except KeyError:
        raise DocumentParseError('field "_id" required')
    return doc_id.split('/', 1)[0]


def get_id(doc):
    """Return the document ID from input.

    :param doc: Document ID or body with "_id" field.
    :type doc: str | unicode | dict
    :return: Document ID.
    :rtype: str | unicode
    :raise arango.exceptions.DocumentParseError: If document ID is missing.
    """
    try:
        return doc['_id'] if isinstance(doc, dict) else doc
    except KeyError:
        raise DocumentParseError('field "_id" required')
