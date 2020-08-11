from __future__ import absolute_import, unicode_literals

from abc import ABCMeta, abstractmethod
from calendar import timegm
from datetime import datetime

import jwt
from six import string_types
from requests_toolbelt import MultipartEncoder

from arango.exceptions import (
    ServerConnectionError,
    JWTAuthError,
)
from arango.request import Request
from arango.response import Response

__all__ = [
    'Connection',
    'BasicConnection',
    'JWTConnection',
    'JWTSuperuserConnection'
]


class Connection(object):
    """Base connection to specific ArangoDB database.

    :param hosts: Host URL or list of URLs (coordinators in a cluster).
    :type hosts: [str]
    :param host_resolver: Host resolver (used for clusters).
    :type host_resolver: arango.resolver.HostResolver
    :param sessions: HTTP session objects per host.
    :type sessions: [requests.Session]
    :param db_name: Database name.
    :type db_name: str
    :param http_client: User-defined HTTP client.
    :type http_client: arango.http.HTTPClient
    """

    __metaclass__ = ABCMeta

    auth_required_header = 'WWW-Authenticate'

    def __init__(self,
                 hosts,
                 host_resolver,
                 sessions,
                 db_name,
                 http_client,
                 serializer,
                 deserializer):
        self._url_prefixes = ['{}/_db/{}'.format(h, db_name) for h in hosts]
        self._host_resolver = host_resolver
        self._sessions = sessions
        self._db_name = db_name
        self._http = http_client
        self._serializer = serializer
        self._deserializer = deserializer

    @property
    def db_name(self):
        """Return the database name.

        :returns: Database name.
        :rtype: str
        """
        return self._db_name

    def serialize(self, obj):
        """Serialize the object and return the string.

        :param obj: Object to serialize.
        :type obj: str | bool | int | list | dict
        :return: Serialized string.
        :rtype: str
        """
        return self._serializer(obj)

    def deserialize(self, string):
        """De-serialize the string and return the object.

        :param string: String to de-serialize.
        :type string: str
        :return: De-serialized object.
        :rtype: str | bool | int | list | dict
        """
        try:
            return self._deserializer(string)
        except (ValueError, TypeError):
            return string

    def prep_response(self, resp, deserialize=True):
        """Populate the response with details and return it.

        :param deserialize: Deserialize the response body.
        :type deserialize: bool
        :param resp: HTTP response.
        :type resp: arango.response.Response
        :return: HTTP response.
        :rtype: arango.response.Response
        """
        if deserialize:
            resp.body = self.deserialize(resp.raw_body)
            if isinstance(resp.body, dict):
                resp.error_code = resp.body.get('errorNum')
                resp.error_message = resp.body.get('errorMessage')
        else:
            resp.body = resp.raw_body

        http_ok = 200 <= resp.status_code < 300
        resp.is_success = http_ok and resp.error_code is None
        return resp

    def prep_bulk_err_response(self, parent_response, body):
        """Build and return a bulk error response.

        :param parent_response: Parent response.
        :type parent_response: arango.response.Response
        :param body: Error response body.
        :type body: dict
        :return: Child bulk error response.
        :rtype: arango.response.Response
        """
        resp = Response(
            method=parent_response.method,
            url=parent_response.url,
            headers=parent_response.headers,
            status_code=parent_response.status_code,
            status_text=parent_response.status_text,
            raw_body=self.serialize(body),
        )
        resp.body = body
        resp.error_code = body['errorNum']
        resp.error_message = body['errorMessage']
        resp.is_success = False
        return resp

    def get_normalized_data(self, request):
        """Normalize request data.

        :param request: HTTP request.
        :type request: arango.request.Request
        :return: Normalized data.
        :rtype: str | bool | int | list | dict
        """
        if request.data is None:
            return request.data
        elif isinstance(request.data, (string_types, MultipartEncoder)):
            return request.data
        else:
            return self.serialize(request.data)

    def ping(self):
        """Ping the next host to check if connection is established.

        :return: Response status code.
        :rtype: int
        """
        request = Request(
            method='get',
            endpoint='/_api/collection'
        )
        resp = self.send_request(request)
        if resp.status_code in {401, 403}:
            raise ServerConnectionError('bad username and/or password')
        if not resp.is_success:  # pragma: no cover
            raise ServerConnectionError(
                resp.error_message or 'bad server response')
        return resp.status_code

    @abstractmethod
    def send_request(self, request):  # pragma: no cover
        """Send an HTTP request to ArangoDB server.

        :param request: HTTP request.
        :type request: arango.request.Request
        :return: HTTP response.
        :rtype: arango.response.Response
        """
        raise NotImplementedError


class BasicConnection(Connection):
    """Connection to specific ArangoDB database using basic authentication.

    :param hosts: Host URL or list of URLs (coordinators in a cluster).
    :type hosts: [str]
    :param host_resolver: Host resolver (used for clusters).
    :type host_resolver: arango.resolver.HostResolver
    :param sessions: HTTP session objects per host.
    :type sessions: [requests.Session]
    :param db_name: Database name.
    :type db_name: str
    :param username: Username.
    :type username: str
    :param password: Password.
    :type password: str
    :param http_client: User-defined HTTP client.
    :type http_client: arango.http.HTTPClient
    """

    def __init__(self,
                 hosts,
                 host_resolver,
                 sessions,
                 db_name,
                 username,
                 password,
                 http_client,
                 serializer,
                 deserializer):
        super(BasicConnection, self).__init__(
            hosts,
            host_resolver,
            sessions,
            db_name,
            http_client,
            serializer,
            deserializer
        )
        self._username = username
        self._auth = (username, password)

    @property
    def username(self):
        """Return the username.

        :returns: Username.
        :rtype: str
        """
        return self._username

    def send_request(self, request):
        """Send an HTTP request to ArangoDB server.

        :param request: HTTP request.
        :type request: arango.request.Request
        :return: HTTP response.
        :rtype: arango.response.Response
        """
        host_index = self._host_resolver.get_host_index()
        resp = self._http.send_request(
            session=self._sessions[host_index],
            method=request.method,
            url=self._url_prefixes[host_index] + request.endpoint,
            params=request.params,
            data=self.get_normalized_data(request),
            headers=request.headers,
            auth=self._auth
        )
        return self.prep_response(resp, request.deserialize)


