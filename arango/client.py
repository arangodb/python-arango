from __future__ import absolute_import, unicode_literals

from datetime import datetime

from requests import ConnectionError

from arango.http_clients import DefaultHTTPClient
from arango.connection import Connection
from arango.utils import HTTP_OK
from arango.database import Database
from arango.exceptions import *
from arango.wal import WriteAheadLog


class ArangoClient(object):
    """ArangoDB client.

    :param protocol: the internet transfer protocol (default: ``"http"``)
    :type protocol: str | unicode
    :param host: ArangoDB host (default: ``"localhost"``)
    :type host: str | unicode
    :param port: ArangoDB port (default: ``8529``)
    :type port: int or str
    :param username: ArangoDB username (default: ``"root"``)
    :type username: str | unicode
    :param password: ArangoDB password (default: ``""``)
    :param verify: check the connection during initialization
    :type verify: bool
    :param http_client: the HTTP client object
    :type http_client: arango.http_clients.base.BaseHTTPClient
    :param enable_logging: log all API requests
    :type enable_logging: bool
    :param check_cert: verify SSL certificate when making HTTP requests
    :type check_cert: bool
    :param use_session: use session when making HTTP requests
    :type use_session: bool
    """

    def __init__(self,
                 protocol='http',
                 host='127.0.0.1',
                 port=8529,
                 username='root',
                 password='',
                 verify=False,
                 http_client=None,
                 enable_logging=True,
                 check_cert=True,
                 use_session=True):

        self._protocol = protocol
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._http_client = DefaultHTTPClient(
            use_session=use_session,
            check_cert=check_cert
        ) if http_client is None else http_client
        self._logging = enable_logging
        self._conn = Connection(
            protocol=self._protocol,
            host=self._host,
            port=self._port,
            database='_system',
            username=self._username,
            password=self._password,
            http_client=self._http_client,
            enable_logging=self._logging
        )
        self._wal = WriteAheadLog(self._conn)

        if verify:
            self.verify()

    def __repr__(self):
        return '<ArangoDB client for "{}">'.format(self._host)

    def verify(self):
        """Verify the connection to ArangoDB server.

        :returns: ``True`` if the connection is successful
        :rtype: bool
        :raises arango.exceptions.ServerConnectionError: if the connection to
            the ArangoDB server fails
        """
        res = self._conn.head('/_api/version')
        if res.status_code not in HTTP_OK:
            raise ServerConnectionError(res)
        return True

    @property
    def protocol(self):
        """Return the internet transfer protocol.

        :returns: the internet transfer protocol
        :rtype: str | unicode
        """
        return self._protocol

    @property
    def host(self):
        """Return the ArangoDB host.

        :returns: the ArangoDB host
        :rtype: str | unicode
        """
        return self._host

    @property
    def port(self):
        """Return the ArangoDB port.

        :returns: the ArangoDB port
        :rtype: int
        """
        return self._port

    @property
    def username(self):
        """Return the ArangoDB username.

        :returns: the ArangoDB username
        :rtype: str | unicode
        """
        return self._username

    @property
    def password(self):
        """Return the ArangoDB user password.

        :returns: the ArangoDB user password
        :rtype: str | unicode
        """
        return self._password

    @property
    def http_client(self):
        """Return the HTTP client.

        :returns: the HTTP client
        :rtype: arango.http_clients.base.BaseHTTPClient
        """
        return self._http_client

    @property
    def logging_enabled(self):
        """Return True if logging is enabled, False otherwise.

        :returns: whether logging is enabled
        :rtype: bool
        """
        return self._logging

    @property
    def wal(self):
        """Return the write-ahead log object.

        :returns: the write-ahead log object
        :rtype: arango.wal.WriteAheadLog
        """
        return self._wal

    def version(self):
        """Return the version of the ArangoDB server.

        :returns: the server version
        :rtype: str | unicode
        :raises arango.exceptions.ServerVersionError: if the server version
            cannot be retrieved
        """
        res = self._conn.get(
            endpoint='/_api/version',
            params={'details': False}
        )
        if res.status_code not in HTTP_OK:
            raise ServerVersionError(res)
        return res.body['version']

    def details(self):
        """Return the component details on the ArangoDB server.

        :returns: the server details
        :rtype: dict
        :raises arango.exceptions.ServerDetailsError: if the server details
            cannot be retrieved
        """
        res = self._conn.get(
            endpoint='/_api/version',
            params={'details': True}
        )
        if res.status_code not in HTTP_OK:
            raise ServerDetailsError(res)
        return res.body['details']

    def required_db_version(self):
        """Return the required version of the target database.

        :returns: the required version of the target database
        :rtype: str | unicode
        :raises arango.exceptions.ServerRequiredDBVersionError: if the
            required database version cannot be retrieved
        """
        res = self._conn.get('/_admin/database/target-version')
        if res.status_code not in HTTP_OK:
            raise ServerRequiredDBVersionError(res)
        return res.body['version']

    def statistics(self, description=False):
        """Return the server statistics.

        :returns: the statistics information
        :rtype: dict
        :raises arango.exceptions.ServerStatisticsError: if the server
            statistics cannot be retrieved
        """
        res = self._conn.get(
            '/_admin/statistics-description'
            if description else '/_admin/statistics'
        )
        if res.status_code not in HTTP_OK:
            raise ServerStatisticsError(res)
        res.body.pop('code', None)
        res.body.pop('error', None)
        return res.body

    def role(self):
        """Return the role of the server in the cluster if any.

        :returns: the server role which can be ``"SINGLE"`` (the server is not
            in a cluster), ``"COORDINATOR"`` (the server is a coordinator in
            the cluster), ``"PRIMARY"`` (the server is a primary database in
            the cluster), ``"SECONDARY"`` (the server is a secondary database
            in the cluster) or ``"UNDEFINED"`` (the server role is undefined,
            the only possible value for a single server)
        :rtype: str | unicode
        :raises arango.exceptions.ServerRoleError: if the server role cannot
            be retrieved
        """
        res = self._conn.get('/_admin/server/role')
        if res.status_code not in HTTP_OK:
            raise ServerRoleError(res)
        return res.body.get('role')

    def time(self):
        """Return the current server system time.

        :returns: the server system time
        :rtype: datetime.datetime
        :raises arango.exceptions.ServerTimeError: if the server time
            cannot be retrieved
        """
        res = self._conn.get('/_admin/time')
        if res.status_code not in HTTP_OK:
            raise ServerTimeError(res)
        return datetime.fromtimestamp(res.body['time'])

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
        res = self._conn.get('/_api/endpoint')
        if res.status_code not in HTTP_OK:
            raise ServerEndpointsError(res)
        return res.body

    def echo(self):
        """Return information on the last request (headers, payload etc.)

        :returns: the details of the last request
        :rtype: dict
        :raises arango.exceptions.ServerEchoError: if the last request cannot
            be retrieved from the server
        """
        res = self._conn.get('/_admin/echo')
        if res.status_code not in HTTP_OK:
            raise ServerEchoError(res)
        return res.body

    def sleep(self, seconds):
        """Suspend the execution for a specified duration before returning.

        :param seconds: the number of seconds to suspend
        :type seconds: int
        :returns: the number of seconds suspended
        :rtype: int
        :raises arango.exceptions.ServerSleepError: if the server cannot be
            suspended
        """
        res = self._conn.get(
            '/_admin/sleep',
            params={'duration': seconds}
        )
        if res.status_code not in HTTP_OK:
            raise ServerSleepError(res)
        return res.body['duration']

    def shutdown(self):  # pragma: no cover
        """Initiate the server shutdown sequence.

        :returns: whether the server was shutdown successfully
        :rtype: bool
        :raises arango.exceptions.ServerShutdownError: if the server shutdown
            sequence cannot be initiated
        """
        try:
            res = self._conn.delete('/_admin/shutdown')
        except ConnectionError:
            return False
        if res.status_code not in HTTP_OK:
            raise ServerShutdownError(res)
        return True

    def run_tests(self, tests):  # pragma: no cover
        """Run the available unittests on the server.

        :param tests: list of files containing the test suites
        :type tests: list
        :returns: the test results
        :rtype: dict
        :raises arango.exceptions.ServerRunTestsError: if the test suites fail
        """
        res = self._conn.post('/_admin/test', data={'tests': tests})
        if res.status_code not in HTTP_OK:
            raise ServerRunTestsError(res)
        return res.body

    def execute(self, program):
        """Execute a Javascript program on the server.

        :param program: the body of the Javascript program to execute.
        :type program: str | unicode
        :returns: the result of the execution
        :rtype: str | unicode
        :raises arango.exceptions.ServerExecuteError: if the program cannot
            be executed on the server
        """
        res = self._conn.post('/_admin/execute', data=program)
        if res.status_code not in HTTP_OK:
            raise ServerExecuteError(res)
        return res.body

    def read_log(self,
                 upto=None,
                 level=None,
                 start=None,
                 size=None,
                 offset=None,
                 search=None,
                 sort=None):
        """Read the global log from the server.

        :param upto: return the log entries up to the given level (mutually
            exclusive with argument **level**), which must be ``"fatal"``,
            ``"error"``, ``"warning"``, ``"info"`` (default) or ``"debug"``
        :type upto: str | unicode | int
        :param level: return the log entries of only the given level (mutually
            exclusive with **upto**), which must be ``"fatal"``, ``"error"``,
            ``"warning"``, ``"info"`` (default) or ``"debug"``
        :type level: str | unicode | int
        :param start: return the log entries whose ID is greater or equal to
            the given value
        :type start: int
        :param size: restrict the size of the result to the given value (this
            setting can be used for pagination)
        :type size: int
        :param offset: the number of entries to skip initially (this setting
            can be setting can be used for pagination)
        :type offset: int
        :param search: return only the log entries containing the given text
        :type search: str | unicode
        :param sort: sort the log entries according to the given fashion, which
            can be ``"sort"`` or ``"desc"``
        :type sort: str | unicode
        :returns: the server log entries
        :rtype: dict
        :raises arango.exceptions.ServerReadLogError: if the server log entries
            cannot be read
        """
        params = dict()
        if upto is not None:
            params['upto'] = upto
        if level is not None:
            params['level'] = level
        if start is not None:
            params['start'] = start
        if size is not None:
            params['size'] = size
        if offset is not None:
            params['offset'] = offset
        if search is not None:
            params['search'] = search
        if sort is not None:
            params['sort'] = sort
        res = self._conn.get('/_admin/log')
        if res.status_code not in HTTP_OK:
            raise ServerReadLogError(res)
        if 'totalAmount' in res.body:
            res.body['total_amount'] = res.body.pop('totalAmount')
        return res.body

    def log_levels(self):
        """Return the current logging levels.

        .. note::
            This method is only compatible with ArangoDB version 3.1+ only.

        :return: the current logging levels
        :rtype: dict
        """
        res = self._conn.get('/_admin/log/level')
        if res.status_code not in HTTP_OK:
            raise ServerLogLevelError(res)
        return res.body

    def set_log_levels(self, **kwargs):
        """Set the logging levels.

        This method takes arbitrary keyword arguments where the keys are the
        logger names and the values are the logging levels. For example:

        .. code-block:: python

            arango.set_log_level(
                agency='DEBUG',
                collector='INFO',
                threads='WARNING'
            )

        .. note::
            Keys that are not valid logger names are simply ignored.

        .. note::
            This method is only compatible with ArangoDB version 3.1+ only.

        :return: the new logging levels
        :rtype: dict
        """
        res = self._conn.put('/_admin/log/level', data=kwargs)
        if res.status_code not in HTTP_OK:
            raise ServerLogLevelSetError(res)
        return res.body

    def reload_routing(self):
        """Reload the routing information from the collection *routing*.

        :returns: whether the routing was reloaded successfully
        :rtype: bool
        :raises arango.exceptions.ServerReloadRoutingError: if the routing
            cannot be reloaded
        """
        res = self._conn.post('/_admin/routing/reload')
        if res.status_code not in HTTP_OK:
            raise ServerReloadRoutingError(res)
        return not res.body['error']

    #######################
    # Database Management #
    #######################

    def databases(self, user_only=False):
        """"Return the database names.

        :param user_only: list only the databases accessible by the user
        :type user_only: bool
        :returns: the database names
        :rtype: list
        :raises arango.exceptions.DatabaseListError: if the retrieval fails
        """
        # Get the current user's databases
        res = self._conn.get(
            '/_api/database/user'
            if user_only else '/_api/database'
        )
        if res.status_code not in HTTP_OK:
            raise DatabaseListError(res)
        return res.body['result']

    def db(self, name, username=None, password=None):
        """Return the database object.

        This is an alias for :func:`~arango.client.ArangoClient.database`.

        :param name: the name of the database
        :type name: str | unicode
        :param username: the username for authentication (if set, overrides
            the username specified during the client initialization)
        :type username: str | unicode
        :param password: the password for authentication (if set, overrides
            the password specified during the client initialization
        :type password: str | unicode
        :returns: the database object
        :rtype: arango.database.Database
        """
        return self.database(name, username, password)

    def database(self, name, username=None, password=None):
        """Return the database object.

        :param name: the name of the database
        :type name: str | unicode
        :param username: the username for authentication (if set, overrides
            the username specified during the client initialization)
        :type username: str | unicode
        :param password: the password for authentication (if set, overrides
            the password specified during the client initialization
        :type password: str | unicode
        :returns: the database object
        :rtype: arango.database.Database
        """
        return Database(Connection(
            protocol=self._protocol,
            host=self._host,
            port=self._port,
            database=name,
            username=username or self._username,
            password=password or self._password,
            http_client=self._http_client,
            enable_logging=self._logging
        ))

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
        res = self._conn.post(
            '/_api/database',
            data={
                'name': name,
                'users': [{
                    'username': user['username'],
                    'passwd': user['password'],
                    'active': user.get('active', True),
                    'extra': user.get('extra', {})
                } for user in users]
            } if users else {'name': name}
        )
        if res.status_code not in HTTP_OK:
            raise DatabaseCreateError(res)
        return self.db(name, username, password)

    def delete_database(self, name, ignore_missing=False):
        """Delete the database of the specified name.

        :param name: the name of the database to delete
        :type name: str | unicode
        :param ignore_missing: ignore missing databases
        :type ignore_missing: bool
        :returns: whether the database was deleted successfully
        :rtype: bool
        :raises arango.exceptions.DatabaseDeleteError: if the delete fails
        """
        res = self._conn.delete('/_api/database/{}'.format(name))
        if res.status_code not in HTTP_OK:
            if not (res.status_code == 404 and ignore_missing):
                raise DatabaseDeleteError(res)
        return not res.body['error']

    ###################
    # User Management #
    ###################

    def users(self):
        """Return the details of all users.

        :returns: the details of all users
        :rtype: [dict]
        :raises arango.exceptions.UserListError: if the retrieval fails

        .. note::
            Root privileges (i.e. access to the ``_system`` database) are
            required to use this method.
        """
        res = self._conn.get('/_api/user')
        if res.status_code not in HTTP_OK:
            raise UserListError(res)
        return [{
            'username': record['user'],
            'active': record['active'],
            'extra': record['extra'],
        } for record in res.body['result']]

    def user(self, username):
        """Return the details of a user.

        :param username: the details of the user
        :type username: str | unicode
        :returns: the user details
        :rtype: dict
        :raises arango.exceptions.UserGetError: if the retrieval fails

        .. note::
            Root privileges (i.e. access to the ``_system`` database) are
            required to use this method.
        """
        res = self._conn.get('/_api/user/{}'.format(username))
        if res.status_code not in HTTP_OK:
            raise UserGetError(res)
        return {
            'username': res.body['user'],
            'active': res.body['active'],
            'extra': res.body['extra']
        }

    def create_user(self, username, password, active=None, extra=None):
        """Create a new user.

        :param username: the name of the user
        :type username: str | unicode
        :param password: the user's password
        :type password: str | unicode
        :param active: whether the user is active
        :type active: bool
        :param extra: any extra data on the user
        :type extra: dict
        :returns: the details of the new user
        :rtype: dict
        :raises arango.exceptions.UserCreateError: if the user create fails

        .. note::
            Root privileges (i.e. access to the ``_system`` database) are
            required to use this method.
        """
        data = {'user': username, 'passwd': password}
        if active is not None:
            data['active'] = active
        if extra is not None:
            data['extra'] = extra

        res = self._conn.post('/_api/user', data=data)
        if res.status_code not in HTTP_OK:
            raise UserCreateError(res)
        return {
            'username': res.body['user'],
            'active': res.body['active'],
            'extra': res.body['extra'],
        }

    def update_user(self, username, password=None, active=None, extra=None):
        """Update an existing user.

        :param username: the name of the existing user
        :type username: str | unicode
        :param password: the user's new password
        :type password: str | unicode
        :param active: whether the user is active
        :type active: bool
        :param extra: any extra data on the user
        :type extra: dict
        :returns: the details of the updated user
        :rtype: dict
        :raises arango.exceptions.UserUpdateError: if the user update fails

        .. note::
            Root privileges (i.e. access to the ``_system`` database) are
            required to use this method.
        """
        data = {}
        if password is not None:
            data['passwd'] = password
        if active is not None:
            data['active'] = active
        if extra is not None:
            data['extra'] = extra

        res = self._conn.patch(
            '/_api/user/{user}'.format(user=username),
            data=data
        )
        if res.status_code not in HTTP_OK:
            raise UserUpdateError(res)
        return {
            'username': res.body['user'],
            'active': res.body['active'],
            'extra': res.body['extra'],
        }

    def replace_user(self, username, password, active=None, extra=None):
        """Replace an existing user.

        :param username: the name of the existing user
        :type username: str | unicode
        :param password: the user's new password
        :type password: str | unicode
        :param active: whether the user is active
        :type active: bool
        :param extra: any extra data on the user
        :type extra: dict
        :returns: the details of the replaced user
        :rtype: dict
        :raises arango.exceptions.UserReplaceError: if the user replace fails

        .. note::
            Root privileges (i.e. access to the ``_system`` database) are
            required to use this method.
        """
        data = {'user': username, 'passwd': password}
        if active is not None:
            data['active'] = active
        if extra is not None:
            data['extra'] = extra

        res = self._conn.put(
            '/_api/user/{user}'.format(user=username), 
            data=data
        )
        if res.status_code not in HTTP_OK:
            raise UserReplaceError(res)
        return {
            'username': res.body['user'],
            'active': res.body['active'],
            'extra': res.body['extra'],
        }

    def delete_user(self, username, ignore_missing=False):
        """Delete an existing user.

        :param username: the name of the existing user
        :type username: str | unicode
        :param ignore_missing: ignore missing users
        :type ignore_missing: bool
        :returns: ``True`` if the operation was successful, ``False`` if the
            user was missing but **ignore_missing** was set to ``True``
        :rtype: bool
        :raises arango.exceptions.UserDeleteError: if the user delete fails

        .. note::
            Root privileges (i.e. access to the ``_system`` database) are
            required to use this method.
        """
        res = self._conn.delete('/_api/user/{user}'.format(user=username))
        if res.status_code in HTTP_OK:
            return True
        elif res.status_code == 404 and ignore_missing:
            return False
        raise UserDeleteError(res)

    def user_access(self, username):
        """Return the database access details of a user.

        :param username: the name of the user
        :type username: str | unicode
        :returns: the names of the databases the user can access
        :rtype: [str]
        :raises: arango.exceptions.UserAccessError: if the retrieval fails

        .. note::
            Root privileges (i.e. access to the ``_system`` database) are
            required to use this method.
        """
        res = self._conn.get('/_api/user/{}/database'.format(username))
        if res.status_code in HTTP_OK:
            return list(res.body['result'])
        raise UserAccessError(res)

    def grant_user_access(self, username, database):
        """Grant user access to a database.

        :param username: the name of the user
        :type username: str | unicode
        :param database: the name of the database
        :type database: str | unicode
        :returns: whether the operation was successful
        :rtype: bool
        :raises arango.exceptions.UserGrantAccessError: if the operation fails

        .. note::
            Root privileges (i.e. access to the ``_system`` database) are
            required to use this method.
        """
        res = self._conn.put(
            '/_api/user/{}/database/{}'.format(username, database),
            data={'grant': 'rw'}
        )
        if res.status_code in HTTP_OK:
            return True
        raise UserGrantAccessError(res)

    def revoke_user_access(self, username, database):
        """Revoke user access to a database.

        :param username: the name of the user
        :type username: str | unicode
        :param database: the name of the database
        :type database: str | unicode | unicode
        :returns: whether the operation was successful
        :rtype: bool
        :raises arango.exceptions.UserRevokeAccessError: if the operation fails

        .. note::
            Root privileges (i.e. access to the ``_system`` database) are
            required to use this method.
        """
        res = self._conn.put(
            '/_api/user/{}/database/{}'.format(username, database),
            data={'grant': 'none'}
        )
        if res.status_code in HTTP_OK:
            return True
        raise UserRevokeAccessError(res)

    ########################
    # Async Job Management #
    ########################

    def async_jobs(self, status, count=None):
        """Return the IDs of asynchronous jobs with the specified status.

        :param status: the job status (``"pending"`` or ``"done"``)
        :type status: str | unicode
        :param count: the maximum number of job IDs to return
        :type count: int
        :returns: the list of job IDs
        :rtype: [str]
        :raises arango.exceptions.AsyncJobListError: if the retrieval fails
        """
        res = self._conn.get(
            '/_api/job/{}'.format(status),
            params={} if count is None else {'count': count}
        )
        if res.status_code not in HTTP_OK:
            raise AsyncJobListError(res)
        return res.body

    def clear_async_jobs(self, threshold=None):
        """Delete asynchronous job results from the server.

        :param threshold: if specified, only the job results created prior to
            the threshold (a unix timestamp) are deleted, otherwise *all* job
            results are deleted
        :type threshold: int
        :returns: whether the deletion of results was successful
        :rtype: bool
        :raises arango.exceptions.AsyncJobClearError: if the operation fails

        .. note::
            Async jobs currently queued or running are not stopped.
        """
        if threshold is None:
            res = self._conn.delete('/_api/job/all')
        else:
            res = self._conn.delete(
                '/_api/job/expired',
                params={'stamp': threshold}
            )
        if res.status_code in HTTP_OK:
            return True
        raise AsyncJobClearError(res)
