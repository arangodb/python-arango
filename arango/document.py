"""ArangoDB Document."""

from arango.exceptions import (
    ArangoDocumentGetError,
    ArangoDocumentCreateError,
    ArangoDocumentDeleteError,
    ArangoDocumentPatchError,
    ArangoDocumentInvalidError,
)


class DocumentMixin(object):
    """Mix-in for ArangoDB document endpoints.

    This class is used by :class:`arango.collection.Collection`.
    """

    def __getitem__(self, key):
        """Return the document from this collection.

        :param key: the document key.
        :type key: str.
        :returns: dict -- the requested document.
        :raises: TypeError.
        """
        if not isinstance(key, str):
            raise TypeError("Expecting a str.")
        return self.get(key)

    def __setitem(self, key, doc):
        """Write the document into this collection.

        :param key: the document key.
        :type key: str.
        """


    def get(self, key, rev=None, match=True):
        """Return the document of the given key.

        :param key: the document key.
        :type key: str.
        :param rev: the document revision to check against (optional).
        :type rev: str.
        :param match: if True ``rev`` must match, else ``rev`` must differ.
        :type match: bool.
        :returns: dict -- the requested document.
        :raises: ArangoDocumentGetError.
        """
        headers = {"If-Match" if match else "If-None-Match": rev} if rev else {}
        res = self._get(
            "/_api/document/{}/{}".format(self.name, key),
            headers=headers
        )
        if res.status_code != 200:
            raise ArangoDocumentGetError(res)
        return res.obj

    def create(self, doc, wait_for_sync=False):
        """Create the given document in this collection.

        :param doc: the document to create in this collection.
        :type doc: dict.
        :param wait_for_sync: block until the document is synced to disk.
        :type wait_for_sync: bool.
        :raises: ArangoDocumentCreateError.
        """
        res = self._post(
            "/_api/document".format(self.name),
            data=doc,
            params = {
                "collection": self.name,
                "waitForSync": wait_for_sync,
            }
        )
        if res.status_code != 201 and res.status_code != 202:
            raise ArangoDocumentCreateError(res)
        return filter_keys(res.obj, ["error"])

    def replace(self, doc, ignore_rev=True, wait_for_sync=False):
        """Replace the document in this collection.

        :param doc: the new document to replace the one in this collection.
        :type doc: dict.
        :param ignore_rev: ignore the revision of the document ("_rev") if present.
        :type ignore_rev: bool.
        :param wait_for_sync: block until the document is synced to disk.
        :type wait_for_sync: bool.
        :raises: ArangoDocumentReplaceError.
        """
        if "_key" not in doc:
            raise ArangoDocumentInvalidError("'_key' missing")
        res = self._put(
            "/_api/document/{}/{}".format(self.name, doc["_key"]),
            data=doc,
            params={
                "waitForSync": wait_for_sync,
                "rev": doc.get("_rev"),
                "policy": "last" if ignore_rev else "error",
            }
        )
        if res.status_code != 201 and res.status_code != 202:
            raise ArangoDocumentReplaceError(res)
        return filter_keys(res.obj, ["error"])

    def patch(self, doc, ignore_rev=True, keep_none=True,
              wait_for_sync=False):
        if "_key" not in doc:
            raise ArangoDocumentInvalidError("'_key' missing")
        res = self._patch(
            "/_api/document/{}/{}".format(self.name, doc["_key"]),
            data=doc,
            params={
                "waitForSync": wait_for_sync,
                "rev": doc.get("_rev"),
                "policy": "last" if ignore_rev else "error",
                "keepNull": keep_none,
            }
        )
        if res.status_code != 201 and res.status_code != 202:
            raise ArangoDocumentPatchError(res)
        return filter_keys(res.obj, ["error"])

    def delete(self, key, ignore_rev=True, wait_for_sync=False):
        res = self._delete(
            "/_api/document/{}/{}".format(self.name, key),
            params={
                "waitForSync": wait_for_sync,
                "rev": doc.get("_rev"),
                "policy": "last" if ignore_rev else "error",
            }
        )
        if res.status_code != 200 and res.status_code != 202:
            raise ArangoDocumentReplaceError(res)
        return filter_keys(res.obj, ["error"])
