from __future__ import absolute_import, unicode_literals

from json import dumps
from six import string_types

from arango.collections.base import BaseCollection
from arango.exceptions import *
from arango.request import Request
from arango.utils import HTTP_OK


class Collection(BaseCollection):
    """ArangoDB (standard) collection.

    A collection consists of documents. It is uniquely identified by its name,
    which must consist only of alphanumeric, hyphen and underscore characters.
    There are two collection types: *document* and *edge*.

    Be default, collections use the traditional key generator, which generates
    key values in a non-deterministic fashion. A deterministic, auto-increment
    key generator can be used as well.

    :param connection: ArangoDB database connection
    :type connection: arango.connection.Connection
    :param name: the name of the collection
    :type name: str | unicode
    """

    def __init__(self, connection, name):
        super(Collection, self).__init__(connection, name)

    def __repr__(self):
        return '<ArangoDB collection "{}">'.format(self._name)

    def get(self, key, rev=None, match_rev=True):
        """Retrieve a document by its key.

        :param key: the document key
        :type key: str | unicode
        :param rev: the revision to compare with that of the retrieved document
        :type rev: str | unicode
        :param match_rev: if ``True``, check if the given revision and
            the target document's revisions are the same, otherwise check if
            the revisions are different (this flag has an effect only when
            **rev** is given)
        :type match_rev: bool
        :returns: the document or ``None`` if the document is missing
        :rtype: dict
        :raises arango.exceptions.DocumentRevisionError: if the given revision
            does not match the revision of the retrieved document
        :raises arango.exceptions.DocumentGetError: if the document cannot
            be retrieved from the collection
        """
        request = Request(
            method='get',
            endpoint='/_api/document/{}/{}'.format(self._name, key),
            headers=(
                {'If-Match' if match_rev else 'If-None-Match': rev}
                if rev is not None else {}
            )
        )

        def handler(res):
            if res.status_code in {304, 412}:
                raise DocumentRevisionError(res)
            elif res.status_code == 404 and res.error_code == 1202:
                return None
            elif res.status_code in HTTP_OK:
                return res.body
            raise DocumentGetError(res)

        return self.handle_request(request, handler)

    def insert(self, document, return_new=False, sync=None):
        """Insert a new document into the collection.

        If the ``"_key"`` field is present in **document**, its value is used
        as the key of the new document. Otherwise, the key is auto-generated.
        The ``"_id"`` and ``"_rev"`` fields are ignored if present in the
        document.

        :param document: the document to insert
        :type document: dict
        :param return_new: if ``True``, the full body of the new
            document is included in the returned result
        :type return_new: bool
        :param sync: wait for the operation to sync to disk
        :type sync: bool
        :returns: the result of the insert (e.g. document key, revision)
        :rtype: dict
        :raises arango.exceptions.DocumentInsertError: if the document cannot
            be inserted into the collection

        .. note::
            Argument **return_new** has no effect in transactions
        """
        params = {'returnNew': return_new}
        if sync is not None:
            params['waitForSync'] = sync

        if self._conn.type != 'transaction':
            command = None
        else:
            command = 'db.{}.insert({},{})'.format(
                self._name,
                dumps(document),
                dumps(params)
            )

        request = Request(
            method='post',
            endpoint='/_api/document/{}'.format(self._name),
            data=document,
            params=params,
            command=command
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentInsertError(res)
            if res.status_code == 202:
                res.body['sync'] = False
            else:
                res.body['sync'] = True
            return res.body

        return self.handle_request(request, handler)

    def insert_many(self, documents, return_new=False, sync=None):
        """Insert multiple documents into the collection.

        If the ``"_key"`` fields are present in the entries in **documents**,
        their values are used as the keys of the new documents. Otherwise the
        keys are auto-generated. Any ``"_id"`` and ``"_rev"`` fields present
        in the documents are ignored.

        :param documents: the list of the new documents to insert
        :type documents: list
        :param return_new: if ``True``, the new bodies of the documents
            are included in the returned result
        :type return_new: bool
        :param sync: wait for the operation to sync to disk
        :type sync: bool
        :returns: the result of the insert (e.g. document keys, revisions)
        :rtype: dict
        :raises arango.exceptions.DocumentInsertError: if the documents cannot
            be inserted into the collection

        .. note::
            Argument **return_new** has no effect in a transaction
        """
        params = {'returnNew': return_new}
        if sync is not None:
            params['waitForSync'] = sync

        if self._conn.type != 'transaction':
            command = None
        else:
            command = 'db.{}.insert({},{})'.format(
                self._name,
                dumps(documents),
                dumps(params)
            )

        request = Request(
            method='post',
            endpoint='/_api/document/{}'.format(self._name),
            data=documents,
            params=params,
            command=command
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentInsertError(res)

            results = []
            for result in res.body:
                if '_id' not in result:
                    result = DocumentInsertError(
                        res.update_body(result)
                    )
                elif res.status_code == 202:
                    result['sync'] = False
                elif res.status_code:
                    result['sync'] = True
                results.append(result)
            return results

        return self.handle_request(request, handler)

    def update(self,
               document,
               merge=True,
               keep_none=True,
               return_new=False,
               return_old=False,
               check_rev=False,
               sync=None):
        """Update a document by its key.

        :param document: the document with updates
        :type document: dict
        :param merge: if ``True``, sub-dictionaries are merged rather
            than overwritten completely
        :type merge: bool
        :param keep_none: if ``True``, the fields with value ``None`` are
            retained in the document, otherwise they are removed
        :type keep_none: bool
        :param return_new: if ``True``, the full body of the new document is
            included in the returned result
        :type return_new: bool
        :param return_old: if ``True``, the full body of the old document is
            included in the returned result
        :type return_old: bool
        :param check_rev: if ``True``, the ``"_rev"`` field in **document**
            is compared against the revision of the target document
        :type check_rev: bool
        :param sync: wait for the operation to sync to disk
        :type sync: bool
        :returns: the result of the update (e.g. document key, revision)
        :rtype: dict
        :raises arango.exceptions.DocumentRevisionError: if the given revision
            does not match the revision of the document
        :raises arango.exceptions.DocumentUpdateError: if the document cannot
            be updated

        .. note::
            The ``"_key"`` field must be present in **document**.

        .. note::
            Arguments **return_new** and **return_old** have no effect in
            transactions
        """
        params = {
            'keepNull': keep_none,
            'mergeObjects': merge,
            'returnNew': return_new,
            'returnOld': return_old,
            'ignoreRevs': not check_rev,
            'overwrite': not check_rev
        }
        if sync is not None:
            params['waitForSync'] = sync

        if self._conn.type != 'transaction':
            command = None
        else:
            if not check_rev:
                document.pop('_rev', None)
            documents_str = dumps(document)
            command = 'db.{}.update({},{},{})'.format(
                self._name,
                documents_str,
                documents_str,
                dumps(params)
            )

        request = Request(
            method='patch',
            endpoint='/_api/document/{}/{}'.format(
                self._name, document['_key']
            ),
            data=document,
            params=params,
            command=command
        )

        def handler(res):
            if res.status_code == 412:
                raise DocumentRevisionError(res)
            elif res.status_code not in HTTP_OK:
                raise DocumentUpdateError(res)
            elif res.status_code == 202:
                res.body['sync'] = False
            else:
                res.body['sync'] = True
            res.body['_old_rev'] = res.body.pop('_oldRev')
            return res.body

        return self.handle_request(request, handler)

    def update_many(self,
                    documents,
                    merge=True,
                    keep_none=True,
                    return_new=False,
                    return_old=False,
                    check_rev=False,
                    sync=None):
        """Update multiple documents in the collection.

        :param documents: the list of documents with updates
        :type documents: list
        :param merge: if ``True``, sub-dictionaries are merged rather
            than overwritten completely
        :type merge: bool
        :param keep_none: if ``True``, the fields with value ``None`` are
            retained in the document, otherwise they are removed
        :type keep_none: bool
        :param return_new: if ``True``, the full bodies of the new documents
            are included in the returned result
        :type return_new: bool
        :param return_old: if ``True``, the full bodies of the old documents
            are included in the returned result
        :type return_old: bool
        :param check_rev: if ``True``, the ``"_rev"`` field in **document**
            is compared against the revision of the target document
        :type check_rev: bool
        :param sync: wait for the operation to sync to disk
        :type sync: bool
        :returns: the result of the update (e.g. document keys, revisions)
        :rtype: dict
        :raises arango.exceptions.DocumentRevisionError: if the given revision
            does not match the revision of the documents
        :raises arango.exceptions.DocumentUpdateError: if the documents cannot
            be updated

        .. note::
            The ``"_key"`` field must be present in **document**.

        .. note::
            Arguments **return_new** and **return_old** have no effect in
            transactions

        .. warning::
            The returned details (whose size scales with the number of target
            documents) are all brought into memory
        """
        params = {
            'keepNull': keep_none,
            'mergeObjects': merge,
            'returnNew': return_new,
            'returnOld': return_old,
            'ignoreRevs': not check_rev,
            'overwrite': not check_rev
        }
        if sync is not None:
            params['waitForSync'] = sync

        if self._conn.type != 'transaction':
            command = None
        else:
            documents_str = dumps(documents)
            command = 'db.{}.update({},{},{})'.format(
                self._name,
                documents_str,
                documents_str,
                dumps(params)
            )

        request = Request(
            method='patch',
            endpoint='/_api/document/{}'.format(self._name),
            data=documents,
            params=params,
            command=command
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentUpdateError(res)

            results = []
            for result in res.body:
                # TODO this is not clean
                if '_id' not in result:
                    # An error occurred with this particular document
                    err = res.update_body(result)
                    # Single out revision error
                    if result['errorNum'] == 1200:
                        result = DocumentRevisionError(err)
                    else:
                        result = DocumentUpdateError(err)
                else:
                    if res.status_code == 202:
                        result['sync'] = False
                    elif res.status_code:
                        result['sync'] = True
                    result['_old_rev'] = result.pop('_oldRev')
                results.append(result)

            return results

        return self.handle_request(request, handler)

    def update_match(self,
                     filters,
                     body,
                     limit=None,
                     keep_none=True,
                     sync=None):
        """Update matching documents in the collection.

        :param filters: the filters
        :type filters: dict
        :param body: the document body
        :type body: dict
        :param limit: the max number of documents to return
        :type limit: int
        :param keep_none: if ``True``, the fields with value ``None``
            are retained in the document, otherwise the fields are removed
            from the document completely
        :type keep_none: bool
        :param sync: wait for the operation to sync to disk
        :type sync: bool
        :returns: the number of documents updated
        :rtype: int
        :raises arango.exceptions.DocumentUpdateError: if the documents
            cannot be updated
        """
        data = {
            'collection': self._name,
            'example': filters,
            'newValue': body,
            'keepNull': keep_none,
        }
        if limit is not None:
            data['limit'] = limit
        if sync is not None:
            data['waitForSync'] = sync

        if self._conn.type != 'transaction':
            command = None
        else:
            command = 'db.{}.updateByExample({},{},{})'.format(
                self._name,
                dumps(filters),
                dumps(body),
                dumps(data)
            )

        request = Request(
            method='put',
            endpoint='/_api/simple/update-by-example',
            data=data,
            command=command
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentUpdateError(res)
            return res.body['updated']

        return self.handle_request(request, handler)

    def replace(self,
                document,
                return_new=False,
                return_old=False,
                check_rev=False,
                sync=None):
        """Replace a document by its key.

        :param document: the new document
        :type document: dict
        :param return_new: if ``True``, the full body of the new document is
            included in the returned result
        :type return_new: bool
        :param return_old: if ``True``, the full body of the old document is
            included in the returned result
        :type return_old: bool
        :param check_rev: if ``True``, the ``"_rev"`` field in **document**
            is compared against the revision of the target document
        :type check_rev: bool
        :param sync: wait for the operation to sync to disk
        :type sync: bool
        :returns: the result of the replace (e.g. document key, revision)
        :rtype: dict
        :raises arango.exceptions.DocumentRevisionError: if the given revision
            does not match the revision of the document
        :raises arango.exceptions.DocumentReplaceError: if the document cannot
            be replaced

        .. note::
            The ``"_key"`` field must be present in **document**. For edge
            collections the ``"_from"`` and ``"_to"`` fields must also be
            present in **document**.

        .. note::
            Arguments **return_new** and **return_old** have no effect in
            transactions

        .. warning::
            The returned details (whose size scales with the number of target
            documents) are all brought into memory

        """
        params = {
            'returnNew': return_new,
            'returnOld': return_old,
            'ignoreRevs': not check_rev,
            'overwrite': not check_rev
        }
        if sync is not None:
            params['waitForSync'] = sync

        if self._conn.type != 'transaction':
            command = None
        else:
            documents_str = dumps(document)
            command = 'db.{}.replace({},{},{})'.format(
                self._name,
                documents_str,
                documents_str,
                dumps(params)
            )

        request = Request(
            method='put',
            endpoint='/_api/document/{}/{}'.format(
                self._name, document['_key']
            ),
            params=params,
            data=document,
            command=command
        )

        def handler(res):
            if res.status_code == 412:
                raise DocumentRevisionError(res)
            if res.status_code not in HTTP_OK:
                raise DocumentReplaceError(res)
            if res.status_code == 202:
                res.body['sync'] = False
            else:
                res.body['sync'] = True
            res.body['_old_rev'] = res.body.pop('_oldRev')
            return res.body

        return self.handle_request(request, handler)

    def replace_many(self,
                     documents,
                     return_new=False,
                     return_old=False,
                     check_rev=False,
                     sync=None):
        """Replace multiple documents in the collection.

        :param documents: the list of new documents
        :type documents: list
        :param return_new: if ``True``, the full bodies of the new documents
            are included in the returned result
        :type return_new: bool
        :param return_old: if ``True``, the full bodies of the old documents
            are included in the returned result
        :type return_old: bool
        :param check_rev: if ``True``, the ``"_rev"`` field in **document**
            is compared against the revision of the target document
        :type check_rev: bool
        :param sync: wait for the operation to sync to disk
        :type sync: bool
        :returns: the result of the replace (e.g. document keys, revisions)
        :rtype: dict
        :raises arango.exceptions.DocumentReplaceError: if the documents cannot
            be replaced

        .. note::
            The ``"_key"`` fields must be present in **documents**. For edge
            collections the ``"_from"`` and ``"_to"`` fields must also be
            present in **documents**.

        .. note::
            Arguments **return_new** and **return_old** have no effect in
            transactions

        .. warning::
            The returned details (whose size scales with the number of target
            documents) are all brought into memory
        """
        params = {
            'returnNew': return_new,
            'returnOld': return_old,
            'ignoreRevs': not check_rev,
            'overwrite': not check_rev
        }
        if sync is not None:
            params['waitForSync'] = sync

        if self._conn.type != 'transaction':
            command = None
        else:
            documents_str = dumps(documents)
            command = 'db.{}.replace({},{},{})'.format(
                self._name,
                documents_str,
                documents_str,
                dumps(params)
            )

        request = Request(
            method='put',
            endpoint='/_api/document/{}'.format(self._name),
            params=params,
            data=documents,
            command=command
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentReplaceError(res)

            results = []
            for result in res.body:
                # TODO this is not clean
                if '_id' not in result:
                    # An error occurred with this particular document
                    err = res.update_body(result)
                    # Single out revision error
                    if result['errorNum'] == 1200:
                        result = DocumentRevisionError(err)
                    else:
                        result = DocumentReplaceError(err)
                else:
                    if res.status_code == 202:
                        result['sync'] = False
                    elif res.status_code:
                        result['sync'] = True
                    result['_old_rev'] = result.pop('_oldRev')
                results.append(result)

            return results

        return self.handle_request(request, handler)

    def replace_match(self, filters, body, limit=None, sync=None):
        """Replace matching documents in the collection.

        :param filters: the document filters
        :type filters: dict
        :param body: the document body
        :type body: dict
        :param limit: max number of documents to replace
        :type limit: int
        :param sync: wait for the operation to sync to disk
        :type sync: bool
        :returns: the number of documents replaced
        :rtype: int
        :raises arango.exceptions.DocumentReplaceError: if the documents
            cannot be replaced
        """
        data = {
            'collection': self._name,
            'example': filters,
            'newValue': body
        }
        if limit is not None:
            data['limit'] = limit
        if sync is not None:
            data['waitForSync'] = sync

        if self._conn.type != 'transaction':
            command = None
        else:
            command ='db.{}.replaceByExample({},{},{})'.format(
                self._name,
                dumps(filters),
                dumps(body),
                dumps(data)
            )

        request = Request(
            method='put',
            endpoint='/_api/simple/replace-by-example',
            data=data,
            command=command
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentReplaceError(res)
            return res.body['replaced']

        return self.handle_request(request, handler)

    def delete(self,
               document,
               ignore_missing=False,
               return_old=False,
               check_rev=False,
               sync=None):
        """Delete a document by its key.

        :param document: the document to delete or its key
        :type document: dict | str | unicode
        :param ignore_missing: ignore missing documents (default: ``False``)
        :type ignore_missing: bool
        :param return_old: if ``True``, the full body of the old document is
            included in the returned result (default: ``False``)
        :type return_old: bool
        :param check_rev: if ``True``, the ``"_rev"`` field in **document** is
            compared against the revision of the target document (this flag is
            only applicable when **document** is an actual document and not a
            document key)
        :type check_rev: bool
        :param sync: wait for the operation to sync to disk
        :type sync: bool
        :returns: the results of the delete (e.g. document key, new revision)
            or ``False`` if the document was missing but ignored
        :rtype: dict
        :raises arango.exceptions.DocumentRevisionError: if the given revision
            does not match the revision of the target document
        :raises arango.exceptions.DocumentDeleteError: if the document cannot
            be deleted

        .. note::
            If **document** is a dictionary it must have the ``"_key"`` field

        .. note::
            Argument **return_old** has no effect in transactions
        """
        params = {
            'returnOld': return_old,
            'ignoreRevs': not check_rev,
            'overwrite': not check_rev
        }
        if sync is not None:
            params['waitForSync'] = sync

        full_doc = not isinstance(document, string_types)
        if check_rev and full_doc and '_rev' in document:
            headers = {'If-Match': document['_rev']}
        else:
            headers = {}

        if self._conn.type != 'transaction':
            command = None
        else:
            command = 'db.{}.remove({},{})'.format(
                self._name,
                dumps(document if full_doc else {'_key': document}),
                dumps(params)
            )

        request = Request(
            method='delete',
            endpoint='/_api/document/{}/{}'.format(
                self._name, document['_key'] if full_doc else document
            ),
            params=params,
            headers=headers,
            command=command
        )

        def handler(res):
            if res.status_code == 412:
                raise DocumentRevisionError(res)
            elif res.status_code == 404:
                if ignore_missing:
                    return False
                raise DocumentDeleteError(res)
            elif res.status_code not in HTTP_OK:
                raise DocumentDeleteError(res)
            if res.status_code == 202:
                res.body['sync'] = False
            else:
                res.body['sync'] = True
            return res.body

        return self.handle_request(request, handler)

    def delete_many(self,
                    documents,
                    return_old=False,
                    check_rev=False,
                    sync=None):
        """Delete multiple documents from the collection.

        :param documents: the list of documents or keys to delete
        :type documents: list
        :param return_old: if ``True``, the full bodies of the old documents
            are included in the returned result
        :type return_old: bool
        :param check_rev: if ``True``, the ``"_rev"`` field in **document**
            is compared against the revision of the target document
        :type check_rev: bool
        :param sync: wait for the operation to sync to disk
        :type sync: bool
        :returns: the result of the delete (e.g. document keys, revisions)
        :rtype: dict
        :raises arango.exceptions.DocumentDeleteError: if the documents cannot
            be deleted

        .. note::
            If an entry in **documents** is a dictionary it must have the
            ``"_key"`` field
        """
        params = {
            'returnOld': return_old,
            'ignoreRevs': not check_rev,
            'overwrite': not check_rev
        }
        if sync is not None:
            params['waitForSync'] = sync

        if self._conn.type != 'transaction':
            command = None
        else:
            command = 'db.{}.remove({},{})'.format(
                self._name,
                dumps(documents),
                dumps(params)
            )

        request = Request(
            method='delete',
            endpoint='/_api/document/{}'.format(self._name),
            params=params,
            data=documents,
            command=command
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentDeleteError(res)

            results = []
            for result in res.body:
                if '_id' not in result:
                    # An error occurred with this particular document
                    err = res.update_body(result)
                    # Single out revision errors
                    if result['errorNum'] == 1200:
                        result = DocumentRevisionError(err)
                    else:
                        result = DocumentDeleteError(err)
                else:
                    if res.status_code == 202:
                        result['sync'] = False
                    elif res.status_code:
                        result['sync'] = True
                results.append(result)

            return results

        return self.handle_request(request, handler)

    def delete_match(self, filters, limit=None, sync=None):
        """Delete matching documents from the collection.

        :param filters: the document filters
        :type filters: dict
        :param limit: the the max number of documents to delete
        :type limit: int
        :param sync: wait for the operation to sync to disk
        :type sync: bool
        :returns: the number of documents deleted
        :rtype: dict
        :raises arango.exceptions.DocumentDeleteError: if the documents
            cannot be deleted from the collection
        """
        data = {'collection': self._name, 'example': filters}
        if sync is not None:
            data['waitForSync'] = sync
        if limit is not None:
            data['limit'] = limit

        request = Request(
            method='put',
            endpoint='/_api/simple/remove-by-example',
            data=data,
            command='db.{}.removeByExample({}, {})'.format(
                self._name,
                dumps(filters),
                dumps(data)
            )
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentDeleteError(res)
            return res.body['deleted']

        return self.handle_request(request, handler)

    def import_bulk(self,
                    documents,
                    halt_on_error=None,
                    details=True,
                    from_prefix=None,
                    to_prefix=None,
                    overwrite=None,
                    on_duplicate=None,
                    sync=None):
        """Insert multiple documents into the collection.

        This is faster than :func:`arango.collections.Collection.insert_many`
        but does not return as much information. Any ``"_id"`` and ``"_rev"``
        fields in **documents** are ignored.

        :param documents: the list of the new documents to insert in bulk
        :type documents: list
        :param halt_on_error: halt the entire import on an error
            (default: ``True``)
        :type halt_on_error: bool
        :param details: if ``True``, the returned result will include an
            additional list of detailed error messages (default: ``True``)
        :type details: bool
        :param from_prefix: the string prefix to prepend to the ``"_from"``
            field of each edge document inserted. *This only works for edge
            collections.*
        :type from_prefix: str | unicode
        :param to_prefix: the string prefix to prepend to the ``"_to"`` field
            of each edge document inserted. *This only works for edge
            collections.*
        :type to_prefix: str | unicode
        :param overwrite: if ``True``, all existing documents in the collection
            are removed prior to the import. Indexes are still preserved.
        :type overwrite: bool
        :param on_duplicate: the action to take on unique key constraint
            violations. Possible values are:

            .. code-block:: none

                "error"   : do not import the new documents and count them as
                            errors (this is the default)

                "update"  : update the existing documents while preserving any
                            fields missing in the new ones

                "replace" : replace the existing documents with the new ones

                "ignore"  : do not import the new documents and count them as
                            ignored, as opposed to counting them as errors

        :type on_duplicate: str | unicode
        :param sync: wait for the operation to sync to disk
        :type sync: bool
        :returns: the result of the bulk import
        :rtype: dict
        :raises arango.exceptions.DocumentInsertError: if the documents cannot
            be inserted into the collection

        .. note::
            Parameters **from_prefix** and **to_prefix** only work for edge
            collections. When the prefix is prepended, it is followed by a
            ``"/"`` character. For example, prefix ``"foo"`` prepended to an
            edge document with ``"_from": "bar"`` will result in a new value
            ``"_from": "foo/bar"``.

        .. note::
            Parameter **on_duplicate** actions ``"update"``, ``"replace"``
            and ``"ignore"`` will work only when **documents** contain the
            ``"_key"`` fields.

        .. warning::
            Parameter **on_duplicate** actions  ``"update"`` and ``"replace"``
            may fail on secondary unique key constraint violations.
        """
        params = {
            'type': 'array',
            'collection': self._name,
            'complete': halt_on_error,
            'details': details,
        }
        if halt_on_error is not None:
            params['complete'] = halt_on_error
        if details is not None:
            params['details'] = details
        if from_prefix is not None:
            params['fromPrefix'] = from_prefix
        if to_prefix is not None:
            params['toPrefix'] = to_prefix
        if overwrite is not None:
            params['overwrite'] = overwrite
        if on_duplicate is not None:
            params['onDuplicate'] = on_duplicate
        if sync is not None:
            params['waitForSync'] = sync

        request = Request(
            method='post',
            endpoint='/_api/import',
            data=documents,
            params=params
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DocumentInsertError(res)
            return res.body

        return self.handle_request(request, handler)
