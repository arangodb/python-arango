"""ArangoDB Index."""


from arango.util import camelify
from arango.exceptions import *


class IndexMixin(object):

    index_types = ["cap", "hash", "skiplist", "geo", "fulltext"]

    @property
    def indexes(self):
        """List the indexes."""
        res = self._get("/_api/index?collection={}".format(self.name))
        if res.status_code != 200:
            raise ArangoIndexListError(res)
        return {
            index_id.split("/", 1)[1]: details for
            index_id, details in res.obj["identifiers"].items()
        }

    def create_index(self, index_type, **config):
        """Create the index."""
        if index_type not in self.index_types:
            raise ArangoIndexCreateError(
                "Unknown index type '{}'".format(index_type))
        config["type"] = index_type
        res = self._post("/_api/index?collection={}".format(self.name),
                         data={camelify(k): v for k, v in config.items()})
        if res.status_code != 200 and res.status_code != 201:
            raise ArangoIndexCreateError(res)

    def delete_index(self, index_id):
        """Delete an index from this collection."""
        res = self._delete("/_api/index/{}".format(index_id))
        if res.status_code != 200:
            raise ArangoIndexDeleteError(res)
