from __future__ import absolute_import, unicode_literals

from arango.api import APIWrapper
from arango.cursor import Cursor, ExportCursor
from arango.exceptions import (
    CollectionBadStatusError,
    CollectionChecksumError,
    CollectionConfigureError,
    CollectionLoadError,
    CollectionPropertiesError,
    CollectionRenameError,
    CollectionRevisionError,
    CollectionRotateJournalError,
    CollectionStatisticsError,
    CollectionTruncateError,
    CollectionUnloadError,
    DocumentCountError,
    DocumentGetError,
    DocumentInError,
    IndexCreateError,
    IndexDeleteError,
    IndexListError,
    UserAccessError,
    UserRevokeAccessError,
    UserGrantAccessError
)
from arango.request import Request
from arango.utils import HTTP_OK


class BaseCollection(APIWrapper):
    """Base ArangoDB collection.

    :param connection: ArangoDB connection object
    :type connection: arango.connection.Connection
    :param name: the name of the collection
    :type name: str  | unicode
    """

    TYPES = {
        2: 'document',
        3: 'edge'
    }

    STATUSES = {
        1: 'new',
        2: 'unloaded',
        3: 'loaded',
        4: 'unloading',
        5: 'deleted',
        6: 'loading'
    }

    def __init__(self, connection, name):
        super(BaseCollection, self).__init__(connection)
        self._name = name

    def __iter__(self):
        """Iterate through the documents in the collection.

        :returns: the document cursor
        :rtype: arango.cursor.Cursor
        :raises arango.exceptions.DocumentGetError: if the documents cannot
            be fetched from the collection
        """
        res = self._conn.put(
            endpoint='/_api/simple/all',
            data={'collection': self._name}
        )
        if res.status_code not in HTTP_OK:
            raise DocumentGetError(res)
        return Cursor(self._conn, res.body)

    def __len__(self):
        """Return the number of documents in the collection.

        :returns: the number of documents
        :rtype: int
        :raises arango.exceptions.DocumentCountError: if the document
            count cannot be retrieved
        """
        res = self._conn.get('/_api/collection/{}/count'.format(self._name))
        if res.status_code not in HTTP_OK:
            raise DocumentCountError(res)
        return res.body['count']

    def __getitem__(self, key):
        """Return a document by its key from the collection.

        :param key: the document key
        :type key: str  | unicode
        :returns: the document
        :rtype: dict
        :raises arango.exceptions.DocumentGetError: if the document cannot
            be fetched from the collection
        """
        res = self._conn.get('/_api/document/{}/{}'.format(self._name, key))
        if res.status_code == 404 and res.error_code == 1202:
            return None
        elif res.status_code not in HTTP_OK:
            raise DocumentGetError(res)
        return res.body

    def __contains__(self, key):
        """Check if a document exists in the collection by its key.

        :param key: the document key
        :type key: dict | str | unicode
        :returns: whether the document exists
        :rtype: bool
        :raises arango.exceptions.DocumentInError: if the check cannot
            be executed
        """
        res = self._conn.get('/_api/document/{}/{}'.format(self._name, key))
        if res.status_code == 404 and res.error_code == 1202:
            return False
        elif res.status_code in HTTP_OK:
            return True
        raise DocumentInError(res)

    def _status(self, code):
        """Return the collection status text.

        :param code: the collection status code
        :type code: int
        :returns: the collection status text or ``None``
        :rtype: str  | unicode | None
        :raises arango.exceptions.CollectionBadStatusError: if the collection
            status code is unknown
        """
        if code is None:  # pragma: no cover
            return None
        try:
            return self.STATUSES[code]
        except KeyError:
            raise CollectionBadStatusError(
                'Unknown status code {}'.format(code)
            )

    @property
    def name(self):
        """Return the name of the collection.

        :returns: the name of the collection
        :rtype: str  | unicode
        """
        return self._name

    @property
    def database(self):
        """Return the name of the database the collection belongs to.

        :returns: The name of the database.
        :rtype: str | unicode
        """
        return self._conn.database

    def rename(self, new_name):
        """Rename the collection.

        :param new_name: the new name for the collection
        :type new_name: str  | unicode
        :returns: the new collection details
        :rtype: dict
        :raises arango.exceptions.CollectionRenameError: if the collection
            name cannot be changed
        """
        request = Request(
            method='put',
            endpoint='/_api/collection/{}/rename'.format(self._name),
            data={'name': new_name}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise CollectionRenameError(res)
            self._name = new_name
            return {
                'id': res.body['id'],
                'is_system': res.body['isSystem'],
                'name': res.body['name'],
                'status': self._status(res.body['status']),
                'type': self.TYPES[res.body['type']]
            }

        return self.handle_request(request, handler)

    def statistics(self):
        """Return the collection statistics.

        :returns: the collection statistics
        :rtype: dict
        :raises arango.exceptions.CollectionStatisticsError: if the
            collection statistics cannot be retrieved
        """
        request = Request(
            method='get',
            endpoint='/_api/collection/{}/figures'.format(self._name)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise CollectionStatisticsError(res)
            stats = res.body['figures']
            stats['compaction_status'] = stats.pop('compactionStatus', None)
            stats['document_refs'] = stats.pop('documentReferences', None)
            stats['last_tick'] = stats.pop('lastTick', None)
            stats['waiting_for'] = stats.pop('waitingFor', None)
            stats['uncollected_logfile_entries'] = stats.pop(
                'uncollectedLogfileEntries', None
            )
            return stats

        return self.handle_request(request, handler)

    def revision(self):
        """Return the collection revision.

        :returns: the collection revision
        :rtype: str  | unicode
        :raises arango.exceptions.CollectionRevisionError: if the
            collection revision cannot be retrieved
        """
        request = Request(
            method='get',
            endpoint='/_api/collection/{}/revision'.format(self._name)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise CollectionRevisionError(res)
            return res.body['revision']

        return self.handle_request(request, handler)

    def properties(self):
        """Return the collection properties.

        :returns: The collection properties.
        :rtype: dict
        :raises arango.exceptions.CollectionPropertiesError: If the
            collection properties cannot be retrieved.
        """
        request = Request(
            method='get',
            endpoint='/_api/collection/{}/properties'.format(self._name)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise CollectionPropertiesError(res)

            key_options = res.body.get('keyOptions', {})

            return {
                'id': res.body.get('id'),
                'name': res.body.get('name'),
                'edge': res.body.get('type') == 3,
                'sync': res.body.get('waitForSync'),
                'status': self._status(res.body.get('status')),
                'compact': res.body.get('doCompact'),
                'system': res.body.get('isSystem'),
                'volatile': res.body.get('isVolatile'),
                'journal_size': res.body.get('journalSize'),
                'keygen': key_options.get('type'),
                'user_keys': key_options.get('allowUserKeys'),
                'key_increment': key_options.get('increment'),
                'key_offset': key_options.get('offset')
            }

        return self.handle_request(request, handler)

    def configure(self, sync=None, journal_size=None):
        """Configure the collection properties.

        Only *sync* and *journal_size* properties are configurable.

        :param sync: Wait for the operation to sync to disk.
        :type sync: bool
        :param journal_size: The journal size.
        :type journal_size: int
        :returns: the new collection properties
        :rtype: dict
        :raises arango.exceptions.CollectionConfigureError: if the
            collection properties cannot be configured
        """
        data = {}
        if sync is not None:
            data['waitForSync'] = sync
        if journal_size is not None:
            data['journalSize'] = journal_size

        request = Request(
            method='put',
            endpoint='/_api/collection/{}/properties'.format(self._name),
            data=data
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise CollectionConfigureError(res)

            key_options = res.body.get('keyOptions', {})

            return {
                'id': res.body.get('id'),
                'name': res.body.get('name'),
                'edge': res.body.get('type') == 3,
                'sync': res.body.get('waitForSync'),
                'status': self._status(res.body.get('status')),
                'compact': res.body.get('doCompact'),
                'system': res.body.get('isSystem'),
                'volatile': res.body.get('isVolatile'),
                'journal_size': res.body.get('journalSize'),
                'keygen': key_options.get('type'),
                'user_keys': key_options.get('allowUserKeys'),
                'key_increment': key_options.get('increment'),
                'key_offset': key_options.get('offset')
            }

        return self.handle_request(request, handler)

    def load(self):
        """Load the collection into memory.

        :returns: the collection status
        :rtype: str  | unicode
        :raises arango.exceptions.CollectionLoadError: if the collection
            cannot be loaded into memory
        """
        request = Request(
            method='put',
            endpoint='/_api/collection/{}/load'.format(self._name),
            command='db.{}.unload()'.format(self._name)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise CollectionLoadError(res)
            return self._status(res.body['status'])

        return self.handle_request(request, handler)

    def unload(self):
        """Unload the collection from memory.

        :returns: the collection status
        :rtype: str  | unicode
        :raises arango.exceptions.CollectionUnloadError: if the collection
            cannot be unloaded from memory
        """
        request = Request(
            method='put',
            endpoint='/_api/collection/{}/unload'.format(self._name),
            command='db.{}.unload()'.format(self._name)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise CollectionUnloadError(res)
            return self._status(res.body['status'])

        return self.handle_request(request, handler)

    def rotate(self):
        """Rotate the collection journal.

        :returns: the result of the operation
        :rtype: dict
        :raises arango.exceptions.CollectionRotateJournalError: if the
            collection journal cannot be rotated
        """
        request = Request(
            method='put',
            endpoint='/_api/collection/{}/rotate'.format(self._name),
            command='db.{}.rotate()'.format(self._name)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise CollectionRotateJournalError(res)
            return res.body['result']  # pragma: no cover

        return self.handle_request(request, handler)

    def checksum(self, with_rev=False, with_data=False):
        """Return the collection checksum.

        :param with_rev: include the document revisions in the checksum
            calculation
        :type with_rev: bool
        :param with_data: include the document data in the checksum
            calculation
        :type with_data: bool
        :returns: the collection checksum
        :rtype: int
        :raises arango.exceptions.CollectionChecksumError: if the
            collection checksum cannot be retrieved
        """
        request = Request(
            method='get',
            endpoint='/_api/collection/{}/checksum'.format(self._name),
            params={'withRevision': with_rev, 'withData': with_data}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise CollectionChecksumError(res)
            return int(res.body['checksum'])

        return self.handle_request(request, handler)

    def truncate(self):
        """Truncate the collection.

        :returns: the collection details
        :rtype: dict
        :raises arango.exceptions.CollectionTruncateError: if the collection
            cannot be truncated
        """
        request = Request(
            method='put',
            endpoint='/_api/collection/{}/truncate'.format(self._name),
            command='db.{}.truncate()'.format(self._name)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise CollectionTruncateError(res)
            return {
                'id': res.body['id'],
                'is_system': res.body['isSystem'],
                'name': res.body['name'],
                'status': self._status(res.body['status']),
                'type': self.TYPES[res.body['type']]
            }

        return self.handle_request(request, handler)

    def count(self):
        """Return the number of documents in the collection.

        :returns: the number of documents
        :rtype: int
        :raises arango.exceptions.DocumentCountError: if the document
            count cannot be retrieved
        """
        request = Request(
            method='get',
            endpoint='/_api/collection/{}/count'.format(self._name)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentCountError(res)
            return res.body['count']

        return self.handle_request(request, handler)

    def has(self, key, rev=None, match_rev=True):
        """Check if a document exists in the collection by its key.

        :param key: the document key
        :type key: dict | str | unicode
        :param rev: the document revision to be compared against the revision
            of the target document
        :type rev: str  | unicode
        :param match_rev: if ``True``, check if the given revision and
            the target document's revisions are the same, otherwise check if
            the revisions are different (this flag has an effect only when
            **rev** is given)
        :type match_rev: bool
        :returns: whether the document exists
        :rtype: bool
        :raises arango.exceptions.DocumentRevisionError: if the given revision
            does not match the revision of the retrieved document
        :raises arango.exceptions.DocumentInError: if the check cannot
            be executed
        """
        request = Request(
            method='get',  # TODO async seems to freeze when using 'head'
            endpoint='/_api/document/{}/{}'.format(self._name, key),
            headers=(
                {'If-Match' if match_rev else 'If-None-Match': rev}
                if rev is not None else {}
            )
        )

        def handler(res):
            if res.status_code == 404 and res.error_code == 1202:
                return False
            elif res.status_code in HTTP_OK:
                return True
            raise DocumentInError(res)

        return self.handle_request(request, handler)

    def all(self,
            skip=None,
            limit=None):
        """Return all documents in the collection using a server cursor.

        :param skip: the number of documents to skip
        :type skip: int
        :param limit: the max number of documents fetched by the cursor
        :type limit: int
        :returns: the document cursor
        :rtype: arango.cursor.Cursor
        :raises arango.exceptions.DocumentGetError: if the documents in
            the collection cannot be retrieved
        """

        data = {'collection': self._name}
        if skip is not None:
            data['skip'] = skip
        if limit is not None:
            data['limit'] = limit

        request = Request(
            method='put',
            endpoint='/_api/simple/all',
            data=data
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentGetError(res)
            return Cursor(self._conn, res.body)

        return self.handle_request(request, handler)

    def export(self,
               limit=None,
               count=False,
               batch_size=None,
               flush=None,
               flush_wait=None,
               ttl=None,
               filter_fields=None,
               filter_type='include'):  # pragma: no cover
        """"Export all documents in the collection using a server cursor.

        :param flush: flush the WAL prior to the export
        :type flush: bool
        :param flush_wait: the max wait time in seconds for the WAL flush
        :type flush_wait: int
        :param count: include the document count in the server cursor
            (default: ``False``)
        :type count: bool
        :param batch_size: the max number of documents in the batch fetched by
            th cursor in one round trip
        :type batch_size: int
        :param limit: the max number of documents fetched by the cursor
        :type limit: int
        :param ttl: time-to-live for the cursor on the server
        :type ttl: int
        :param filter_fields: list of document fields to filter by
        :type filter_fields: list
        :param filter_type: ``"include"`` (default) or ``"exclude"``
        :type filter_type: str  | unicode
        :returns: the document export cursor
        :rtype: arango.cursor.ExportCursor
        :raises arango.exceptions.DocumentGetError: if the documents in
            the collection cannot be exported

        .. note::
            If **flush** is not set to ``True``, the documents in WAL during
            time of the retrieval are *not* included by the server cursor
        """
        data = {'count': count}
        if flush is not None:  # pragma: no cover
            data['flush'] = flush
        if flush_wait is not None:  # pragma: no cover
            data['flushWait'] = flush_wait
        if batch_size is not None:
            data['batchSize'] = batch_size
        if limit is not None:
            data['limit'] = limit
        if ttl is not None:
            data['ttl'] = ttl
        if filter_fields is not None:
            data['restrict'] = {
                'fields': filter_fields,
                'type': filter_type
            }
        request = Request(
            method='post',
            endpoint='/_api/export',
            params={'collection': self._name},
            data=data
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentGetError(res)
            return ExportCursor(self._conn, res.body)

        return self.handle_request(request, handler)

    def find(self, filters, offset=None, limit=None):
        """Return all documents that match the given filters.

        :param filters: the document filters
        :type filters: dict
        :param offset: the number of documents to skip initially
        :type offset: int
        :param limit: the max number of documents to return
        :type limit: int
        :returns: the document cursor
        :rtype: arango.cursor.Cursor
        :raises arango.exceptions.DocumentGetError: if the document
            cannot be fetched from the collection
        """
        data = {'collection': self._name, 'example': filters}
        if offset is not None:
            data['skip'] = offset
        if limit is not None:
            data['limit'] = limit

        request = Request(
            method='put',
            endpoint='/_api/simple/by-example',
            data=data
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentGetError(res)
            return Cursor(self._conn, res.body)

        return self.handle_request(request, handler)

    def get_many(self, keys):
        """Return multiple documents by their keys.

        :param keys: the list of document keys
        :type keys: list
        :returns: the list of documents
        :rtype: list
        :raises arango.exceptions.DocumentGetError: if the documents
            cannot be fetched from the collection
        """
        request = Request(
            method='put',
            endpoint='/_api/simple/lookup-by-keys',
            data={'collection': self._name, 'keys': keys}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentGetError(res)
            return res.body['documents']

        return self.handle_request(request, handler)

    def random(self):
        """Return a random document from the collection.

        :returns: a random document
        :rtype: dict
        :raises arango.exceptions.DocumentGetError: if the document cannot
            be fetched from the collection
        """
        request = Request(
            method='put',
            endpoint='/_api/simple/any',
            data={'collection': self._name}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentGetError(res)
            return res.body['document']

        return self.handle_request(request, handler)

    def find_near(self, latitude, longitude, limit=None):
        """Return documents near a given coordinate.

        By default, at most 100 documents near the coordinate are returned.
        Documents returned are sorted according to distance, with the nearest
        document being the first. If there are documents of equal distance,
        they are be randomly chosen from the set until the limit is reached.

        :param latitude: the latitude
        :type latitude: int
        :param longitude: the longitude
        :type longitude: int
        :param limit: the max number of documents to return
        :type limit: int
        :returns: the document cursor
        :rtype: arango.cursor.Cursor
        :raises arango.exceptions.DocumentGetError: if the documents
            cannot be fetched from the collection

        .. note::
            A geo index must be defined in the collection for this method to
            be used
        """
        full_query = """
        FOR doc IN NEAR(@collection, @latitude, @longitude{})
            RETURN doc
        """.format(', @limit' if limit is not None else '')

        bind_vars = {
            'collection': self._name,
            'latitude': latitude,
            'longitude': longitude
        }
        if limit is not None:
            bind_vars['limit'] = limit

        request = Request(
            method='post',
            endpoint='/_api/cursor',
            data={'query': full_query, 'bindVars': bind_vars}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentGetError(res)
            return Cursor(self._conn, res.body)

        return self.handle_request(request, handler)

    def find_in_range(self,
                      field,
                      lower,
                      upper,
                      offset=0,
                      limit=100,
                      inclusive=True):
        """Return documents within a given range in a random order.

        :param field: the name of the field to use
        :type field: str  | unicode
        :param lower: the lower bound
        :type lower: int
        :param upper: the upper bound
        :type upper: int
        :param offset: the number of documents to skip
        :type offset: int
        :param limit: the max number of documents to return
        :type limit: int
        :param inclusive: include the lower and upper bounds
        :type inclusive: bool
        :returns: the document cursor
        :rtype: arango.cursor.Cursor
        :raises arango.exceptions.DocumentGetError: if the documents
            cannot be fetched from the collection

        .. note::
            A geo index must be defined in the collection for this method to
            be used
        """
        if inclusive:
            full_query = """
            FOR doc IN @@collection
                FILTER doc.@field >= @lower && doc.@field <= @upper
                LIMIT @skip, @limit
                RETURN doc
            """
        else:
            full_query = """
            FOR doc IN @@collection
                FILTER doc.@field > @lower && doc.@field < @upper
                LIMIT @skip, @limit
                RETURN doc
            """
        bind_vars = {
            '@collection': self._name,
            'field': field,
            'lower': lower,
            'upper': upper,
            'skip': offset,
            'limit': limit
        }

        request = Request(
            method='post',
            endpoint='/_api/cursor',
            data={'query': full_query, 'bindVars': bind_vars}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentGetError(res)
            return Cursor(self._conn, res.body)

        return self.handle_request(request, handler)

    # TODO the WITHIN geo function does not seem to work properly
    def find_in_radius(self, latitude, longitude, radius, distance_field=None):
        """Return documents within a given radius in a random order.

        :param latitude: the latitude
        :type latitude: int
        :param longitude: the longitude
        :type longitude: int
        :param radius: the maximum radius
        :type radius: int
        :param distance_field: the key containing the distance
        :type distance_field: str  | unicode
        :returns: the document cursor
        :rtype: arango.cursor.Cursor
        :raises arango.exceptions.DocumentGetError: if the documents
            cannot be fetched from the collection

        .. note::
            A geo index must be defined in the collection for this method to
            be used
        """
        full_query = """
        FOR doc IN WITHIN(@collection, @latitude, @longitude, @radius{})
            RETURN doc
        """.format(', @distance' if distance_field is not None else '')

        bind_vars = {
            'collection': self._name,
            'latitude': latitude,
            'longitude': longitude,
            'radius': radius
        }
        if distance_field is not None:
            bind_vars['distance'] = distance_field

        request = Request(
            method='post',
            endpoint='/_api/cursor',
            data={'query': full_query, 'bindVars': bind_vars}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentGetError(res)
            return Cursor(self._conn, res.body)

        return self.handle_request(request, handler)

    def find_in_box(self,
                    latitude1,
                    longitude1,
                    latitude2,
                    longitude2,
                    skip=None,
                    limit=None,
                    geo_field=None):
        """Return all documents in an rectangular area.

        :param latitude1: the first latitude
        :type latitude1: int
        :param longitude1: the first longitude
        :type longitude1: int
        :param latitude2: the second latitude
        :type latitude2: int
        :param longitude2: the second longitude
        :type longitude2: int
        :param skip: the number of documents to skip
        :type skip: int
        :param limit: the max number of documents to return (if 0 is given all
            documents are returned)
        :type limit: int
        :param geo_field: the field to use for geo index
        :type geo_field: str  | unicode
        :returns: the document cursor
        :rtype: arango.cursor.Cursor
        :raises arango.exceptions.DocumentGetError: if the documents
            cannot be fetched from the collection
        """
        data = {
            'collection': self._name,
            'latitude1': latitude1,
            'longitude1': longitude1,
            'latitude2': latitude2,
            'longitude2': longitude2,
        }
        if skip is not None:
            data['skip'] = skip
        if limit is not None:
            data['limit'] = limit
        if geo_field is not None:
            data['geo'] = '/'.join([self._name, geo_field])

        request = Request(
            method='put',
            endpoint='/_api/simple/within-rectangle',
            data=data
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentGetError(res)
            return Cursor(self._conn, res.body)

        return self.handle_request(request, handler)

    def find_by_text(self, key, query, limit=None):
        """Return documents that match the specified fulltext **query**.

        :param key: the key with a fulltext index
        :type key: str  | unicode
        :param query: the fulltext query
        :type query: str  | unicode
        :param limit: the max number of documents to return
        :type limit: int
        :returns: the document cursor
        :rtype: arango.cursor.Cursor
        :raises arango.exceptions.DocumentGetError: if the documents
            cannot be fetched from the collection
        """
        full_query = """
        FOR doc IN FULLTEXT(@collection, @field, @query{})
            RETURN doc
        """.format(', @limit' if limit is not None else '')

        bind_vars = {
            'collection': self._name,
            'field': key,
            'query': query
        }
        if limit is not None:
            bind_vars['limit'] = limit

        request = Request(
            method='post',
            endpoint='/_api/cursor',
            data={'query': full_query, 'bindVars': bind_vars}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentGetError(res)
            return Cursor(self._conn, res.body)

        return self.handle_request(request, handler)

    def indexes(self):
        """Return the collection indexes.

        :returns: the collection indexes
        :rtype: [dict]
        :raises arango.exceptions.IndexListError: if the list of indexes
            cannot be retrieved

        """
        request = Request(
            method='get',
            endpoint='/_api/index',
            params={'collection': self._name}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise IndexListError(res)

            indexes = []
            for index in res.body['indexes']:
                index['id'] = index['id'].split('/', 1)[1]
                if 'minLength' in index:
                    index['min_length'] = index.pop('minLength')
                if 'geoJson' in index:
                    index['geo_json'] = index.pop('geoJson')
                if 'ignoreNull' in index:
                    index['ignore_none'] = index.pop('ignoreNull')
                if 'selectivityEstimate' in index:
                    index['selectivity'] = index.pop('selectivityEstimate')
                indexes.append(index)
            return indexes

        return self.handle_request(request, handler)

    def _add_index(self, data):
        """Helper method for creating a new index."""
        request = Request(
            method='post',
            endpoint='/_api/index',
            data=data,
            params={'collection': self._name}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise IndexCreateError(res)
            details = res.body
            details['id'] = details['id'].split('/', 1)[1]
            details.pop('error', None)
            details.pop('code', None)
            if 'minLength' in details:
                details['min_length'] = details.pop('minLength')
            if 'geoJson' in details:
                details['geo_json'] = details.pop('geoJson')
            if 'ignoreNull' in details:
                details['ignore_none'] = details.pop('ignoreNull')
            if 'selectivityEstimate' in details:
                details['selectivity'] = details.pop('selectivityEstimate')
            if 'isNewlyCreated' in details:
                details['new'] = details.pop('isNewlyCreated')
            return details

        return self.handle_request(request, handler)

    def add_hash_index(self,
                       fields,
                       unique=None,
                       sparse=None,
                       deduplicate=None):
        """Create a new hash index in the collection.

        :param fields: the document fields to index
        :type fields: list
        :param unique: whether the index is unique
        :type unique: bool
        :param sparse: index ``None``'s
        :type sparse: bool
        :param deduplicate: Controls whether inserting duplicate index values
            from the same document into a unique array index leads to a unique
            constraint error or not. If set to ``True`` (default), only a
            single instance of each non-unique index values is inserted into
            the index per document. Trying to insert a value into the index
            that already exists will always fail, regardless of the value of
            this field.
        :param deduplicate: bool
        :returns: the details on the new index
        :rtype: dict
        :raises arango.exceptions.IndexCreateError: if the hash index cannot
            be created in the collection
        """
        data = {'type': 'hash', 'fields': fields}
        if unique is not None:
            data['unique'] = unique
        if sparse is not None:
            data['sparse'] = sparse
        if deduplicate is not None:
            data['deduplicate'] = deduplicate
        return self._add_index(data)

    def add_skiplist_index(self,
                           fields,
                           unique=None,
                           sparse=None,
                           deduplicate=None):
        """Create a new skiplist index in the collection.

        A skiplist index is used to find the ranges of documents (e.g. time).

        :param fields: the document fields to index
        :type fields: list
        :param unique: whether the index is unique
        :type unique: bool
        :param sparse: index ``None``'s
        :type sparse: bool
        :param deduplicate: Controls whether inserting duplicate index values
            from the same document into a unique array index leads to a unique
            constraint error or not. If set to ``True`` (default), only a
            single instance of each non-unique index values is inserted into
            the index per document. Trying to insert a value into the index
            that already exists will always fail, regardless of the value of
            this field.
        :param deduplicate: bool
        :returns: the details on the new index
        :rtype: dict
        :raises arango.exceptions.IndexCreateError: if the skiplist index
            cannot be created in the collection
        """
        data = {'type': 'skiplist', 'fields': fields}
        if unique is not None:
            data['unique'] = unique
        if sparse is not None:
            data['sparse'] = sparse
        if deduplicate is not None:
            data['deduplicate'] = deduplicate
        return self._add_index(data)

    def add_geo_index(self, fields, ordered=None):
        """Create a geo-spatial index in the collection.

        :param fields: if given a single field, the index is created using its
            value (which must be a list with at least two floats), and if given
            a list of fields, the index is created using values of both;
            documents without the fields or with invalid values are ignored.
        :type fields: list
        :param ordered: whether the order is longitude -> latitude
        :type ordered: bool
        :returns: the details on the new index
        :rtype: dict
        :raises arango.exceptions.IndexCreateError: if the geo-spatial index
            cannot be created in the collection
        """
        data = {'type': 'geo', 'fields': fields}
        if ordered is not None:
            data['geoJson'] = ordered
        return self._add_index(data)

    def add_fulltext_index(self, fields, min_length=None):
        """Create a fulltext index in the collection.

        A fulltext index is used to find words or prefixes of words. Only words
        with textual values of minimum length are indexed. Word tokenization is
        done using the word boundary analysis provided by libicu, which uses
        the language selected during server startup. Words are indexed in their
        lower-cased form. The index supports complete match and prefix queries.

        :param fields: the field to index
        :type fields: list
        :param min_length: the minimum number of characters to index
        :type min_length: int
        :returns: the details on the new index
        :rtype: dict
        :raises arango.exceptions.IndexCreateError: if the fulltext index
            cannot be created in the collection
        """
        # TODO keep an eye on this for future ArangoDB releases
        if len(fields) > 1:
            raise IndexCreateError('Only one field is currently supported')

        data = {'type': 'fulltext', 'fields': fields}
        if min_length is not None:
            data['minLength'] = min_length
        return self._add_index(data)

    def add_persistent_index(self, fields, unique=None, sparse=None):
        """Create a persistent index in the collection.

        :param fields: the field to index
        :type fields: list
        :param unique: whether the index is unique
        :type unique: bool
        :param sparse: exclude documents that do not contain at least one of
            the indexed fields or that have a value of ``None`` in any of the
            indexed fields
        :type sparse: bool
        :returns: the details on the new index
        :rtype: dict
        :raises arango.exceptions.IndexCreateError: if the persistent index
            cannot be created in the collection

        .. note::
            Unique persistent indexes on non-sharded keys are not supported
            in a cluster
        """
        data = {'type': 'persistent', 'fields': fields}
        if unique is not None:
            data['unique'] = unique
        if sparse is not None:
            data['sparse'] = sparse
        return self._add_index(data)

    def delete_index(self, index_id, ignore_missing=False):
        """Delete an index from the collection.

        :param index_id: the ID of the index to delete
        :type index_id: str  | unicode
        :param ignore_missing: ignore missing indexes
        :type ignore_missing: bool
        :returns: whether the index was deleted successfully
        :rtype: bool
        :raises arango.exceptions.IndexDeleteError: if the specified index
            cannot be deleted from the collection
        """
        request = Request(
            method='delete',
            endpoint='/_api/index/{}/{}'.format(self._name, index_id)
        )

        def handler(res):
            if res.status_code == 404 and res.error_code == 1212:
                if ignore_missing:
                    return False
                raise IndexDeleteError(res)
            if res.status_code not in HTTP_OK:
                raise IndexDeleteError(res)
            return not res.body['error']

        return self.handle_request(request, handler)

    def user_access(self, username):
        """Return a user's access details for the collection.

        Appropriate permissions are required in order to execute this method.

        :param username: The name of the user.
        :type username: str | unicode
        :returns: The access details (e.g. ``"rw"``, ``None``)
        :rtype: str | unicode | None
        :raises: arango.exceptions.UserAccessError: If the retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_api/user/{}/database/{}/{}'.format(
                username, self.database, self.name
            )
        )

        def handler(res):
            if res.status_code in HTTP_OK:
                result = res.body['result'].lower()
                return None if result == 'none' else result
            raise UserAccessError(res)

        return self.handle_request(request, handler)

    def grant_user_access(self, username):
        """Grant user access to the collection.

        Appropriate permissions are required in order to execute this method.

        :param username: The name of the user.
        :type username: str | unicode
        :returns: Whether the operation was successful or not.
        :rtype: bool
        :raises arango.exceptions.UserGrantAccessError: If the operation fails.
        """
        request = Request(
            method='put',
            endpoint='/_api/user/{}/database/{}/{}'.format(
                username, self.database, self.name
            ),
            data={'grant': 'rw'}
        )

        def handler(res):
            if res.status_code in HTTP_OK:
                return True
            raise UserGrantAccessError(res)

        return self.handle_request(request, handler)

    def revoke_user_access(self, username):
        """Revoke user access to the collection.

        Appropriate permissions are required in order to execute this method.

        :param username: The name of the user.
        :type username: str | unicode
        :returns: Whether the operation was successful or not.
        :rtype: bool
        :raises arango.exceptions.UserRevokeAccessError: If operation fails.
        """
        request = Request(
            method='delete',
            endpoint='/_api/user/{}/database/{}/{}'.format(
                username, self.database, self.name
            )
        )

        def handler(res):
            if res.status_code in HTTP_OK:
                return True
            raise UserRevokeAccessError(res)

        return self.handle_request(request, handler)
