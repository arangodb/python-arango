"""ArangoDB's Top-Level API."""

from datetime import datetime


from arango.database import Database
from arango.connection import Connection
from arango.exceptions import *
from arango.constants import HTTP_OK, LOG_LEVELS, DEFAULT_DATABASE
from arango.clients import DefaultHTTPClient
from arango.utils import uncamelify, unicode_to_str


class Arango(object):
    """Driver for ArangoDB's top-level APIs:

    1. Database Management
    2. User Management
    3. Administration & Monitoring
    4. Miscellaneous Functions
    """

    def __init__(self, protocol='http', host='localhost', port=8529,
                 username='root', password='', client=None, check_conn=False):
        """Initialize the API driver.

        :param protocol: the internet transfer protocol (default: 'http')
        :type protocol: str
        :param host: ArangoDB host (default: 'localhost')
        :type host: str
        :param port: ArangoDB port (default: 8529)
        :type port: int
        :param username: ArangoDB username (default: 'root')
        :type username: str
        :param password: ArangoDB password (default: '')
        :type password: str
        :param client: the HTTP client to use under the hood
        :type client: arango.clients.base.BaseHTTPClient or None
        :param check_conn: check the connection during instantiation
        :type check_conn: bool
        :raises: arango.exceptions.ConnectionError
        """
        self._protocol = protocol
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._client = client if client else DefaultHTTPClient()

        # Initialize the ArangoDB API connection object
        self._conn = Connection(
            protocol=self._protocol,
            host=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            client=self._client,
        )
        if check_conn:
            # Check the connection by requesting a header
            res = self._conn.head('/_api/version')
            if res.status_code not in HTTP_OK:
                raise ServerConnectionError(res)

        # Initialize the wrapper for the default database
        self._default_database = Database(self._conn, DEFAULT_DATABASE)

    def __repr__(self):
        """Return a descriptive string of this instance."""
        return "<ArangoDB API driver pointing to '{}'>".format(self._host)

    def __getattr__(self, attr):
        """Call __getattr__ of the default database."""
        return getattr(self._default_database, attr)

    def __getitem__(self, item):
        """Call __getitem__ of the default database."""
        return self._default_database.collection(item)

    ###########################
    # Miscellaneous Functions #
    ###########################

    def version(self):
        """Return the version of the ArangoDB server.

        :returns: the server version
        :rtype: str
        :raises: VersionGetError
        """
        res = self._conn.get(
            endpoint='/_api/version',
            params={'details': False}
        )
        if res.status_code not in HTTP_OK:
            raise VersionGetError(res)
        return str(res.body['version'])

    def details(self):
        """Return the details of the ArangoDB server.

        :returns: the server details
        :rtype: dict
        :raises: VersionGetError
        """
        res = self._conn.get(
            endpoint='/_api/version',
            params={'details': True}
        )
        if res.status_code not in HTTP_OK:
            raise VersionGetError(res)
        details = res.body['details']
        return {
            'architecture': str(details['architecture']),
            'build_date': datetime.strptime(
                details['build-date'], "%Y-%m-%d %H:%M:%S"
            ),
            'configure': str(details['configure']),
            'env': str(details['env']),
            'fd_client_event_handler': str(details['fd-client-event-handler']),
            'fd_set_size': int(details['fd-setsize']),
            'icu_version': str(details['icu-version']),
            'libev_version': str(details['libev-version']),
            'maintainer_mode': details['maintainer-mode'] != 'false',
            'mode': str(details['mode']),
            'openssl_version': str(details['openssl-version']),
            'server_version': str(details['server-version']),
            'size_of_int': int(details['sizeof int']),
            'size_of_void*': int(details['sizeof void*']),
            'tcmalloc': details['tcmalloc'] != 'false',
            'v8_version': str(details['v8-version'])
        }

    def required_db_version(self):
        """Return the required database version.

        :returns: the required database version
        :rtype: str
        :raises: RequiredDatabaseVersionGetError
        """
        res = self._conn.get('/_admin/database/target-version')
        if res.status_code not in HTTP_OK:
            raise RequiredDatabaseVersionGetError(res)
        return str(res.body['version'])

    def time(self):
        """Return the current system time.

        :returns: the system time
        :rtype: datetime.datetime
        :raises: TimeGetError
        """
        res = self._conn.get('/_admin/time')
        if res.status_code not in HTTP_OK:
            raise TimeGetError(res)
        return datetime.fromtimestamp(res.body['time'])

    def wal(self):
        """Return the configuration of the write-ahead log.

        :returns: the configuration of the write-ahead log
        :rtype: dict
        :raises: WriteAheadLogGetError
        """
        res = self._conn.get('/_admin/wal/properties')
        if res.status_code not in HTTP_OK:
            raise WriteAheadLogGetError(res)
        return {
            'oversized_ops': res.body.get('allowOversizeEntries'),
            'log_size': res.body.get('logfileSize'),
            'historic_logs': res.body.get('historicLogfiles'),
            'reserve_logs': res.body.get('reserveLogfiles'),
            'sync_interval': res.body.get('syncInterval'),
            'throttle_wait': res.body.get('throttleWait'),
            'throttle_limit': res.body.get('throttleWhenPending')
        }

    def flush_wal(self, wait_for_sync=True, wait_for_gc=True):
        """Flush the write-ahead log to collection journals and data files.

        :param wait_for_sync: block until data is synced to disk
        :type wait_for_sync: bool
        :param wait_for_gc: block until flushed data is garbage collected
        :type wait_for_gc: bool
        :raises: WriteAheadLogFlushError
        """
        res = self._conn.put(
            '/_admin/wal/flush',
            data={
                'waitForSync': wait_for_sync,
                'waitForCollector': wait_for_gc
            }
        )
        if res.status_code not in HTTP_OK:
            raise WriteAheadLogFlushError(res)

    def configure_wal(self, oversized_ops=None, log_size=None,
                      historic_logs=None, reserve_logs=None,
                      throttle_wait=None, throttle_limit=None):
        """Configure the parameters of the write-ahead log.

        When ``throttle_when_pending`` is set to 0, write-throttling will not
        be triggered at all.

        :param oversized_ops: execute and store ops bigger than a log file
        :type oversized_ops: bool or None
        :param log_size: the size of each write-ahead log file
        :type log_size: int or None
        :param historic_logs: the number of historic log files to keep
        :type historic_logs: int or None
        :param reserve_logs: the number of reserve log files to allocate
        :type reserve_logs: int or None
        :param throttle_wait: wait time before aborting when throttled (in ms)
        :type throttle_wait: int or None
        :param throttle_limit: number of pending gc ops before write-throttling
        :type throttle_limit: int or None
        :returns: the new configuration of the write-ahead log
        :rtype: dict
        :raises: Write
        """
        data = dict()
        if oversized_ops is not None:
            data['allowOversizeEntries'] = oversized_ops
        if log_size is not None:
            data['logfileSize'] = log_size
        if historic_logs is not None:
            data['historicLogfiles'] = historic_logs
        if reserve_logs is not None:
            data['reserveLogfiles'] = reserve_logs
        if throttle_wait is not None:
            data['throttleWait'] = throttle_wait
        if throttle_limit is not None:
            data['throttleWhenPending'] = throttle_limit
        res = self._conn.put('/_admin/wal/properties', data=data)
        if res.status_code not in HTTP_OK:
            raise WriteAheadLogGetError(res)
        return {
            'oversized_ops': res.body.get('allowOversizeEntries'),
            'log_size': res.body.get('logfileSize'),
            'historic_logs': res.body.get('historicLogfiles'),
            'reserve_logs': res.body.get('reserveLogfiles'),
            'sync_interval': res.body.get('syncInterval'),
            'throttle_wait': res.body.get('throttleWait'),
            'throttle_limit': res.body.get('throttleWhenPending')
        }

    def echo(self):
        """Return information on the last request (headers, payload etc.)

        :returns: the information on the last request
        :rtype: dict
        :raises: EchoError
        """
        res = self._conn.get('/_admin/echo')
        if res.status_code not in HTTP_OK:
            raise EchoError(res)
        return {
            'headers': unicode_to_str(res.body['headers']),
            'request_type': str(res.body['requestType']),
            'parameters': unicode_to_str(res.body['parameters'])
        }

    def sleep(self, seconds):
        """Suspend the execution for a specified duration before returning.

        :param seconds: the amount of seconds to wait until the reply is sent
        :raises: SleepError
        """
        res = self._conn.get(
            '/_admin/sleep',
            params={'duration': seconds}
        )
        if res.status_code not in HTTP_OK:
            raise SleepError(res)
        return res.body.get('duration')

    def shutdown(self):
        """Initiate the server shutdown sequence.

        :raises: ShutdownError
        """
        res = self._conn.get('/_admin/shutdown')
        if res.status_code not in HTTP_OK:
            raise ShutdownError(res)

    def test(self, tests):
        """Run the available unittests on the server.

        :param tests: list of files containing the test suites
        :type tests: list
        :returns: the passed result
        :rtype: dict
        :raises: TestsRunError
        """
        res = self._conn.post('/_admin/test', data={'tests': tests})
        if res.status_code not in HTTP_OK:
            raise TestsRunError(res)
        return res.body.get('passed')

    def run_javascript(self, javascript):
        """Execute a javascript program on the server.

        :param javascript: the body of the javascript program to execute.
        :type javascript: str
        :returns: the result of the execution
        :rtype: str
        :raises: ProgramExecuteError
        """
        res = self._conn.post(
            '/_admin/execute',
            data=javascript
        )
        if res.status_code not in HTTP_OK:
            raise ProgramExecuteError(res)
        return res.body

    #######################
    # Database Management #
    #######################

    def list_databases(self, user_only=False):
        """"Return the database names.

        :param user_only: return only the user database names
        :type user_only: bool
        :returns: the database names
        :rtype: dict
        :raises: DatabaseListError
        """
        # Get the current user's databases
        res = self._conn.get(
            '/_api/database/user' if user_only else '/_api/database'
        )
        if res.status_code not in HTTP_OK:
            raise DatabaseListError(res)
        return res.body['result']

    def db(self, name):
        """Return the database object of the specified name.

        :param name: the name of the database
        :type name: str
        :returns: the database object
        :rtype: arango.database.Database
        """
        return self.database(name)

    def database(self, name):
        """Return the database object of the specified name.

        :param name: the name of the database
        :type name: str
        :returns: the database object
        :rtype: arango.database.Database
        """
        return Database(
            name=name,
            connection=Connection(
                protocol=self._protocol,
                host=self._host,
                port=self._port,
                username=self._username,
                password=self._password,
                database=name,
                client=self._client
            )
        )

    def create_database(self, name, users=None):
        """Create a new database.

        :param name: the name of the new database
        :type name: str
        :param users: the users configuration
        :type users: dict
        :returns: the Database object
        :rtype: arango.database.Database
        :raises: DatabaseCreateError
        """
        res = self._conn.post(
            '/_api/database',
            data={'name': name, 'users': users} if users else {'name': name}
        )
        if res.status_code not in HTTP_OK:
            raise DatabaseCreateError(res)
        return self.database(name)

    def delete_database(self, name, safe_delete=False):
        """Delete the database of the specified name.

        :param name: the name of the database to delete
        :type name: str
        :param safe_delete: whether to execute a safe delete (ignore 404)
        :type safe_delete: bool
        :raises: DatabaseDeleteError
        """
        res = self._conn.delete('/_api/database/{}'.format(name))
        if res.status_code not in HTTP_OK:
            if not (res.status_code == 404 and safe_delete):
                raise DatabaseDeleteError(res)

    ###################
    # User Management #
    ###################

    def list_users(self):
        """Return details on all users.

        :returns: the mapping of usernames to user information
        :rtype: dict
        :raises: UserListError
        """
        res = self._conn.get('/_api/user')
        if res.status_code not in HTTP_OK:
            raise UserListError(res)
        return {
            record['user']: {
                'change_password': record.get('changePassword'),
                'active': record.get('active'),
                'extra': record.get('extra'),
            }
            for record in res.body['result']
        }

    def user(self, username):
        """Return the details on a single user.

        :param username: the username
        :type username: str
        :returns: user information
        :rtype: dict or None
        :raises: UserNotFoundError
        """
        res = self._conn.get('/_api/user')
        if res.status_code not in HTTP_OK:
            raise UserNotFoundError(username)
        for record in res.body['result']:
            if record['user'] == username:
                return {
                    'change_password': record.get('changePassword'),
                    'active': record.get('active'),
                    'extra': record.get('extra'),
                }
        raise UserNotFoundError(username)

    def create_user(self, username, password, active=None, extra=None,
                    change_password=None):
        """Create a new user.

        if ``change_password`` is set to true, the only operation allowed by
        the user will be ``self.replace_user`` or ``self.update_user``. All
        other operations executed by the user will result in an HTTP 403.

        :param username: the name of the user
        :type username: str
        :param password: the user password
        :type password: str
        :param active: whether the user is active
        :type active: bool or None
        :param extra: any extra data about the user
        :type extra: dict or None
        :param change_password: whether the user must change the password
        :type change_password: bool or None
        :returns: the information about the new user
        :rtype: dict
        :raises: UserCreateError
        """
        data = {'user': username, 'passwd': password}
        if active is not None:
            data['active'] = active
        if extra is not None:
            data['extra'] = extra
        if change_password is not None:
            data['changePassword'] = change_password

        res = self._conn.post('/_api/user', data=data)
        if res.status_code not in HTTP_OK:
            raise UserCreateError(res)
        return {
            'active': res.body.get('active'),
            'change_password': res.body.get('changePassword'),
            'extra': res.body.get('extra'),
        }

    def update_user(self, username, password=None, active=None, extra=None,
                    change_password=None):
        """Update an existing user.

        if ``change_password`` is set to true, the only operation allowed by
        the user will be ``self.replace_user`` or ``self.update_user``. All
        other operations executed by the user will result in an HTTP 403.

        :param username: the name of the existing user
        :type username: str
        :param password: the user password
        :type password: str
        :param active: whether the user is active
        :type active: bool or None
        :param extra: any extra data about the user
        :type extra: dict or None
        :param change_password: whether the user must change the password
        :type change_password: bool or None
        :returns: the information about the updated user
        :rtype: dict
        :raises: UserUpdateError
        """
        data = {}
        if password is not None:
            data['password'] = password
        if active is not None:
            data['active'] = active
        if extra is not None:
            data['extra'] = extra
        if change_password is not None:
            data['changePassword'] = change_password

        res = self._conn.patch(
            '/_api/user/{user}'.format(user=username), data=data
        )
        if res.status_code not in HTTP_OK:
            raise UserUpdateError(res)
        return {
            'active': res.body.get('active'),
            'change_password': res.body.get('changePassword'),
            'extra': res.body.get('extra'),
        }

    def replace_user(self, username, password, active=None, extra=None,
                     change_password=None):
        """Replace an existing user.

        if ``change_password`` is set to true, the only operation allowed by
        the user will be ``self.replace_user`` or ``self.update_user``. All
        other operations executed by the user will result in an HTTP 403.

        :param username: the name of the existing user
        :type username: str
        :param password: the user password
        :type password: str
        :param active: whether the user is active
        :type active: bool or None
        :param extra: any extra data about the user
        :type extra: dict or None
        :param change_password: whether the user must change the password
        :type change_password: bool or None
        :returns: the information about the replaced user
        :rtype: dict
        :raises: UserReplaceError
        """
        data = {'user': username, 'password': password}
        if active is not None:
            data['active'] = active
        if extra is not None:
            data['extra'] = extra
        if change_password is not None:
            data['changePassword'] = change_password

        res = self._conn.put(
            '/_api/user/{user}'.format(user=username), data=data
        )
        if res.status_code not in HTTP_OK:
            raise UserReplaceError(res)
        return {
            'active': res.body.get('active'),
            'change_password': res.body.get('changePassword'),
            'extra': res.body.get('extra'),
        }

    def delete_user(self, username, safe_delete=False):
        """Delete an existing user.

        :param username: the name of the user
        :type username: str
        :param safe_delete: ignores HTTP 404 if set to True
        :type safe_delete: bool
        :raises: UserDeleteError
        """
        res = self._conn.delete('/_api/user/{user}'.format(user=username))
        if res.status_code not in HTTP_OK:
            if not (res.status_code == 404 and safe_delete):
                raise UserDeleteError(res)

    ###############################
    # Administration & Monitoring #
    ###############################

    def read_log(self, upto=None, level=None, start=None, size=None,
                 offset=None, search=None, sort=None):
        """Read the global log from the server

        The parameters ``upto`` and ``level`` are mutually exclusive.
        The values for ``upto`` and ``level`` must be one of:

        'fatal' or 0
        'error' or 1
        'warning' or 2
        'info' or 3 (default)
        'debug' or 4

        The parameters ``offset`` and ``size`` can be used for pagination.
        The values for ``sort`` must be one of 'asc' or 'desc'.

        :param upto: return entries up to this level
        :type upto: str or int or None
        :param level: return entries of this level only
        :type level: str or int or None
        :param start: return entries whose id >= to the given value
        :type start: int or None
        :param size: restrict the result to the given value
        :type size: int or None
        :param offset: return entries skipping the given number
        :type offset: int or None
        :param search: return only the entires containing the given text
        :type search: str or None
        :param sort: sort the entries according to their lid values
        :type sort: str or None
        :returns: the server log
        :rtype: dict
        :raises: LogGetError
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
            LogGetError(res)
        return unicode_to_str(res.body)

    def reload_routing(self):
        """Reload the routing information from the collection ``routing``.

        :raises: RoutingInfoReloadError
        """
        res = self._conn.post('/_admin/routing/reload')
        if res.status_code not in HTTP_OK:
            raise RountingInfoReloadError(res)

    def statistics(self, description=False):
        """Return the server statistics.

        :param description: return the statistics description instead
        :type description: bool
        :returns: the statistics information
        :rtype: dict
        :raises: StatisticsGetError
        """
        if description:
            endpoint = '/_admin/statistics-description'
        else:
            endpoint = '/_admin/statistics'
        res = self._conn.get(endpoint)
        if res.status_code not in HTTP_OK:
            raise StatisticsGetError(res)
        res.body.pop('code', None)
        res.body.pop('error', None)
        return unicode_to_str(res.body)

    def role(self):
        """Return the role of the server in the cluster if applicable

        Possible return values are:

        COORDINATOR: the server is a coordinator in the cluster
        PRIMARY:     the server is a primary database in the cluster
        SECONDARY:   the server is a secondary database in the cluster
        UNDEFINED:   in a cluster, UNDEFINED is returned if the server role
                     cannot be determined. On a single server, UNDEFINED is
                     the only possible return value.

        :returns: the server role
        :rtype: str
        :raises: ServerRoleGetError
        """
        res = self._conn.get('/_admin/server/role')
        if res.status_code not in HTTP_OK:
            raise ServerRoleGetError(res)
        return str(res.body.get('role'))

if __name__ == '__main__':
    a = Arango()
    print(a.version())
