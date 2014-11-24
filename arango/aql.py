"""ArangoDB AQL Functions."""

from arango.exceptions import (
    ArangoAQLFunctionListError,
    ArangoAQLFunctionCreateError,
    ArangoAQLFunctionDeleteError
)


class AQLMixin(object):
    """Mix-in class for handling AQL functions."""

    @property
    def aql_functions(self):
        res = self._get("/_api/aqlfunction")
        if res.status_code != 200:
            raise ArangoAQLFunctionListError(res)
        return res.obj

    def create_aql_function(self, name, code, **kwargs):
        data = {"name": name, "code": code}
        data.update(kwargs)
        res = self._post("/_api/aqlfunction", data=data)
        if res.status_code not in (200, 201):
            raise ArangoAQLFunctionCreateError(res)

    def delete_aql_function(self, name, **kwargs):
        res = self._delete("/_api/aqlfunction/{}".format(name), data=kwargs)
        if res.status_code != 200:
            raise ArangoAQLFunctionDeleteError(res)
