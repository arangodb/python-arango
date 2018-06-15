from __future__ import absolute_import, unicode_literals

__all__ = ['Cursor']

from collections import deque

from arango.exceptions import (
    CursorNextError,
    CursorCloseError,
    CursorStateError,
    CursorEmptyError
)
from arango.request import Request


class Cursor(object):
    """Cursor API wrapper.

    Cursors fetch query results from ArangoDB server in batches. Cursor objects
    are *stateful* as they store the fetched items in-memory. They must not be
    shared across threads without proper locking mechanism.

    In transactions, the entire result set is loaded into the cursor. Therefore
    you must be mindful of client-side memory capacity when running queries
    that can potentially return a large result set.

    :param connection: HTTP connection.
    :type connection: arango.connection.Connection
    :param init_data: Cursor initialization data.
    :type init_data: dict | list
    :param cursor_type: Cursor type ("cursor" or "export").
    :type cursor_type: str | unicode
    """

    __slots__ = [
        '_conn',
        '_type',
        '_id',
        '_count',
        '_cached',
        '_stats',
        '_profile',
        '_warnings',
        '_has_more',
        '_batch',
        '_count'
    ]

    def __init__(self, connection, init_data, cursor_type='cursor'):
        self._conn = connection
        self._type = cursor_type
        self._batch = deque()
        self._id = None
        self._count = None
        self._cached = None
        self._stats = None
        self._profile = None
        self._warnings = None

        if isinstance(init_data, list):
            # In transactions, cursor initialization data is a list containing
            # the entire result set.
            self._has_more = False
            self._batch.extend(init_data)
            self._count = len(init_data)
        else:
            # In other execution contexts, cursor initialization data is a dict
            # containing cursor metadata (e.g. ID, parameters).
            self._update(init_data)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def __enter__(self):
        return self

    def __len__(self):
        return self._count

    def __exit__(self, *_):
        self.close(ignore_missing=True)

    def __repr__(self):
        return '<Cursor {}>'.format(self._id) if self._id else '<Cursor>'

    def _update(self, data):
        """Update the cursor using data from ArangoDB server.

        :param data: Cursor data from ArangoDB server (e.g. results).
        :type data: dict
        """
        result = {}

        if 'id' in data:
            self._id = data['id']
            result['id'] = data['id']
        if 'count' in data:
            self._count = data['count']
            result['count'] = data['count']
        if 'cached' in data:
            self._cached = data['cached']
            result['cached'] = data['cached']

        self._has_more = data['hasMore']
        result['has_more'] = data['hasMore']

        self._batch.extend(data['result'])
        result['batch'] = data['result']

        if 'extra' in data:
            extra = data['extra']

            if 'profile' in extra:
                self._profile = extra['profile']
                result['profile'] = extra['profile']

            if 'warnings' in extra:
                self._warnings = extra['warnings']
                result['warnings'] = extra['warnings']

            if 'stats' in extra:
                stats = extra['stats']
                if 'writesExecuted' in stats:
                    stats['modified'] = stats.pop('writesExecuted')
                if 'writesIgnored' in stats:
                    stats['ignored'] = stats.pop('writesIgnored')
                if 'scannedFull' in stats:
                    stats['scanned_full'] = stats.pop('scannedFull')
                if 'scannedIndex' in stats:
                    stats['scanned_index'] = stats.pop('scannedIndex')
                if 'executionTime' in stats:
                    stats['execution_time'] = stats.pop('executionTime')
                if 'httpRequests' in stats:
                    stats['http_requests'] = stats.pop('httpRequests')
                self._stats = stats
                result['statistics'] = stats

        return result

    @property
    def id(self):
        """Return the cursor ID.

        :return: Cursor ID.
        :rtype: str | unicode
        """
        return self._id

    @property
    def type(self):
        """Return the cursor type.

        :return: Cursor type ("cursor" or "export").
        :rtype: str | unicode
        """
        return self._type

    def batch(self):
        """Return the current batch of results.

        :return: Current batch.
        :rtype: collections.deque
        """
        return self._batch

    def has_more(self):
        """Return True if more results are available on the server.

        :return: True if more results are available on the server.
        :rtype: bool
        """
        return self._has_more

    def count(self):
        """Return the total number of documents in the entire result set.

        :return: Total number of documents, or None if the count option
            was not enabled during cursor initialization.
        :rtype: int | None
        """
        return self._count

    def cached(self):
        """Return True if results are cached.

        :return: True if results are cached.
        :rtype: bool
        """
        return self._cached

    def statistics(self):
        """Return cursor statistics.

        :return: Cursor statistics.
        :rtype: dict
        """
        return self._stats

    def profile(self):
        """Return cursor performance profile.

        :return: Cursor performance profile.
        :rtype: dict
        """
        return self._profile

    def warnings(self):
        """Return any warnings from the query execution.

        :return: Warnings, or None if there are none.
        :rtype: list
        """
        return self._warnings

    def empty(self):
        """Check if the current batch is empty.

        :return: True if current batch is empty, False otherwise.
        :rtype: bool
        """
        return len(self._batch) == 0

    def next(self):
        """Pop the next item from the current batch.

        If current batch is empty/depleted, an API request is automatically
        sent to ArangoDB server to fetch the next batch and update the cursor.

        :return: Next item in current batch.
        :rtype: str | unicode | bool | int | list | dict
        :raise StopIteration: If the result set is depleted.
        :raise arango.exceptions.CursorNextError: If batch retrieval fails.
        :raise arango.exceptions.CursorStateError: If cursor ID is not set.
        """
        if self.empty():
            if not self.has_more():
                raise StopIteration
            self.fetch()

        return self.pop()

    def pop(self):
        """Pop the next item from current batch.

        If current batch is empty/depleted, an exception is raised. You must
        call :func:`arango.cursor.Cursor.fetch` to manually fetch the next
        batch from server.

        :return: Next item in current batch.
        :rtype: str | unicode | bool | int | list | dict
        :raise arango.exceptions.CursorEmptyError: If current batch is empty.
        """
        if len(self._batch) == 0:
            raise CursorEmptyError('current batch is empty')
        return self._batch.popleft()

    def fetch(self):
        """Fetch the next batch from server and update the cursor.

        :return: New batch details.
        :rtype: dict
        :raise arango.exceptions.CursorNextError: If batch retrieval fails.
        :raise arango.exceptions.CursorStateError: If cursor ID is not set.
        """
        if self._id is None:
            raise CursorStateError('cursor ID not set')
        request = Request(
            method='put',
            endpoint='/_api/{}/{}'.format(self._type, self._id)
        )
        resp = self._conn.send_request(request)

        if not resp.is_success:
            raise CursorNextError(resp, request)
        return self._update(resp.body)

    def close(self, ignore_missing=False):
        """Close the cursor and free any server resources tied to it.

        :param ignore_missing: Do not raise exception on missing cursors.
        :type ignore_missing: bool
        :return: True if cursor was closed successfully, False if cursor was
            missing on the server and **ignore_missing** was set to True, None
            if there are no cursors to close server-side (e.g. result set is
            smaller than the batch size, or in transactions).
        :rtype: bool | None
        :raise arango.exceptions.CursorCloseError: If operation fails.
        :raise arango.exceptions.CursorStateError: If cursor ID is not set.
        """
        if self._id is None:
            return None
        request = Request(
            method='delete',
            endpoint='/_api/{}/{}'.format(self._type, self._id)
        )
        resp = self._conn.send_request(request)
        if resp.is_success:
            return True
        if resp.status_code == 404 and ignore_missing:
            return False
        raise CursorCloseError(resp, request)
