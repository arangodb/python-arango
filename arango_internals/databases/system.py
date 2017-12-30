from __future__ import absolute_import, unicode_literals

from arango_internals import Request
from arango_internals.utils import HTTP_OK
from arango_internals.databases import BaseDatabase
from arango_internals.exceptions import (
    DatabaseCreateError,
    DatabaseDeleteError,
    ServerEndpointsError
)


class SystemDatabase(BaseDatabase):
    """ArangoDB System Database.  Every call made using this database must
    use root access.
    """

    def __init__(self,
                 connection):

        if connection.database != "_system":
            raise ValueError("SystemDatabase must recieve a connection to "
                             "the _system database.")

        super(SystemDatabase, self).__init__(connection)

    def endpoints(self):
        """Return the list of the endpoints the server is listening on.

        Each endpoint is mapped to a list of databases. If the list is empty,
        it means all databases can be accessed via the endpoint. If the list
        contains more than one database, the first database receives all the
        requests by default, unless the name is explicitly specified.

        :returns: the list of endpoints
        :rtype: list
        :raises arango.exceptions.ServerEndpointsError: if the endpoints
            cannot be retrieved from the server
        """

        request = Request(
            method="get",
            url="/_api/endpoint"
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise ServerEndpointsError(res)
            return res.body

        return self.handle_request(request, handler)

    def create_database(self, name, users=None, username=None, password=None):
        """Create a new database.

        :param name: the name of the new database
        :type name: str | unicode
        :param users: the list of users with access to the new database, where
            each user is a dictionary with keys ``"username"``, ``"password"``,
            ``"active"`` and ``"extra"``.
        :type users: [dict]
        :param username: the username for authentication (if set, overrides
            the username specified during the client initialization)
        :type username: str | unicode
        :param password: the password for authentication (if set, overrides
            the password specified during the client initialization
        :type password: str | unicode
        :returns: the database object
        :rtype: arango.database.Database
        :raises arango.exceptions.DatabaseCreateError: if the create fails

        .. note::
            Here is an example entry in **users**:

            .. code-block:: python

                {
                    'username': 'john',
                    'password': 'password',
                    'active': True,
                    'extra': {'Department': 'IT'}
                }

            If **users** is not set, only the root and the current user are
            granted access to the new database by default.
        """

        data = {
            'name': name,
        }

        if users is not None:
            data['users'] = [{
                'username': user['username'],
                'passwd': user['password'],
                'active': user.get('active', True),
                'extra': user.get('extra', {})
            } for user in users]

        request = Request(
            method="post",
            url="/_api/database",
            data=data
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise DatabaseCreateError(res)
            return self.db(name, username, password)

        return self.handle_request(request, handler)

    def delete_database(self, name, ignore_missing=False):
        """Delete the database of the specified name.

        :param name: the name of the database to delete
        :type name: str | unicode
        :param ignore_missing: ignore missing databases
        :type ignore_missing: bool
        :returns: whether the database was deleted successfully
        :rtype: bool
        :raises arango.exceptions.DatabaseDeleteError: if the delete fails

        .. note::
            Root privileges (i.e. access to the ``_system`` database) are
            required to use this method.
        """

        request = Request(
            method="delete",
            url='/_api/database/{}'.format(name)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                if not (res.status_code == 404 and ignore_missing):
                    raise DatabaseDeleteError(res)
            return not res.body['error']

        return self.handle_request(request, handler)
