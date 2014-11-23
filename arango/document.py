"""ArangoDB Document."""

from arango.exceptions import *


class ArangoDocumentMixin(object):
    """ArangoDB document mix-in class for ArangoCollection"""


    def doc(self, key, include_system_keys=True):
        return self.document(key, include_system_keys)

    def document(self, key, include_system_keys=True):
        res = self._get("/_api/document/{}/{}".format(self.name, key))
        if res.status_code != 200:
            raise ArangoDocumentGetError(res)
        document = res.obj["document"]
        if include_system_keys:
            for system_key in ["_id", "_key", "_rev"]:
                document[system_key] = res.obj[system_key]
        return document

    def create(self, document, wait_for_sync=False):
        res = self._post(
            "/_api/document?collection={}".format(self.name),
            data={
                "document": document,
                "collection": self.name,
                "waitForSync": wait_for_sync,
            }
        )
        if res.status_code != 201 and res.status_code != 202:
            raise ArangoDocumentCreateError(res)
        return res.obj

    def replace(self, key, document):
        pass

    def patch(self, key, data):
        pass

    def batch_create(self, documents):
        pass

    def batch_replace(self, documents):
        pass