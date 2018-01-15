from __future__ import absolute_import, unicode_literals

from arango.utils import HTTP_OK
from arango.exceptions import (
    CursorNextError,
    CursorCloseError,
)
from arango import APIWrapper
from arango import Request
from arango.jobs import BaseJob


class BaseCursor(APIWrapper):
    """ArangoDB cursor which returns documents from the server in batches.

    :param connection: ArangoDB database connection
    :type connection: arango.connections.BaseConnection
    :param init_data: the cursor initialization data
    :type init_data: dict
    :param cursor_type: One of `"cursor"` or `"export"`, which endpoint to use
    :raises CursorNextError: if the next batch cannot be retrieved
    :raises CursorCloseError: if the cursor cannot be closed

    .. note::
        This class is designed to be instantiated internally only.
    """

    def __init__(self, connection, init_data, cursor_type="cursor"):
        super(BaseCursor, self).__init__(connection)
        self._data = init_data
        self._cursor_type = cursor_type

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close(ignore_missing=True)

    def __repr__(self):
        if self.id is None:
            return '<ArangoDB cursor>'
        return '<ArangoDB cursor {}>'.format(self.id)

    @property
    def id(self):
        """Return the cursor ID.

        :returns: the cursor ID
        :rtype: str
        """
        return self._data.get('id')

    def batch(self):
        """Return the current batch of documents.

        :returns: the current batch of documents
        :rtype: list
        """
        return self._data['result']

    def has_more(self):
        """Indicates whether more results are available.

        :returns: whether more results are available
        :rtype: bool
        """
        return self._data['hasMore']

    def count(self):
        """Return the total number of documents in the results.

        .. note::
            If the cursor was not initialized with the count option enabled,
            None is returned instead.

        :returns: the total number of results
        :rtype: int
        """
        return self._data.get('count')

    def cached(self):
        """Return whether the result is cached or not.

        :return: whether the result is cached or not
        :rtype: bool
        """
        return self._data.get('cached')

    def statistics(self):
        """Return any available cursor stats.

        :return: the cursor stats
        :rtype: dict
        """
        if 'extra' in self._data and 'stats' in self._data['extra']:
            stats = dict(self._data['extra']['stats'])
            stats['modified'] = stats.pop('writesExecuted', None)
            stats['ignored'] = stats.pop('writesIgnored', None)
            stats['scanned_full'] = stats.pop('scannedFull', None)
            stats['scanned_index'] = stats.pop('scannedIndex', None)
            stats['execution_time'] = stats.pop('executionTime', None)
            return stats

    def warnings(self):
        """Return any warnings (e.g. from the query execution).

        :returns: the warnings
        :rtype: list
        """
        if 'extra' in self._data and 'warnings' in self._data['extra']:
            return self._data['extra']['warnings']

    def next(self):
        """Read the next result from the cursor.

        :returns: the next item in the cursor
        :rtype: dict
        :raises: StopIteration, CursorNextError
        """

        if len(self.batch()) == 0:
            if not self.has_more():
                raise StopIteration

            request = Request(
                method="put",
                url="/_api/{}/{}".format(self._cursor_type, self.id)
            )

            def handler(res):
                if res.status_code not in HTTP_OK:
                    raise CursorNextError(res)
                return res.body

            job = self.handle_request(request, handler, job_class=BaseJob,
                                      use_underlying=True)

            result = job.result(raise_errors=True)

            self._data = result

        return self.batch().pop(0)

    def close(self, ignore_missing=True):
        """Close the cursor and free the resources tied to it.

        :returns: whether the cursor was closed successfully
        :rtype: bool
        :param ignore_missing: ignore missing cursors
        :type ignore_missing: bool
        :raises: CursorCloseError
        """

        if not self.id:
            return False

        request = Request(
            method="delete",
            url="/_api/{}/{}".format(self._cursor_type, self.id)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                if res.status_code == 404 and ignore_missing:
                    return False

                raise CursorCloseError(res)

            return True

        return self.handle_request(request, handler, job_class=BaseJob,
                                   use_underlying=True).result(
                                                        raise_errors=True)