class JWTConnection(Connection):
    """Connection to specific ArangoDB database using JWT authentication.

    :param hosts: Host URL or list of URLs (coordinators in a cluster).
    :type hosts: [str]
    :param host_resolver: Host resolver (used for clusters).
    :type host_resolver: arango.resolver.HostResolver
    :param sessions: HTTP session objects per host.
    :type sessions: [requests.Session]
    :param db_name: Database name.
    :type db_name: str
    :param username: Username.
    :type username: str
    :param password: Password.
    :type password: str
    :param http_client: User-defined HTTP client.
    :type http_client: arango.http.HTTPClient
    """

    def __init__(self,
                 hosts,
                 host_resolver,
                 sessions,
                 db_name,
                 username,
                 password,
                 http_client,
                 serializer,
                 deserializer):
        super(JWTConnection, self).__init__(
            hosts,
            host_resolver,
            sessions,
            db_name,
            http_client,
            serializer,
            deserializer
        )
        self._username = username
        self._password = password
        self.exp_leeway = 0

        self._auth_header = None
        self._token = None
        self._token_exp = None
        self.refresh_token()

    def send_request(self, request):
        """Send an HTTP request to ArangoDB server.

        :param request: HTTP request.
        :type request: arango.request.Request
        :return: HTTP response.
        :rtype: arango.response.Response
        """
        host_index = self._host_resolver.get_host_index()
        request.headers['Authorization'] = self._auth_header

        resp = self._http.send_request(
            session=self._sessions[host_index],
            method=request.method,
            url=self._url_prefixes[host_index] + request.endpoint,
            params=request.params,
            data=self.get_normalized_data(request),
            headers=request.headers,
        )
        resp = self.prep_response(resp, request.deserialize)

        # Refresh the token and retry on HTTP 401 and error code 11.
        if resp.error_code != 11 or resp.status_code != 401:
            return resp

        now = timegm(datetime.utcnow().utctimetuple())
        if self._token_exp < now - self.exp_leeway:  # pragma: no cover
            return resp

        self.refresh_token()
        request.headers['Authorization'] = self._auth_header

        resp = self._http.send_request(
            session=self._sessions[host_index],
            method=request.method,
            url=self._url_prefixes[host_index] + request.endpoint,
            params=request.params,
            data=self.get_normalized_data(request),
            headers=request.headers,
        )
        return self.prep_response(resp, request.deserialize)

    def refresh_token(self):
        """Get a new JWT token for the current user (cannot be a superuser).

        :return: JWT token.
        :rtype: str
        """
        request = Request(
            method='post',
            endpoint='/_open/auth',
            data={
                'username': self._username,
                'password': self._password
            }
        )
        host_index = self._host_resolver.get_host_index()
        resp = self._http.send_request(
            session=self._sessions[host_index],
            method=request.method,
            url=self._url_prefixes[host_index] + request.endpoint,
            data=self.get_normalized_data(request)
        )
        resp = self.prep_response(resp)
        if not resp.is_success:
            raise JWTAuthError(resp, request)

        self._token = resp.body['jwt']
        jwt_payload = jwt.decode(
            self._token,
            issuer='arangodb',
            algorithms=['HS256'],
            options={
                'require_exp': True,
                'require_iat': True,
                'verify_iat': True,
                'verify_exp': True,
                'verify_signature': False
            },
        )
        self._token_exp = jwt_payload['exp']
        self._auth_header = 'bearer {}'.format(self._token)


class JWTSuperuserConnection(Connection):
    """Connection to specific ArangoDB database using superuser JWT.

    :param hosts: Host URL or list of URLs (coordinators in a cluster).
    :type hosts: [str]
    :param host_resolver: Host resolver (used for clusters).
    :type host_resolver: arango.resolver.HostResolver
    :param sessions: HTTP session objects per host.
    :type sessions: [requests.Session]
    :param db_name: Database name.
    :type db_name: str
    :param http_client: User-defined HTTP client.
    :type http_client: arango.http.HTTPClient
    :param superuser_token: User generated token for superuser access.
    :type superuser_token: str
    """

    def __init__(self,
                 hosts,
                 host_resolver,
                 sessions,
                 db_name,
                 http_client,
                 serializer,
                 deserializer,
                 superuser_token):
        super(JWTSuperuserConnection, self).__init__(
            hosts,
            host_resolver,
            sessions,
            db_name,
            http_client,
            serializer,
            deserializer
        )
        self._auth_header = 'bearer {}'.format(superuser_token)

    def send_request(self, request):
        """Send an HTTP request to ArangoDB server.

        :param request: HTTP request.
        :type request: arango.request.Request
        :return: HTTP response.
        :rtype: arango.response.Response
        """
        host_index = self._host_resolver.get_host_index()
        request.headers['Authorization'] = self._auth_header

        resp = self._http.send_request(
            session=self._sessions[host_index],
            method=request.method,
            url=self._url_prefixes[host_index] + request.endpoint,
            params=request.params,
            data=self.get_normalized_data(request),
            headers=request.headers,
        )
        return self.prep_response(resp, request.deserialize)
